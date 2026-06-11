import streamlit as st
import os
import json
import requests
from datetime import datetime

API_URL = os.getenv("BACKEND_API_URL", "http://localhost:8000")

st.set_page_config(page_title="Refund Easy", layout="wide", initial_sidebar_state="collapsed")

def load_customers():
    try:
        res = requests.get(f"{API_URL}/customers")

        st.write("Status:", res.status_code)
        st.write("Response:", res.text[:500])

        return res.json()

    except Exception as e:
        st.error(f"Error: {e}")
        return []

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

* { font-family: 'Inter', sans-serif !important; }

.stApp > div:first-child { margin-top: 0 !important; padding-top: 0 !important; }
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.stApp {
    background: #FFFBEB;
    border-left: 3px solid #C9A84C;
    border-right: 3px solid #C9A84C;
    border-bottom: 3px solid #C9A84C;
}
.block-container { padding: 0 !important; max-width: 100% !important; margin: 0 !important; }
[data-testid="stAppViewContainer"] { padding: 0 !important; }
[data-testid="stMain"] { padding: 0 !important; }
[data-testid="stMainBlockContainer"] { padding: 0 !important; }
.stMainBlockContainer { padding-top: 0 !important; }
section.main > div:first-child { padding-top: 0 !important; }

.navbar {
    background: #1A1209;
    border-bottom: 3px solid #C9A84C;
    padding: 0 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 100px;
    width: 100%;
    margin: 0;
    position: relative;
}
.nav-logo {
    width: 36px; height: 36px; background: #C9A84C;
    border-radius: 10px; display: flex; align-items: center;
    justify-content: center; font-size: 13px; font-weight: 900; color: #1A1209;
    border-bottom: 4px solid #8B6914; border-right: 4px solid #8B6914;
    transform: perspective(100px) rotateX(5deg) rotateY(-5deg);
}
.nav-title { color: #C9A84C; font-size: 24px; font-weight: 800; letter-spacing: -0.3px; }

.main-content { padding: 16px 20px 20px 20px; }

.section-label {
    font-size: 13px; font-weight: 700; color: #92784A;
    letter-spacing: 0.01em; margin-bottom: 10px; margin-top: 4px;
}

.stTextArea textarea {
    background-color: #ffffff !important;
    border: 1px solid #E8D5A3 !important;
    color: #1A1209 !important;
    font-size: 14px !important;
}
.stTextArea textarea:focus {
    border-color: #C9A84C !important;
    box-shadow: 0 0 0 2px rgba(201,168,76,0.2) !important;
}
textarea {
    background-color: #ffffff !important;
    border: 1px solid #E8D5A3 !important;
    color: #1A1209 !important;
}
div[data-baseweb="textarea"] { background-color: #ffffff !important; }
div[data-baseweb="input"] input {
    background-color: #ffffff !important;
    border: 1px solid #E8D5A3 !important;
    font-size: 14px !important;
}
div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border-color: #E8D5A3 !important;
}
div[data-baseweb="select"] span { color: #1A1209 !important; font-size: 14px !important; }

.chat-user-bubble {
    background: #C9A84C; color: #1A1209;
    padding: 12px 16px; border-radius: 10px 10px 2px 10px;
    font-size: 14px; font-weight: 600;
    margin-left: auto; max-width: 80%;
    margin-bottom: 8px; display: block;
    text-align: right; line-height: 1.6;
}
.chat-agent-bubble {
    background: #FFFDF5; color: #1A1209;
    padding: 14px 18px; border-radius: 10px 10px 10px 2px;
    font-size: 14px; max-width: 92%; margin-bottom: 20px;
    border: 1px solid #E8D5A3; display: block;
    line-height: 1.8;
}

.badge { font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px; display: inline-block; }
.badge-approved { background: #D1FAE5; color: #065F46; }
.badge-denied { background: #FEE2E2; color: #991B1B; }
.badge-escalated { background: #FEF3C7; color: #92400E; }
.badge-unknown { background: #E5E7EB; color: #374151; }
.meta-text { font-size: 11px; color: #9CA3AF; }

.metric-box {
    background: #FFF8DC; border-radius: 10px;
    padding: 14px; margin-bottom: 12px;
    border: 1px solid #E8D5A3;
}
.metric-val { font-size: 26px; font-weight: 800; color: #C9A84C; }
.metric-val-green { font-size: 26px; font-weight: 800; color: #059669; }
.metric-val-red { font-size: 26px; font-weight: 800; color: #DC2626; }
.metric-val-amber { font-size: 26px; font-weight: 800; color: #D97706; }
.metric-label { font-size: 11px; font-weight: 500; color: #92784A; margin-top: 4px; }

.order-card {
    background: #FFFBEB; border-radius: 10px; padding: 14px 18px;
    border: 1px solid #E8D5A3; margin-top: 8px;
}
.order-card-label {
    font-size: 16px; font-weight: 700; color: #8B6914;
    margin-bottom: 12px; letter-spacing: 0.01em;
}
.order-card-row { display: flex; gap: 48px; flex-wrap: wrap; padding-top: 4px; }
.order-card-key { font-size: 14px; font-weight: 600; color: #92784A; margin-bottom: 3px; }
.order-card-item { font-size: 12px; font-weight: 500; color: #1A1209; }
.order-card-item span { color: #8B6914; font-weight: 600; }

.stButton > button {
    border-radius: 8px !important; font-size: 13px !important;
    font-weight: 600 !important; height: 40px !important; width: 100% !important;
}
.stButton > button[kind="primary"] {
    background-color: #C9A84C !important;
    border-color: #8B6914 !important;
    color: #1A1209 !important;
}
div[data-testid="column"] { padding: 0 4px !important; }

/* Expander fix — clean label, no overlap */
[data-testid="stExpander"] {
    border: 1px solid #E8D5A3 !important;
    border-radius: 8px !important;
    margin-bottom: 6px !important;
    background: #FFFDF5 !important;
}
[data-testid="stExpander"] summary {
    font-size: 13px !important;
    font-weight: 600 !important;
    color: #1A1209 !important;
    padding: 10px 14px !important;
    align-items: center !important;
}
[data-testid="stExpander"] summary p {
    font-size: 13px !important;
    font-weight: 600 !important;
    margin: 0 !important;
    padding: 0 !important;
    line-height: 1.4 !important;
}
</style>
""", unsafe_allow_html=True)

# ---------- Session state ----------
if "saved_customer_id" not in st.session_state:
    st.session_state.saved_customer_id = None
if "saved_order_id" not in st.session_state:
    st.session_state.saved_order_id = None
if "current_exchange" not in st.session_state:
    st.session_state.current_exchange = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = []
if "trace_logs" not in st.session_state:
    st.session_state.trace_logs = []
if "show_chat" not in st.session_state:
    st.session_state.show_chat = False
if "chat_action" not in st.session_state:
    st.session_state.chat_action = None
if "stats" not in st.session_state:
    st.session_state.stats = {"total": 0, "approved": 0, "denied": 0, "escalated": 0}
if "active_customer_key" not in st.session_state:
    st.session_state.active_customer_key = None
if "input_key" not in st.session_state:
    st.session_state.input_key = 0
if "session_terminated" not in st.session_state:
    st.session_state.session_terminated = False

# ---------- Helpers ----------
def get_decision(response_text):
    text = response_text.upper()
    if "ESCALATED" in text or "MANUAL REVIEW" in text or "24-48" in text:
        return "ESCALATED", "badge-escalated"
    elif "CANNOT BE APPROVED" in text or "CANNOT APPROVE" in text or "UNABLE TO APPROVE" in text or "DENIED" in text or "NOT ELIGIBLE" in text or "I'M SORRY" in text or "I AM SORRY" in text or "ALREADY SUBMITTED" in text or "DUPLICATE" in text or "ALREADY REQUESTED" in text or "CANNOT BE PROCESSED" in text:
        return "DENIED", "badge-denied"
    elif "APPROVED" in text or "ELIGIBLE FOR A REFUND" in text or "WILL BE PROCESSED" in text:
        return "APPROVED", "badge-approved"
    return "UNKNOWN", "badge-unknown"

def get_orders_for_customer(customer_id, customers):
    for c in customers:
        if c["customer_id"] == customer_id:
            return c["orders"]
    return []

def send_message(customer_id, order_id, message):
    full_message = f"Customer ID: {customer_id}, Order ID: {order_id}. {message}"
    try:
        prior = list(reversed(st.session_state.chat_history))
        history_payload = []
        for entry in prior:
            history_payload.append({"role": "user", "content": entry["message"]})
            history_payload.append({"role": "assistant", "content": entry["response"]})

        res = requests.post(f"{API_URL}/chat", json={
            "customer_id": customer_id,
            "order_id": order_id,
            "message": full_message,
            "history": history_payload
        })
        data = res.json()
        agent_response = data["response"]
        trace = data["trace"]
        ticket_id = data.get("ticket_id", None)
        decision, badge_class = get_decision(agent_response)

        if "[DENIED]" in agent_response and "terminated" in agent_response.lower():
            st.session_state.session_terminated = True

        timestamp = datetime.now().strftime("%H:%M:%S")
        total_tokens = sum(s.get("token_usage", {}).get("total_tokens", 0) for s in trace if s["step"] == "agent_reasoning")
        total_latency = round(sum(s.get("latency_seconds", 0) for s in trace), 2)
        exchange = {
            "customer_id": customer_id, "order_id": order_id,
            "message": message, "response": agent_response,
            "decision": decision, "badge_class": badge_class,
            "timestamp": timestamp, "trace": trace,
            "total_tokens": total_tokens, "total_latency": total_latency,
            "ticket_id": ticket_id
        }
        st.session_state.current_exchange = exchange
        st.session_state.chat_history.insert(0, exchange)
        st.session_state.trace_logs.insert(0, exchange)
        st.session_state.stats["total"] += 1
        if decision == "APPROVED":
            st.session_state.stats["approved"] += 1
        elif decision == "DENIED":
            st.session_state.stats["denied"] += 1
        elif decision == "ESCALATED":
            st.session_state.stats["escalated"] += 1
    except Exception as e:
        st.error(f"Backend error: {e}")

# ---------- Navbar ----------
st.markdown("""
<div class="navbar">
    <div style="width:120px"></div>
    <div style="position:absolute;left:50%;transform:translateX(-50%);display:flex;align-items:center;gap:14px">
        <div class="nav-logo">RE</div>
        <div style="display:flex;flex-direction:column;gap:3px">
            <span class="nav-title" style="font-size:30px">Refund Easy</span>
            <span style="font-size:16px;color:rgba(201,168,76,0.6)">AI-powered refund decisions, instantly.</span>
        </div>
""", unsafe_allow_html=True)
st.markdown('<div class="main-content">', unsafe_allow_html=True)

# ---------- Layout ----------
left, right = st.columns([2.2, 0.8], gap="small")

# ---------- Left ----------
with left:
    customers = load_customers()

    with st.container(border=True):
        col1, col2 = st.columns(2)
        with col1:
            customer_id = st.text_input("Customer ID")
        with col2:
            orders = get_orders_for_customer(customer_id, customers)
            if orders:
                order_options = [f"{o['order_id']} — {o['item_name']}" for o in orders]
                selected_order = st.selectbox("Order ID", order_options)
                order_id = selected_order.split(" — ")[0]
                selected_order_details = next((o for o in orders if o["order_id"] == order_id), None)
            else:
                st.text_input("Order ID", disabled=True)
                order_id = None
                selected_order_details = None

        if customer_id and not orders:
            st.warning("⚠️ Customer ID not found. Please enter a valid Customer ID (e.g. C001–C021).")

        if selected_order_details:
            st.markdown(
                f'<div class="order-card">'
                f'<div class="order-card-label">Order Details</div>'
                f'<div class="order-card-row">'
                f'<div><div class="order-card-key">Item</div><div class="order-card-item">{selected_order_details["item_name"]}</div></div>'
                f'<div><div class="order-card-key">Price</div><div class="order-card-item">${selected_order_details["price"]}</div></div>'
                f'<div><div class="order-card-key">Purchased</div><div class="order-card-item">{datetime.strptime(selected_order_details["purchase_date"], "%Y-%m-%d").strftime("%m-%d-%Y")}</div></div>'
                f'<div><div class="order-card-key">Status</div><div class="order-card-item">{selected_order_details["status"].capitalize()}</div></div>'
                f'</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    # Reset chat when customer/order changes
    active_customer_id = customer_id or st.session_state.saved_customer_id
    active_order_id = order_id or st.session_state.saved_order_id
    current_key = f"{active_customer_id}_{active_order_id}"

    if current_key != st.session_state.active_customer_key:
        st.session_state.active_customer_key = current_key
        st.session_state.chat_history = []
        st.session_state.conversation_history = []
        st.session_state.current_exchange = None
        st.session_state.session_terminated = False
        st.session_state.input_key += 1

    if active_customer_id and active_order_id and not st.session_state.session_terminated:
        with st.container(border=True):
            st.markdown('<div class="section-label" style="font-size:14px;font-weight:700;">Chat Here with Our Virtual Assistant Alex</div>', unsafe_allow_html=True)
            user_input = st.text_area(
                " ",
                placeholder="Type your message here...",
                height=80,
                key=f"chat_input_{st.session_state.input_key}"
            )
            if st.button("Send", type="primary"):
                msg = user_input.strip() if user_input else ""
                if msg and active_customer_id and active_order_id:
                    with st.spinner("Agent is thinking..."):
                        send_message(active_customer_id, active_order_id, msg)
                    st.session_state.chat_action = None
                    st.session_state.input_key += 1
                    st.rerun()
                elif not msg:
                    st.warning("Please type a message.")
                else:
                    st.warning("Please enter Customer ID and select an Order first.")

    if st.session_state.session_terminated:
        st.error("This session has been terminated due to a conduct violation. Please contact support@techmart.com for further assistance.")

    if st.session_state.chat_history:
        with st.container(border=True):
            st.markdown('<div class="section-label">Chat History</div>', unsafe_allow_html=True)
            for entry in st.session_state.chat_history:
                st.markdown(
                    f'<div class="chat-user-bubble">🧑 {entry["message"]}</div>',
                    unsafe_allow_html=True
                )
                with st.container():
                    st.markdown(
                        f'<div class="chat-agent-bubble"><strong>Alex</strong><br><br>{entry["response"]}</div>',
                        unsafe_allow_html=True
                    )

    if st.button("🗑️ Clear Session"):
        st.session_state.current_exchange = None
        st.session_state.chat_history = []
        st.session_state.conversation_history = []
        st.session_state.trace_logs = []
        st.session_state.show_chat = False
        st.session_state.chat_action = None
        st.session_state.active_customer_key = None
        st.session_state.input_key += 1
        st.session_state.session_terminated = False
        st.session_state.stats = {"total": 0, "approved": 0, "denied": 0, "escalated": 0}
        st.rerun()

# ---------- Right ----------
with right:
    st.markdown("<div style='margin-top:16px'>", unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown('<div class="section-label">Overview</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-box"><div class="metric-val">{st.session_state.stats["total"]}</div><div class="metric-label">Total runs</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-box"><div class="metric-val-green">{st.session_state.stats["approved"]}</div><div class="metric-label">Approved</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-box"><div class="metric-val-red">{st.session_state.stats["denied"]}</div><div class="metric-label">Denied</div></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="metric-box"><div class="metric-val-amber">{st.session_state.stats["escalated"]}</div><div class="metric-label">Escalated</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.trace_logs:
        with st.container(border=True):
            st.markdown('<div class="section-label">Agent Thinking</div>', unsafe_allow_html=True)
            for log_idx, log_entry in enumerate(st.session_state.trace_logs):
                st.markdown(f"""
                    <div style="background:#FFF8DC;border:1px solid #E8D5A3;border-radius:8px;
                    padding:10px 14px;margin-bottom:8px;font-size:13px;font-weight:700;color:#92784A;">
                    Run {len(st.session_state.trace_logs) - log_idx} — {log_entry['timestamp']} · {log_entry['decision']}
                    </div>
                """, unsafe_allow_html=True)
                for step in log_entry["trace"]:
                    if step["step"] == "tool_call":
                        import json
                        input_str = json.dumps(step.get("input", {}), indent=2)
                        output_str = json.dumps(step.get("output", {}), indent=2)
                        st.markdown(f"""
                            <div style="background:#F0FDF4;border:1px solid #D1FAE5;border-radius:6px;
                            padding:10px 14px;margin-bottom:6px;margin-left:12px;font-size:12px;color:#065F46;line-height:1.6;">
                            <strong>Tool: {step['tool_name']}</strong> &nbsp;·&nbsp; 
                            Status: {step.get('status')} &nbsp;·&nbsp; 
                            {step.get('latency_seconds', 0)}s<br><br>
                            <strong>Input:</strong><br>
                            <pre style="background:#ECFDF5;padding:8px;border-radius:4px;font-size:11px;color:#1A1209;overflow-x:auto;">{input_str}</pre>
                            <strong>Output:</strong><br>
                            <pre style="background:#ECFDF5;padding:8px;border-radius:4px;font-size:11px;color:#1A1209;overflow-x:auto;">{output_str}</pre>
                            </div>
                        """, unsafe_allow_html=True)
                    elif step["step"] == "agent_reasoning":
                        usage = step.get("token_usage", {})
                        content = step.get("content", "")
                        st.markdown(f"""
                            <div style="background:#FFFDF5;border:1px solid #E8D5A3;border-radius:6px;
                            padding:10px 14px;margin-bottom:6px;margin-left:12px;font-size:12px;color:#1A1209;line-height:1.6;">
                            <strong>Agent Reasoning</strong><br><br>
                            {content if content else "<em style='color:#9CA3AF'>No reasoning content</em>"}<br><br>
                            <span style="color:#9CA3AF;font-size:11px;">
                            Prompt: {usage.get('prompt_tokens', 0)} | 
                            Completion: {usage.get('completion_tokens', 0)} | 
                            Latency: {step.get('latency_seconds', 0)}s
                            </span>
                            </div>
                        """, unsafe_allow_html=True)
