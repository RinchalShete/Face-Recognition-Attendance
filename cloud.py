import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os
import uuid  # for unique image naming

# Load .env credentials
load_dotenv()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUD_NAME"),
    api_key=os.getenv("CLOUD_API_KEY"),
    api_secret=os.getenv("CLOUD_API_SECRET")
)

def upload_image_to_cloudinary(image_file, employee_name):
    try:
        # Use UUID to make filename unique
        unique_id = str(uuid.uuid4())[:8]  # short unique suffix
        public_id = f"{employee_name}_{unique_id}"

        result = cloudinary.uploader.upload(
            image_file,
            folder="fra_employees",  # Optional folder in Cloudinary
            public_id=public_id,
            overwrite=False,  # Don't overwrite!
            resource_type="image"
        )
        return result.get("secure_url")
    except Exception as e:
        print(f"[Cloudinary Upload Error]: {e}")
        return None

def upload_multiple_images_to_cloudinary(images_dict, employee_name):
    """
    Uploads multiple labeled face images for an employee.
    
    Parameters:
    - images_dict: dict like { "front": image_file, "left": image_file, ... }
    - employee_name: str

    Returns:
    - List of Cloudinary URLs (in order of provided dict)
    """
    uploaded_urls = []

    for label, image_file in images_dict.items():
        try:
            unique_id = str(uuid.uuid4())[:8]
            public_id = f"{employee_name}_{label}_{unique_id}"
            
            result = cloudinary.uploader.upload(
                image_file,
                folder="fra_employees",
                public_id=public_id,
                overwrite=False,
                resource_type="image"
            )
            uploaded_urls.append(result.get("secure_url"))
        except Exception as e:
            print(f"[Upload Error for {label}]: {e}")
            uploaded_urls.append(None)

    return uploaded_urls

