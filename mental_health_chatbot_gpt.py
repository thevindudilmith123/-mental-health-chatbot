import streamlit as st
import hashlib
import json
import os
import datetime
import requests

# ---------------------------
# 🔐 Gemini REST Setup
# ---------------------------
if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = "AIzaSyBMmwmAQ0Y4y_1mpMXlGouy_O6mgSsayy4"

st.session_state.gemini_api_key = st.sidebar.text_input(
    "🔐 Gemini API Key", value=st.session_state.gemini_api_key, type="password"
)

def call_gemini_api(prompt, key):
    if not key:
        return "❗ No API key provided."

    try:
        url = "https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent"
        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": prompt}]
                }
            ]
        }
        response = requests.post(f"{url}?key={key}", headers=headers, json=data)
        result = response.json()

        if "candidates" in result:
            return result["candidates"][0]["content"]["parts"][0]["text"]
        elif "error" in result:
            return f"❌ Gemini Error: {result['error'].get('message', 'Unknown error')}"
        else:
            return "⚠️ Unexpected response from Gemini API."
    except Exception as e:
        return f"⚠️ Exception: {e}"

# ---------------------------
# 🔐 User Auth & UI Setup
# ---------------------------
st.set_page_config(page_title="Gemini REST Chat", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "just_sent" not in st.session_state:
    st.session_state.just_sent = False

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

def load_messages():
    if os.path.exists("messages.json"):
        with open("messages.json", "r") as f:
            return json.load(f)
    return []

def save_messages(messages):
    with open("messages.json", "w") as f:
        json.dump(messages, f)

st.sidebar.title("🌗 Theme")
dark_mode = st.sidebar.checkbox("Dark Mode")
if dark_mode:
    st.markdown("""
    <style>
    body { background-color: #121212; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🤖 Gemini REST Chatbot")
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("🔐 Menu", menu)

if choice == "Register":
    st.subheader("📝 Register")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    if st.button("Register"):
        if register_user(new_user, new_pass):
            st.success("✅ Registered successfully!")
        else:
            st.warning("⚠️ Username exists.")
elif choice == "Login":
    st.subheader("🔑 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Welcome, {username}!")
        else:
            st.error("❌ Invalid credentials.")

if st.session_state.logged_in:
    st.markdown(f"### 👋 Hello, **{st.session_state.username}**")
    messages = load_messages()

    if st.session_state.just_sent:
        messages = load_messages()
        st.session_state.just_sent = False

    for msg in messages:
        is_you = msg["sender"] == st.session_state.username
        align = "right" if is_you else "left"
        bg = "#cce5ff" if is_you else "#f1f0f0"
        icon = "🧍‍♂️" if is_you else "🤖"

        st.markdown(f"""
        <div style='text-align:{align}; margin-bottom:10px;'>
            <div style='display:inline-block; background:{bg}; padding:10px; border-radius:10px; max-width:80%;'>
                <b>{icon} {msg['sender']}</b> <small style='opacity:0.6'>[{msg['time']}]</small><br>
                {msg['text']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.form("send_form", clear_on_submit=True):
        user_msg = st.text_input("Type your message")
        send = st.form_submit_button("Send")

    if send and user_msg:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        messages.append({"sender": st.session_state.username, "text": user_msg, "time": timestamp})

        bot_reply = call_gemini_api(user_msg, st.session_state.gemini_api_key)
        messages.append({"sender": "Bot", "text": bot_reply, "time": timestamp})

        save_messages(messages)
        st.session_state.just_sent = True

    st.markdown("---")
    st.download_button(
        "📥 Download Chat",
        data="\n".join([f"{m['time']} - {m['sender']}: {m['text']}" for m in messages]),
        file_name="chat_history.txt"
    )
