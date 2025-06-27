import face_recognition
import numpy as np
from PIL import Image
import io
from db import employees_col

def get_face_encodings(image_file):
    """Returns a list of encodings from a given image file (for multiple faces)."""
    image = face_recognition.load_image_file(image_file)
    encodings = face_recognition.face_encodings(image)
    return encodings  # could be empty


def recognize_faces_from_image(image_file, organization, tolerance=0.4):
    # Read and convert image
    if isinstance(image_file, bytes):
        image_data = image_file
    else:
        image_data = image_file.read()

    pil_image = Image.open(io.BytesIO(image_data)).convert("RGB")
    image_np = np.array(pil_image)

    # Detect all face encodings in uploaded image
    unknown_encodings = face_recognition.face_encodings(image_np)
    if not unknown_encodings:
        return []

    # Load all known encodings for this organization
    known_employees = list(employees_col.find({"organization": organization}))
    
    recognized_names = []

    for unknown_encoding in unknown_encodings:
        for emp in known_employees:
            emp_name = emp["employee_name"]
            emp_encodings = emp.get("face_encodings", [])
            
            # Fallback for old entries (single encoding)
            if "face_encoding" in emp:
                emp_encodings.append(emp["face_encoding"])

            for known_encoding in emp_encodings:
                known_encoding_np = np.array(known_encoding)
                match = face_recognition.compare_faces([known_encoding_np], unknown_encoding, tolerance=tolerance)[0]
                if match:
                    recognized_names.append(emp_name)
                    break  # stop after first match for that person

    return list(set(recognized_names))  # remove duplicates

