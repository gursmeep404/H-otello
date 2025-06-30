from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
from datetime import datetime
import uuid
from twilio.rest import Client
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory store
queries: Dict[str, Dict] = {}
query_counter = 0

# Pydantic schemas
class QueryRequest(BaseModel):
    query: str

class RespondRequest(BaseModel):
    query: str
    response: str

@app.post("/api/query")
def receive_query(payload: QueryRequest):
    global query_counter
    query_counter += 1
    query_id = f"query_{int(datetime.utcnow().timestamp())}_{query_counter}"
    
    queries[query_id] = {
        "id": query_id,
        "query": payload.query,
        "status": "pending",
        "timestamp": datetime.utcnow().isoformat(),
        "response": None,
        "answeredAt": None,
    }

    print(f"New query received [{query_id}]: {payload.query}")
    print(f"Total unanswered queries: {get_unanswered_count()}")
    return {"message": "Query received", "id": query_id}

@app.get("/api/query")
def get_oldest_unanswered():
    unanswered = get_oldest_unanswered_query()
    if unanswered:
        return {
            "query": unanswered["query"],
            "id": unanswered["id"],
            "timestamp": unanswered["timestamp"],
            "unansweredCount": get_unanswered_count()
        }
    return {"query": None, "unansweredCount": 0}

@app.post("/api/respond")
def respond_to_query(payload: RespondRequest):
    TWILIO_SID = os.getenv("TWILIO_SID")
    TWILIO_AUTH = os.getenv("TWILIO_AUTH")
    TWILIO_WHATSAPP_NUMBER = "whatsapp:+14155238886"
    query_id = find_query_id_by_content(payload.query)
    client = Client(TWILIO_SID, TWILIO_AUTH)
    to_number = "whatsapp:+917607665801"
    if to_number:
        message = client.messages.create(
            body=f"✅ Here's the human-answered response:\n\n{payload.response}",
            from_=TWILIO_WHATSAPP_NUMBER,
            to=to_number
        )
    print(f"✅ Sent WhatsApp message SID: {message.sid}")

    if query_id and query_id in queries:
        queries[query_id]["status"] = "answered"
        queries[query_id]["response"] = payload.response
        queries[query_id]["answeredAt"] = datetime.utcnow().isoformat()

        print(f"Query answered [{query_id}]: {payload.response}")
        print(f"Remaining unanswered queries: {get_unanswered_count()}")
        return {"message": "Response submitted"}

    raise HTTPException(status_code=404, detail="Query not found or already answered")

@app.get("/api/response/{query_id}")
def get_response(query_id: str):
    query = queries.get(query_id)
    if not query:
        raise HTTPException(status_code=404, detail="Query not found")
    return {
        "id": query["id"],
        "query": query["query"],
        "status": query["status"],
        "response": query["response"],
        "answeredAt": query["answeredAt"]
    }

@app.get("/api/queries")
def get_all_queries():
    return {
        "totalQueries": len(queries),
        "unansweredCount": get_unanswered_count(),
        "queries": queries
    }

@app.get("/api/stats")
def get_stats():
    total = len(queries)
    answered = sum(1 for q in queries.values() if q["status"] == "answered")
    pending = total - answered
    return {
        "totalQueries": total,
        "answeredQueries": answered,
        "pendingQueries": pending,
        "queryCounter": query_counter
    }

@app.delete("/api/queries")
def clear_queries():
    global queries, query_counter
    queries = {}
    query_counter = 0
    print("All queries cleared")
    return {"message": "All queries cleared"}

# Helper functions
def get_unanswered_count():
    return sum(1 for q in queries.values() if q["status"] == "pending")

def get_oldest_unanswered_query():
    unanswered = sorted(
        (q for q in queries.values() if q["status"] == "pending"),
        key=lambda x: x["timestamp"]
    )
    return unanswered[0] if unanswered else None

def find_query_id_by_content(query_content: str) -> Optional[str]:
    for qid, q in queries.items():
        if q["query"] == query_content and q["status"] == "pending":
            return qid
    return None