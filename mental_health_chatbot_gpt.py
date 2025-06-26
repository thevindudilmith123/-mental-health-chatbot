import streamlit as st
from textblob import TextBlob
import hashlib
import json
import os
import datetime

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
        return "That's wonderful to hear! Keep the positivity flowing 😊"
    elif mood == "negative":
        return "I'm sorry you're feeling this way. You're not alone 💙 Take a deep breath and be kind to yourself."
    else:
        return "Thanks for sharing. I'm here if you want to talk more 💬"

# -----------------------
# Streamlit App
# -----------------------

st.set_page_config(page_title="Mental Health Chatbot", layout="centered")

st.title("🧠 AI Mental Health Chatbot ")

# Sidebar Navigation
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("🔐 Menu", menu)

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Register Page
if choice == "Register":
    st.subheader("📝 Create New Account")
    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")
    if st.button("Register"):
        if register_user(new_user, new_pass):
            st.success("✅ Account created! You can now log in.")
        else:
            st.warning("⚠️ Username already exists. Try a different one.")

# Login Page
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

# Chatbot Page (Only if Logged In)
if st.session_state.logged_in:
    st.markdown("## 💬 How are you feeling today?")
    user_input = st.text_input("Type your message below")

    if user_input:
        reply = generate_response(user_input)
        st.markdown(f"**Bot:** {reply}")

        with open("chat_log_basic.txt", "a") as f:
            f.write(f"{datetime.datetime.now()} | {st.session_state.username} | User: {user_input} | Bot: {reply}\n")

    st.markdown("---")
    st.markdown("📘 *This chatbot is for emotional support only. Not a medical tool.*")

