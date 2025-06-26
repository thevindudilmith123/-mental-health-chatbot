import streamlit as st
from textblob import TextBlob
import hashlib
import json
import os
import datetime

# -----------------------
# Session State Setup (fixes NameError)
# -----------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# -----------------------
# Page Setup
# -----------------------
st.set_page_config(page_title="AI Mental Health Chatbot", layout="centered")
st.title("🧠 AI Mental Health Chatbot (No API Needed)")

# -----------------------
# User Handling Functions
# -----------------------
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as f:
            return json.load(f)
    else:
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

# -----------------------
# Chatbot Functions
# -----------------------
def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.3:
        return "positive"
    elif polarity < -0.3:
        return "negative"
    else:
        return "neutral"

def generate_response(text):
    mood = get_sentiment(text)
    if mood == "positive":
        return "That's wonderful to hear! 😊 Keep spreading the good vibes!"
    elif mood == "negative":
        return "I'm really sorry you're feeling this way. You're not alone 💙 Take a deep breath and be kind to yourself."
    else:
        return "Thank you for sharing. I'm here if you want to talk more 💬"

# -----------------------
# UI Sidebar Menu
# -----------------------
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("🔐 Menu", menu)

# -----------------------
# Registration Section
# -----------------------
if choice == "Register":
    st.subheader("📝 Create New Account")
    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")
    if st.button("Register"):
        if register_user(new_user, new_pass):
            st.success("✅ Account created! You can now log in.")
        else:
            st.warning("⚠️ Username already exists. Try a different one.")

# -----------------------
# Login Section
# -----------------------
elif choice == "Login":
    st.subheader("🔑 Login to Your Account")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if login_user(username, password):
            st.success(f"✅ Welcome, {username}!")
            st.session_state.logged_in = True
            st.session_state.username = username
        else:
            st.error("❌ Incorrect username or password")

# -----------------------
# Chat Section (Visible Only After Login)
# -----------------------
if st.session_state.logged_in:
    st.markdown(f"### 💬 Hello **{st.session_state.username}**, how are you feeling today?")

    # Chat input form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        bot_reply = generate_response(user_input)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Store both messages
        st.session_state.chat_history.append({
            "role": "user",
            "text": user_input,
            "time": timestamp
        })
        st.session_state.chat_history.append({
            "role": "bot",
            "text": bot_reply,
            "time": timestamp
        })

        # Save to local chat log file
        with open("chat_log_basic.txt", "a") as f:
            f.write(f"{timestamp} | {st.session_state.username} | User: {user_input} | Bot: {bot_reply}\n")

    # Show chat history in styled boxes
    st.markdown("### 🗨️ Chat History")
    for msg in st.session_state.chat_history:
        role_icon = "🧍‍♂️" if msg["role"] == "user" else "🤖"
        bg_color = "#e6f7ff" if msg["role"] == "user" else "#f1f0f0"
        st.markdown(
            f"<div style='background-color:{bg_color};padding:10px;border-radius:10px;margin-bottom:5px'>"
            f"<strong>{role_icon} {msg['role'].capitalize()} [{msg['time']}]:</strong><br>{msg['text']}</div>",
            unsafe_allow_html=True
        )

    # Download chat history
    download_text = "\n".join(
        [f"{m['time']} - {m['role'].capitalize()}: {m['text']}" for m in st.session_state.chat_history]
    )
    st.download_button("📥 Download Chat as .txt", data=download_text, file_name="chat_history.txt")

    st.markdown("---")
    st.markdown("📘 *This chatbot is for emotional support only. Not a medical tool.*")
