from fastapi import FastAPI, Form
from fastapi.responses import Response
import os
from dotenv import load_dotenv
from mongodb_assistant import MongoDBAssistant
from urllib.parse import quote_plus

# Load environment variables
load_dotenv()

app = FastAPI()

mongo_user = quote_plus(os.getenv("MONGO_USER") or "")
mongo_pass = quote_plus(os.getenv("MONGO_PASS") or "")
MONGODB_URI = f"mongodb+srv://{mongo_user}:{mongo_pass}@ottelo.y5psic0.mongodb.net/?retryWrites=true&w=majority"

assistant = MongoDBAssistant(
    api_key=os.getenv("GEMINI_API_KEY"),
    mongodb_uri=MONGODB_URI,
    db_name=os.getenv("MONGO_DB_NAME")
)

@app.post("/webhook")
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    print(f"\nMessage from WhatsApp: {From} => {Body}")

    try:
        response_text = assistant.chat(Body)
    except Exception as e:
        response_text = f"Something went wrong: {str(e)}"

    print("Response to WhatsApp:")
    print(response_text)

    # Return TwiML XML response
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{response_text}</Message>
</Response>"""

    return Response(content=twiml, media_type="application/xml")
