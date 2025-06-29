from pymongo import MongoClient, ASCENDING
from datetime import datetime
from bson.objectid import ObjectId
from dotenv import load_dotenv
from urllib.parse import quote_plus
import os

load_dotenv()


user = os.getenv("MONGO_USER") or ""
password_env = os.getenv("MONGO_PASS") or ""
password = quote_plus(password_env.encode())
uri = f"mongodb+srv://{user}:{password}@ottelo.y5psic0.mongodb.net/?retryWrites=true&w=majority"

