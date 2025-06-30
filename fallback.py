from datetime import datetime

import json

def send_to_dashboard(query_text: str,reason: str ="unparsable"):
    import requests
    payload = {
        "query":query_text,
        "reason":reason,
    }
    try:
        response = requests.post("http://127.0.0.1:8000/api/query",json=payload)
        print(f"Query Sent to the Dashboard, Will be answered Later:{response.status_code}")
    except Exception as e:
        print("Failed to send to the Dashboard: {e}")