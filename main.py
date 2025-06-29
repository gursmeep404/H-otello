from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse
import google.generativeai as genai
import json
import os
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in .env file")


genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(model_name="gemini-1.5-flash-latest")


app = FastAPI()


def extract_intent_from_message(message: str) -> dict:
    prompt = f"""
You are a hotel assistant bot. Understand the user's message and extract structured data.

Input: "{message}"

Reply only with JSON like this:
{{
  "action": "block_room" / "change_rate" / "get_address",
  "room": "3",
  "start_date": "2024-07-02",
  "end_date": "2024-07-05",
  "price": "1800"
}}

If fields are not relevant, leave them null.
"""

    try:
        
        response = model.generate_content(prompt)
        raw_text = response.text.strip()

        print("Raw Gemini Output:")
        print(raw_text)

        # 🧹 Clean markdown formatting if present
        if raw_text.startswith("```"):
            lines = raw_text.splitlines()
            json_lines = [line for line in lines if not line.strip().startswith("```") and line.strip() != "json"]
            raw_text = "\n".join(json_lines).strip()

        # Parse cleaned JSON string
        parsed = json.loads(raw_text)
        return parsed

    except Exception as e:
        print("Error parsing Gemini response:", e)
        return {"action": "unknown", "error": str(e)}



@app.post("/webhook")
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    print(f"\nMessage from {From}: {Body}")

    parsed = extract_intent_from_message(Body)

    print("Gemini Parsed Output:")
    print(json.dumps(parsed, indent=2))

    return PlainTextResponse(f"Gemini JSON:\n{json.dumps(parsed, indent=2)}")
