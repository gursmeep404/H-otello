from pymongo import MongoClient, ASCENDING
from datetime import datetime
from bson.objectid import ObjectId
from dotenv import load_dotenv
import os

MONGO_URI = "mongodb+srv://prateek:prateekadvitgursmeep@2025@ottelo.y5psic0.mongodb.net/"

client = MongoClient(MONGO_URI)

db = client["main"]


hosts = db["hosts"]
hosts.create_index("phone_number", unique=True)


properties = db["properties"]
properties.create_index("host_id")


availability = db["availability_calendar"]
availability.create_index([("room_id", ASCENDING), ("date", ASCENDING)], unique=True)


bookings = db["bookings"]
bookings.create_index("room_id")
bookings.create_index("property_id")


guests = db["guests"]
guests.create_index("phone_number", unique=False)


messages = db["messages"]
messages.create_index("phone_number")


analytics = db["analytics_snapshots"]
analytics.create_index("host_id")

print("Tables created")


