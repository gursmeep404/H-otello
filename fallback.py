from fastapi import FastAPI, Request
from datetime import datetime

import json


app = FastAPI()

def send_to_dashboard(query_text: str,reason: str ="unparsable"):
    import requests
    payload = {
        "query":query_text,
        "reason":reason,
        "timestamp":datetime.utcnow().isoformat()
    }
    try:
        response = requests.post("/api/query",json=payload)
        print(f"Query Sent to the Dashboard, Will be answered Later:{response.status_code}")
    except Exception as e:
        print("Failed to send to the Dashboard: {e}")