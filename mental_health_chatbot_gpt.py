import streamlit as st
import requests
import time
import hashlib
import json
import os
import pandas as pd
from fpdf import FPDF

# Config
st.set_page_config(page_title="Together AI Chatbot", layout="wide")
theme = st.sidebar.radio("🌗 Theme", ["Light", "Dark"])
if theme == "Dark":
    st.markdown("<style>body { background-color: #1e1e1e; color: white; }</style>", unsafe_allow_html=True)

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
if "moods" not in st.session_state:
    st.session_state.moods = []

# Auth
st.sidebar.title("🔐 Access")
auth_mode = st.sidebar.radio("Choose", ["Login", "Register"])
uname = st.sidebar.text_input("Username")
pword = st.sidebar.text_input("Password", type="password")
if auth_mode == "Login":
    if st.sidebar.button("Login"):
        if login_user(uname, pword):
            st.session_state.logged_in = True
            st.session_state.username = uname
            st.success("✅ Logged in!")
        else:
            st.error("❌ Invalid username or password.")
else:
    if st.sidebar.button("Register"):
        if register_user(uname, pword):
            st.success("✅ Registered successfully.")
        else:
            st.warning("⚠️ Username already exists.")

if not st.session_state.logged_in:
    st.stop()

# ✅ Hardcoded API Key
api_key = "Bearer f9883b98aa0011d27802548ea685a4b7756fa7a513043134fdd37cbe650590e1"  # ← Replace this with your real API key
model = "mistralai/Mistral-7B-Instruct-v0.1"

# Personality switcher
personality = st.selectbox("🤖 Bot Personality", ["Therapist", "Motivator", "Coach", "Friend"])
intro_messages = {
    "Therapist": "You are a caring mental health therapist. Provide supportive, calm, and reflective responses.",
    "Motivator": "You are a high-energy motivational coach. Be positive, encouraging, and goal-focused.",
    "Coach": "You are a practical personal coach. Give advice and ask helpful questions.",
    "Friend": "You are a supportive best friend. Talk informally and warmly."
}

if not any(m['role'] == 'system' for m in st.session_state.messages):
    st.session_state.messages.append({"role": "system", "content": intro_messages[personality]})

# Mood input
st.markdown(f"### 👋 Hello, **{st.session_state.username}**")
mood = st.radio("🧠 Mood", ["🙂 Happy", "😔 Sad", "😠 Angry", "😰 Anxious", "💬 Just Chat"], horizontal=True)
mood_prompts = {
    "🙂 Happy": "I'm feeling 😊 happy today!",
    "😔 Sad": "I'm feeling 😢 a bit down.",
    "😠 Angry": "I'm feeling 😠 frustrated.",
    "😰 Anxious": "I'm feeling 😰 anxious lately.",
    "💬 Just Chat": "Let's chat about anything."
}
default_prompt = mood_prompts[mood]
if mood != "💬 Just Chat":
    st.session_state.moods.append(mood)

# Show past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input("Type here..." if mood == "💬 Just Chat" else default_prompt)
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # GPT bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            headers = {
                "Authorization": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "max_tokens": 250,
                "temperature": 0.7,
                "messages": st.session_state.messages
            }
            res = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload)
            if res.status_code == 200:
                reply = res.json()["choices"][0]["message"]["content"]
            else:
                reply = f"❌ Error: {res.status_code} - {res.text}"

            full = ""
            box = st.empty()
            for char in reply:
                full += char
                box.markdown(full + "▌")
                time.sleep(0.01)
            box.markdown(full)
            st.session_state.messages.append({"role": "assistant", "content": reply})

# Save user chat
os.makedirs("user_logs", exist_ok=True)
with open(f"user_logs/{st.session_state.username}_chat.txt", "w") as f:
    for m in st.session_state.messages:
        f.write(f"{m['role']}: {m['content']}\n")

# Export to PDF
def export_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Chat History", ln=True, align="C")
    pdf.ln(10)
    for m in st.session_state.messages:
        who = "You" if m["role"] == "user" else "Bot"
        pdf.multi_cell(0, 10, txt=f"{who}: {m['content']}")
    filename = f"{st.session_state.username}_chat.pdf"
    pdf.output(filename)
    return filename

col1, col2 = st.columns(2)
with col1:
    if st.button("📄 Export PDF"):
        file = export_pdf()
        with open(file, "rb") as f:
            st.download_button("Download PDF", f, file_name=file)
with col2:
    if st.button("📈 View Mood Stats") and st.session_state.moods:
        df = pd.DataFrame(st.session_state.moods, columns=["Mood"])
        mood_count = df["Mood"].value_counts()
        st.bar_chart(mood_count)
