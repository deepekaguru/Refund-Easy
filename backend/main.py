import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from typing import Optional
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.agent import run_agent
import backend.database as db

app = FastAPI(title="Refund Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ---------- Schemas ----------
class ChatRequest(BaseModel):
    customer_id: str
    order_id: str
    message: str
    history: list = []

from typing import Optional

class ChatResponse(BaseModel):
    response: str
    trace: list
    decision: str
    ticket_id: Optional[str] = None

# ---------- Helpers ----------
def extract_decision(response_text: str) -> str:
    text = response_text.upper()
    if "ESCALATED" in text or "MANUAL REVIEW" in text or "24-48" in text:
        return "ESCALATED"
    elif "CANNOT BE APPROVED" in text or "CANNOT APPROVE" in text or "DENIED" in text or "I'M SORRY" in text or "I AM SORRY" in text or "UNABLE" in text or "ALREADY SUBMITTED" in text or "ALREADY REQUESTED" in text or "DUPLICATE" in text or "CANNOT BE PROCESSED" in text:
        return "DENIED"
    elif "APPROVED" in text or "WILL BE PROCESSED" in text or "ELIGIBLE FOR A REFUND" in text:
        return "APPROVED"
    return "UNKNOWN"

def extract_policy_reason(trace: list) -> str:
    for step in trace:
        if step.get("step") == "tool_call" and step.get("tool_name") == "tool_validate_refund_policy":
            output = step.get("output", {})
            if isinstance(output, dict):
                return output.get("reason", "")
    return ""

def generate_ticket_id(customer_id: str) -> str:
    from datetime import datetime
    date_str = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"TKT-{date_str}-{customer_id}"

def get_order_details(customer_id: str, order_id: str) -> dict:
    import json
    path = os.path.join(os.path.dirname(__file__), "../data/customers.json")
    with open(path, "r") as f:
        customers = json.load(f)
    for customer in customers:
        if customer["customer_id"] == customer_id:
            for order in customer["orders"]:
                if order["order_id"] == order_id:
                    return {
                        "customer_name": customer["name"],
                        "customer_email": customer["email"],
                        "item_name": order["item_name"],
                        "amount": order["price"]
                    }
    return {"customer_name": "", "customer_email": "", "item_name": "", "amount": 0}

# ---------- Endpoints ----------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    result = run_agent(
        customer_id=request.customer_id,
        order_id=request.order_id,
        user_message=request.message,
        history=request.history
    )

    response_text = result["response"]
    trace = result["trace"]
    decision = extract_decision(response_text)

    total_tokens = sum(
        s.get("token_usage", {}).get("total_tokens", 0)
        for s in trace if s["step"] == "agent_reasoning"
    )
    total_latency = round(sum(s.get("latency_seconds", 0) for s in trace), 2)

    order_details = get_order_details(request.customer_id, request.order_id)

    ticket_id = None

    # Check if this is a duplicate request
    history_check = db.check_refund_history(request.customer_id, request.order_id)
    is_duplicate = history_check.get("found", False)

    if not is_duplicate:
        if decision == "ESCALATED":
            ticket_id = generate_ticket_id(request.customer_id)
            db.save_support_ticket(
                ticket_id=ticket_id,
                customer_id=request.customer_id,
                order_id=request.order_id,
                customer_name=order_details["customer_name"],
                item_name=order_details["item_name"],
                amount=order_details["amount"],
                reason=response_text[:200]
            )

    policy_reason = extract_policy_reason(trace)
    print(f"DEBUG reason: {policy_reason}")
    db.save_refund_request(
        customer_id=request.customer_id,
        order_id=request.order_id,
        customer_name=order_details["customer_name"],
        item_name=order_details["item_name"],
        amount=order_details["amount"],
        user_message=request.message,
        agent_response=response_text,
        decision=decision,
        reason=policy_reason if policy_reason else response_text[:200],
        total_tokens=total_tokens,
        total_latency=total_latency,
        trace=trace,
        ticket_id=ticket_id
    )

    return ChatResponse(
        response=response_text,
        trace=trace,
        decision=decision,
        ticket_id=ticket_id
    )

@app.get("/customers")
def get_customers():
    import json
    with open(os.path.join(os.path.dirname(__file__), "../data/customers.json"), "r") as f:
        return json.load(f)

@app.post("/report-damage")
def report_damage(customer_id: str, order_id: str):
    import sqlite3
    # In production this would update the CRM
    # For demo — update customers.json flag
    return {"status": "damage report received", 
            "message": "Our team will verify within 24 hours"}

@app.get("/logs")
def get_logs():
    return db.get_all_requests()

@app.get("/tickets")
def get_tickets():
    return db.get_all_tickets()

@app.delete("/clear-logs")
def clear_logs():
    import sqlite3
    db_path = os.path.join(os.path.dirname(__file__), "../data/refund_agent.db")
    conn = sqlite3.connect(db_path)
    conn.execute("DELETE FROM refund_requests")
    conn.execute("DELETE FROM support_tickets")
    conn.commit()
    conn.close()
    return {"status": "cleared"}
