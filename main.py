from fastapi import FastAPI, Form
from fastapi.responses import PlainTextResponse

app = FastAPI()

@app.post("/webhook")
async def whatsapp_webhook(From: str = Form(...), Body: str = Form(...)):
    print(f"Message from {From}: {Body}")

    if "block room" in Body.lower():
        return PlainTextResponse("Room blocked.")

    elif "change rate" in Body.lower():
        return PlainTextResponse("Price updated.")

    elif "where is the property" in Body.lower():
        return PlainTextResponse("It's at 123 Beach Road, Goa.")

    else:
        return PlainTextResponse("Sorry, I didn’t understand that.")
