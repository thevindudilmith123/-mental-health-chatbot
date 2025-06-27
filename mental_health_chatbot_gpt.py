import streamlit as st
from textblob import TextBlob
import hashlib
import json
import os
import datetime

# -------------------------------
# ✅ PAGE CONFIG
# -------------------------------
st.set_page_config(page_title="AI Mental Health Chatbot", layout="centered", initial_sidebar_state="expanded")

# -------------------------------
# ✅ SESSION SETUP
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# -------------------------------
# ✅ DARK MODE STYLING
# -------------------------------
def set_theme():
    if st.session_state.theme == "dark":
        st.markdown("""
            <style>
                body { background-color: #121212; color: #f5f5f5; }
                .stTextInput>div>div>input { background-color: #1e1e1e; color: white; }
                .chat-bubble { background-color: #2e2e2e; padding: 10px; border-radius: 10px; margin: 5px 0; }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <style>
                .chat-bubble { background-color: #f0f2f6; padding: 10px; border-radius: 10px; margin: 5px 0; }
            </style>
        """, unsafe_allow_html=True)

# Toggle
st.sidebar.markdown("🌓 **Theme**")
theme_toggle = st.sidebar.checkbox("Dark Mode", value=(st.session_state.theme == "dark"))
st.session_state.theme = "dark" if theme_toggle else "light"
set_theme()

# -------------------------------
# ✅ USER HANDLING
# -------------------------------
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

# -------------------------------
# ✅ CHATBOT LOGIC
# -------------------------------
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
        return "That's wonderful to hear! 😊 Stay positive and keep going strong!"
    elif mood == "negative":
        return "I'm really sorry you're feeling this way. You're not alone 💙 Take a deep breath. Things can get better."
    else:
        return "Thanks for opening up. I'm here for you whenever you need to talk 💬"

# -------------------------------
# ✅ SIDEBAR MENU
# -------------------------------
menu = ["Login", "Register"]
choice = st.sidebar.selectbox("🔐 Menu", menu)

if choice == "Register":
    st.subheader("📝 Create Account")
    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")
    if st.button("Register"):
        if register_user(new_user, new_pass):
            st.success("✅ Account created! Please login.")
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
            st.error("❌ Incorrect username or password.")

# -------------------------------
# ✅ MAIN CHAT UI
# -------------------------------
if st.session_state.logged_in:
    st.markdown(f"### 💬 Hello, **{st.session_state.username}**")

    # Mood Buttons
    st.markdown("**🧠 Choose your mood:**")
    cols = st.columns(4)
    if cols[0].button("😊 Happy"):
        st.session_state.mood_input = "I'm feeling happy today!"
    elif cols[1].button("😔 Sad"):
        st.session_state.mood_input = "I'm feeling sad and a bit down."
    elif cols[2].button("😡 Angry"):
        st.session_state.mood_input = "I'm feeling really angry right now."
    elif cols[3].button("😰 Stressed"):
        st.session_state.mood_input = "I'm feeling anxious and stressed."

    # Input Form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message", value=st.session_state.get("mood_input", ""))
        submitted = st.form_submit_button("Send")
        st.session_state.mood_input = ""  # Clear mood pre-fill

    if submitted and user_input:
        bot_reply = generate_response(user_input)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        st.session_state.chat_history.append({"role": "user", "text": user_input, "time": timestamp})
        st.session_state.chat_history.append({"role": "bot", "text": bot_reply, "time": timestamp})

        # Save to file
        with open("chat_log_basic.txt", "a") as f:
            f.write(f"{timestamp} | {st.session_state.username} | User: {user_input} | Bot: {bot_reply}\n")

    # Chat Display
    st.markdown("### 💬 Your Conversation")
    for msg in st.session_state.chat_history:
        align = "left" if msg["role"] == "bot" else "right"
        name = "🤖 Bot" if msg["role"] == "bot" else "🧍‍♂️ You"
        bubble_style = f"""
            <div style='text-align: {align};'>
                <div class='chat-bubble'>
                    <strong>{name} [{msg["time"]}]</strong><br>{msg["text"]}
                </div>
            </div>
        """
        st.markdown(bubble_style, unsafe_allow_html=True)

    # Download
    text_data = "\n".join([f"{m['time']} - {m['role'].capitalize()}: {m['text']}" for m in st.session_state.chat_history])
    st.download_button("📥 Download Conversation", data=text_data, file_name="chat_history.txt")

    st.markdown("---")
    st.markdown("📘 *This chatbot is here for support, not professional diagnosis.*")
