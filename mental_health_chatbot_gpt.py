import streamlit as st
import hashlib
import json
import os
import datetime
from openai import OpenAI

# ✅ Embed your project API key here
openai_api_key = "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"

client = OpenAI(api_key=openai_api_key)

def get_gpt_response(prompt):
    try:
        res = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a supportive and empathetic mental health assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠️ GPT Error: {e}"

# ---------------------------
# 🔐 User Auth
# ---------------------------
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    save_users(users)
    return True

def login_user(username, password):
    users = load_users()
    return username in users and users[username] == hash_password(password)

# ---------------------------
# 💬 Chat Storage
# ---------------------------
def load_messages():
    if os.path.exists("messages.json"):
        with open("messages.json", "r") as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open("messages.json", "w") as f:
        json.dump(messages, f)

# ---------------------------
# 🌗 UI Setup
# ---------------------------
st.set_page_config(page_title="GPT Chat", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "refresh" in st.session_state:
    del st.session_state["refresh"]

# 🔘 Theme toggle
st.sidebar.markdown("🌗 **Theme**")
dark_mode = st.sidebar.checkbox("Enable Dark Mode")
if dark_mode:
    st.markdown("""
    <style>
    body { background-color: #121212; color: #f5f5f5; }
    .chat-bubble { background-color: #2e2e2e; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
    .chat-bubble { background-color: #f0f2f6; }
    </style>
    """, unsafe_allow_html=True)

# ---------------------------
# 🔐 Login/Register UI
# ---------------------------
st.title("💬 GPT Mental Wellness Chat")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("🔐 Menu", menu)

if choice == "Register":
    st.subheader("📝 Create Account")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    if st.button("Register"):
        if register_user(new_user, new_pass):
            st.success("✅ Registered! Please log in.")
        else:
            st.warning("⚠️ Username already exists.")

elif choice == "Login":
    st.subheader("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"✅ Welcome, {username}!")
        else:
            st.error("❌ Invalid login")

# ---------------------------
# 💬 Chat Interface
# ---------------------------
if st.session_state.logged_in:
    messages = load_messages()
    st.markdown(f"### 👋 Hello, **{st.session_state.username}**")

    for msg in messages:
        is_user = msg["sender"] == st.session_state.username
        align = "right" if is_user else "left"
        icon = "🧍‍♂️" if is_user else "🤖"
        color = "#cce5ff" if is_user else "#f1f0f0"
        st.markdown(f"""
        <div style='text-align:{align}; margin-bottom:10px;'>
            <div style='display:inline-block; background:{color}; padding:10px; border-radius:10px; max-width:80%;'>
                <b>{icon} {msg["sender"]}</b> <small style='opacity:0.6'>[{msg["time"]}]</small><br>
                {msg["text"]}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Input message
    with st.form("send_form", clear_on_submit=True):
        user_msg = st.text_input("Type your message")
        send = st.form_submit_button("Send")

    if send and user_msg:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        messages.append({
            "sender": st.session_state.username,
            "text": user_msg,
            "time": timestamp
        })

        bot_reply = get_gpt_response(user_msg)
        messages.append({
            "sender": "Bot",
            "text": bot_reply,
            "time": timestamp
        })

        save_messages(messages)
        st.session_state["refresh"] = True
        st.stop()

    st.markdown("---")
    chat_data = "\n".join([f"{m['time']} - {m['sender']}: {m['text']}" for m in messages])
    st.download_button("📥 Download Chat", data=chat_data, file_name="chat.txt")
