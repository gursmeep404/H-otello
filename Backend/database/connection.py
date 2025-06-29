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

client = MongoClient(uri)
db = client["main"]

hosts = db["hosts"]
properties = db["properties"]
availability = db["availability_calendar"]
bookings = db["bookings"]
guests = db["guests"]


hosts.create_index("phone_number", unique=True)
properties.create_index("host_id")
availability.create_index([("room_id", ASCENDING), ("date", ASCENDING)], unique=True)
bookings.create_index("room_id")
bookings.create_index("property_id")
guests.create_index("phone_number")

print("✅ Collections & Indexes Created")

# ==== INSERTING SAMPLE DATA ====

# Insert host
host_id = hosts.insert_one({
    "name": "Gursmeep Kaur",
    "phone_number": "7607665801",
    "created_at": datetime.utcnow()
}).inserted_id

# Insert property
room1_id = ObjectId()
room2_id = ObjectId()

property_id = properties.insert_one({
    "host_id": host_id,
    "name": "J startupHouse",
    "location": "Jaipur",
    "default_price": 1800,
    "rooms": [
        {
            "room_id": room1_id,
            "name": "Room_1",
            "type": "double",
            "max_guests": 4,
            "is_active": True
        },
        {
            "room_id": room2_id,
            "name": "Room_2",
            "type": "single",
            "max_guests": 1,
            "is_active": True
        }
    ],
    "created_at": datetime.utcnow()
}).inserted_id

# Insert booking
bookings_id = bookings.insert_one({
    "room_id": room1_id,
    "property_id": property_id,
    "guest_name": "Robin Shukla",
    "check_in": datetime(2025, 7, 3),
    "check_out": datetime(2025, 7, 6),
    "amount_paid": 4000,
    "source": "manual",
    "created_at": datetime.utcnow()
}).inserted_id

print("📦 Sample data inserted successfully.")
