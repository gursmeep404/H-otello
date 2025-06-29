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
db = client["ottelodb"]

hosts = db["hosts"]
properties = db["properties"]
availability = db["availability_calendar"]
bookings = db["bookings"]
guests = db["guests"]
analytics = db["analytics_snapshots"]
def setup_indexes():
    hosts.create_index("phone_number", unique=True)
    properties.create_index("host_id")
    availability.create_index([("room_id", ASCENDING), ("date", ASCENDING)], unique=True)
    bookings.create_index("room_id")
    bookings.create_index("property_id")
    guests.create_index("phone_number")
    analytics.create_index("host_id")
    print("✅ Indexes created.")


def insert_sample_data():
    host_id = hosts.insert_one({
        "name":"Advit Garg",
        "phone_number": "+91-7607613614",
        "language_pref": "en",
        "created_at": datetime.utcnow()
    }).inserted_id

    # Create Room ObjectIds first
    room1_id = ObjectId()
    room2_id = ObjectId()

    # Insert Property
    property_id = properties.insert_one({
        "host_id": host_id,
        "name": "Thalasa",
        "location": "Goa",
        "default_price": 90000,
        "rooms": [
            {
                "room_id": room1_id,
                "name": "Room 4",
                "type": "double",
                "max_guests": 4,
                "is_active": True
            },
            {
                "room_id": room2_id,
                "name": "Room 5",
                "type": "double",
                "max_guests": 4,
                "is_active": True
            }
        ],
        "created_at": datetime.utcnow()
    }).inserted_id

    # Insert Availability
    availability.insert_many([
        {
            "room_id": room1_id,
            "date": datetime(2025, 12, 5),
            "is_available": True,
            "price": 1800,
            "source": "manual"
        },
        {
            "room_id": room2_id,
            "date": datetime(2025, 7, 1),
            "is_available": False,
            "price": 2000,
            "source": "manual"
        }
    ])

    # Insert Booking
    bookings.insert_one({
        "room_id": room2_id,
        "property_id": property_id,
        "guest_name": "Gursmeep Kaur",
        "check_in": datetime(2025, 10, 1),
        "check_out": datetime(2025, 5, 3),
        "amount_paid": 700,
        "source": "manual",
        "created_at": datetime.utcnow()
    })

    # Insert Guest (optional)
    guests.insert_one({
        "name": "Prateek Shukla",
        "phone_number": "+91-994476655",
        "email": "shuka@example.com",
        "preferred_language": "en"
    })

    # Insert Analytics Snapshot
    analytics.insert_one({
        "host_id": host_id,
        "date_range": {
            "from": datetime(2025, 7, 1),
            "to": datetime(2025, 7, 7)
        },
        "total_bookings": 365,
        "total_earnings": 7808420,
        "occupancy_rate": 0.9,
        "suggestions": "Raise weekend prices by 10%",
        "created_at": datetime.utcnow()
    })

    print("📦 Sample data seeded successfully.")


if __name__ == "__main__":
    setup_indexes()
    insert_sample_data()