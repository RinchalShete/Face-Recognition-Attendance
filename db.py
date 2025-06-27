import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]

users_col = db["users"]
employees_col = db["employees"]
attendance_col = db["attendance"]

