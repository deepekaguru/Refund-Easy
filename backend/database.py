import sqlite3
import os
import json
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "../data/refund_agent.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refund_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT,
            customer_id TEXT NOT NULL,
            order_id TEXT NOT NULL,
            customer_name TEXT,
            item_name TEXT,
            amount REAL,
            user_message TEXT,
            agent_response TEXT,
            decision TEXT,
            reason TEXT,
            total_tokens INTEGER,
            total_latency REAL,
            trace JSON,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            customer_id TEXT NOT NULL,
            order_id TEXT NOT NULL,
            customer_name TEXT,
            item_name TEXT,
            amount REAL,
            reason TEXT,
            status TEXT DEFAULT 'open',
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()

def save_refund_request(
    customer_id, order_id, customer_name, item_name,
    amount, user_message, agent_response, decision,
    reason, total_tokens, total_latency, trace, ticket_id=None
):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO refund_requests (
            ticket_id, customer_id, order_id, customer_name,
            item_name, amount, user_message, agent_response,
            decision, reason, total_tokens, total_latency, trace, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id, customer_id, order_id, customer_name,
        item_name, amount, user_message, agent_response,
        decision, reason, total_tokens, total_latency,
        json.dumps(trace), datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def check_refund_history(customer_id, order_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM refund_requests
        WHERE customer_id = ? AND order_id = ?
        ORDER BY created_at DESC
        LIMIT 1
    """, (customer_id, order_id))
    row = cursor.fetchone()
    conn.close()
    if row:
        return {
            "found": True,
            "decision": row["decision"],
            "created_at": row["created_at"],
            "ticket_id": row["ticket_id"],
            "reason": row["reason"]
        }
    return {"found": False}

def save_support_ticket(ticket_id, customer_id, order_id, customer_name, item_name, amount, reason):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO support_tickets (
            ticket_id, customer_id, order_id, customer_name,
            item_name, amount, reason, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id, customer_id, order_id, customer_name,
        item_name, amount, reason,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))
    conn.commit()
    conn.close()

def get_all_requests():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM refund_requests ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_tickets():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM support_tickets ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

init_db()
