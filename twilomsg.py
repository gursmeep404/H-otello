from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()

TWILIO_SID = os.getenv("TWILIO_SID")
TWILIO_AUTH = os.getenv("TWILIO_AUTH")
TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"  # Twilio sandbox number

client = Client(TWILIO_SID, TWILIO_AUTH)

to_number = "whatsapp:+917607665801" 

if to_number:
    message = client.messages.create(
        body=f"✅ Here's the response from the staff: Hello how are you",
        from_=TWILIO_WHATSAPP_NUMBER,
        to=to_number
    )
    print(f"✅ Sent WhatsApp message SID: {message.sid}")
