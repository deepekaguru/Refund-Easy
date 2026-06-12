import json
import os
from datetime import datetime, date
from backend.database import check_refund_history as db_check_refund_history

# Load customer data
DATA_PATH = os.path.join(os.path.dirname(__file__), "../data/customers.json")
POLICY_PATH = os.path.join(os.path.dirname(__file__), "../data/refund_policy.txt")

with open(DATA_PATH, "r") as f:
    CUSTOMERS = json.load(f)

with open(POLICY_PATH, "r") as f:
    REFUND_POLICY = f.read()
    
def check_previous_refund_request(customer_id: str, order_id: str) -> dict:
    """Check if a refund request was already submitted for this order."""
    result = db_check_refund_history(customer_id, order_id)
    if result["found"]:
        return {
            "already_requested": True,
            "decision": result["decision"],
            "reason": result.get("reason", ""),
            "requested_on": result["created_at"],
            "ticket_id": result.get("ticket_id"),
            "message": f"A refund request for order {order_id} was already submitted on {result['created_at']} with decision: {result['decision']}."
        }
    return {
        "already_requested": False,
        "message": "No previous refund request found for this order."
    }


def get_customer_order(customer_id: str, order_id: str) -> dict:
    """Look up a customer's order by customer_id and order_id."""
    for customer in CUSTOMERS:
        if customer["customer_id"] == customer_id:
            for order in customer["orders"]:
                if order["order_id"] == order_id:
                    purchase_date = datetime.strptime(order["purchase_date"], "%Y-%m-%d").date()
                    days_since_purchase = (date.today() - purchase_date).days
                    return {
                        "found": True,
                        "customer_name": customer["name"],
                        "customer_id": customer_id,
                        "order_id": order_id,
                        "item_name": order["item_name"],
                        "price": order["price"],
                        "purchase_date": order["purchase_date"],
                        "days_since_purchase": days_since_purchase,
                        "status": order["status"],
                        "is_final_sale": order["is_final_sale"],
                        "is_digital": order["is_digital"],
                        "is_damaged": order["is_damaged"]
                    }
            return {"found": False, "error": f"Order {order_id} not found for customer {customer_id}"}
    return {"found": False, "error": f"Customer {customer_id} not found"}


def validate_refund_policy(order_details: dict) -> dict:
    """Validate an order against the refund policy and return a decision."""
    if not order_details.get("found"):
        return {
            "eligible": False,
            "decision": "DENIED",
            "reason": "Order not found in the system."
        }

    item_name = order_details["item_name"]
    price = order_details["price"]
    days_since_purchase = order_details["days_since_purchase"]
    is_final_sale = order_details["is_final_sale"]
    is_digital = order_details["is_digital"]
    is_damaged = order_details["is_damaged"]

    # Rule 1: Final sale — always denied, no exceptions
    if is_final_sale:
        return {
            "eligible": False,
            "decision": "DENIED",
            "reason": f"{item_name} is a final sale item and cannot be refunded under any circumstances."
        }

    # Rule 2: Digital product — always denied, no exceptions
    if is_digital:
        return {
            "eligible": False,
            "decision": "DENIED",
            "reason": f"{item_name} is a digital product and is non-refundable once delivered."
        }

    # Rule 3: Damaged/defective item — must be reported within 7 days
    # If within 7 days: APPROVED with fees waived
    # If outside 7 days: DENIED
    if is_damaged:
        if days_since_purchase <= 7:
            refund_amount = price  
            if price >= 500:
                return {
                    "eligible": True,
                    "decision": "ESCALATED",
                    "reason": f"{item_name} was reported as damaged within 7 days. Refund of ${refund_amount} qualifies for fee waiver but exceeds $500 and requires human review."
                }
            return {
                "eligible": True,
                "decision": "APPROVED",
                "reason": f"{item_name} was reported as damaged within 7 days. A free prepaid shipping label will be provided. Refund of ${refund_amount} will be processed within 5-7 business days.",
                "refund_amount": refund_amount,
                "prepaid_label": True
            }
        else:
            return {
                "eligible": False,
                "decision": "DENIED",
                "reason": f"{item_name} is marked as damaged but was reported {days_since_purchase} days after delivery. Damaged or defective items must be reported within 7 calendar days of delivery."
            }

    # Rule 4: Outside 30-day return window
    if days_since_purchase > 30:
        return {
            "eligible": False,
            "decision": "DENIED",
            "reason": f"The return window has passed. {item_name} was purchased {days_since_purchase} days ago. Refunds are only accepted within 30 days of purchase."
        }

    # Rule 5: Over $500 — escalate
    if price >= 500:
        return {
            "eligible": True,
            "decision": "ESCALATED",
            "reason": f"Refund of ${price} for {item_name} meets or exceeds the $500 threshold and requires Senior Management review before processing."
        }


    # Rule 6: Standard return — full refund
    return {
        "eligible": True,
        "decision": "APPROVED",
        "reason": f"{item_name} is eligible for a full refund of ${price}. It will be processed to your original payment method within 5-7 business days. Return shipping is the customer's responsibility.",
        "refund_amount": price,
        "prepaid_label": False
    }


def escalate_to_human(reason: str) -> dict:
    """Escalate a refund request to a human agent."""
    return {
        "escalated": True,
        "message": f"This request has been escalated to our support team for manual review. Reason: {reason}. You will receive an email within 24-48 hours."
    }


def get_refund_policy() -> str:
    """Return the full refund policy text."""
    return REFUND_POLICY


