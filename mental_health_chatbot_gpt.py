import streamlit as st
import requests
import time
import hashlib
import json
from fpdf import FPDF

# Config
st.set_page_config(page_title="Together AI Chatbot", layout="centered")
st.markdown("<style>footer {visibility: hidden;}</style>", unsafe_allow_html=True)

# Auth utils
def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

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

# Session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# Login / Register
st.sidebar.title("🔐 User Access")
auth_option = st.sidebar.radio("Choose option:", ["Login", "Register"])

if not st.session_state.logged_in:
    uname = st.sidebar.text_input("Username")
    pword = st.sidebar.text_input("Password", type="password")
    if auth_option == "Login":
        if st.sidebar.button("Login"):
            if login_user(uname, pword):
                st.session_state.logged_in = True
                st.session_state.username = uname
                st.success("✅ Logged in!")
            else:
                st.error("❌ Invalid login.")
    else:
        if st.sidebar.button("Register"):
            if register_user(uname, pword):
                st.success("✅ Account created. Login now.")
            else:
                st.warning("⚠️ Username already exists.")

# Chat UI
if not st.session_state.logged_in:
    st.stop()

model = "mistralai/Mistral-7B-Instruct-v0.1"

st.title(f"🧠 Hello, {st.session_state.username}")
st.subheader("💬 How are you feeling?")
mood = st.radio("", ["🙂 Happy", "😔 Sad", "😠 Angry", "😰 Anxious", "💬 Just Chat"], horizontal=True)
mood_prompts = {
    "🙂 Happy": "I'm feeling happy today!",
    "😔 Sad": "I'm feeling really sad lately.",
    "😠 Angry": "I'm frustrated about something.",
    "😰 Anxious": "I'm struggling with anxiety right now.",
    "💬 Just Chat": "Let's talk about something."
}
default_prompt = mood_prompts[mood]

# Show messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Input
user_input = st.chat_input("Say something..." if mood == "💬 Just Chat" else default_prompt)
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            headers = {
                "Authorization": "f9883b98aa0011d27802548ea685a4b7756fa7a513043134fdd37cbe650590e1",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "max_tokens": 300,
                "temperature": 0.7,
                "messages": [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
            }
            res = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload)
            if res.status_code == 200:
                reply = res.json()["choices"][0]["message"]["content"]
            else:
                reply = f"❌ Error: {res.status_code} - {res.text}"

            full = ""
            msg_box = st.empty()
            for c in reply:
                full += c
                msg_box.markdown(full + "▌")
                time.sleep(0.01)
            msg_box.markdown(full)
            st.session_state.messages.append({"role": "assistant", "content": reply})
