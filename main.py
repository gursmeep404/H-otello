from fastapi import FastAPI, Form
from fastapi.responses import Response
import os
from dotenv import load_dotenv
from mongodb_assistant import MongoDBAssistant
from urllib.parse import quote_plus
from html import escape
import json

# Load environment variables
load_dotenv()

app = FastAPI()

mongo_user = quote_plus(os.getenv("MONGO_USER") or "")
mongo_pass = quote_plus(os.getenv("MONGO_PASS") or "")
MONGODB_URI = f"mongodb+srv://{mongo_user}:{mongo_pass}@ottelo.y5psic0.mongodb.net/?retryWrites=true&w=majority"

assistant = MongoDBAssistant(
    api_key=os.getenv("GEMINI_API_KEY") or "",
    mongodb_uri=MONGODB_URI,
    db_name=os.getenv("MONGO_DB_NAME") or "",
)

@app.post("/webhook")
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    print(f"\nMessage from WhatsApp: {From} => {Body}")

    try:
        result = assistant.chat(Body)

        if isinstance(result, dict) and "output" in result:
            raw_output = result["output"]

            try:
                docs = json.loads(raw_output)
                if isinstance(docs, list):
                    response_text = "Bookings:\n\n"
                    for i, doc in enumerate(docs, start=1):
                        response_text += f"{i}. Guest: {doc.get('guest_name')}\n   Room ID: {doc.get('room_id')}\n   Check-in: {doc.get('check_in')}\n   Check-out: {doc.get('check_out')}\n   Amount Paid: ₹{doc.get('amount_paid')}\n\n"
                else:
                    response_text = raw_output
            except Exception:
                response_text = raw_output
        elif isinstance(result, str):
            response_text = result
        else:
            response_text = str(result)

    except Exception as e:
        response_text = f"Something went wrong: {str(e)}"

    print("Response to WhatsApp:")
    print(response_text)

    
    safe_response = escape(response_text)[:1500]

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{safe_response}</Message>
</Response>"""

    print("TwiML being sent to Twilio:")
    print(twiml)

    return Response(content=twiml, media_type="application/xml")
