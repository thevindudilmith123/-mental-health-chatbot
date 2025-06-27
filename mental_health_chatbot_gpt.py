import streamlit as st
import hashlib
import json
import os
import datetime
import openai

# ---------------------------
# 🧠 GPT Setup
# ---------------------------
openai_api_key = st.sidebar.text_input("🔐 OpenAI API Key", type="password")

def get_gpt_response(prompt):
    if not openai_api_key:
        return "❗ No API key provided."
    openai.api_key = openai_api_key
    try:
        res = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Or gpt-4
            messages=[
                {"role": "system", "content": "You are a supportive and empathetic mental health assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return res.choices[0].message["content"].strip()
    except Exception as e:
        return f"⚠️ Error: {e}"

# ---------------------------
# 🔐 User Authentication
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
# 💬 Message Functions
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
# 🌗 Theme & UI Setup
# ---------------------------
st.set_page_config(page_title="GPT Chat", layout="centered")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

st.sidebar.title("🌗 Theme")
dark_mode = st.sidebar.checkbox("Dark Mode")
if dark_mode:
    st.markdown("""
        <style>
        body { background-color: #121212; color: white; }
        .bubble { background-color: #2f2f2f; }
        </style>
    """, unsafe_allow_html=True)

# ---------------------------
# 🔐 Auth Section
# ---------------------------
st.title("🤖 GPT Mental Health Chat")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("🔐 Menu", menu)

if choice == "Register":
    st.subheader("📝 Create Account")
    new_user = st.text_input("Username")
    new_pass = st.text_input("Password", type="password")
    if st.button("Register"):
        if register_user(new_user, new_pass):
            st.success("✅ Account created! Now log in.")
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
            st.error("❌ Invalid credentials.")

# ---------------------------
# 💬 Chat Interface
# ---------------------------
if st.session_state.logged_in:
    messages = load_messages()

    st.markdown(f"### 👋 Welcome, **{st.session_state.username}**")

    # Show chat
    for msg in messages:
        is_you = msg["sender"] == st.session_state.username
        align = "right" if is_you else "left"
        bg = "#cce5ff" if is_you else "#f1f0f0"
        icon = "🧍‍♂️" if is_you else ("🤖" if msg["sender"] == "Bot" else "👤")

        st.markdown(f"""
        <div style='text-align:{align}; margin-bottom:10px;'>
            <div style='display:inline-block; background:{bg}; padding:10px; border-radius:10px; max-width:80%;'>
                <b>{icon} {msg['sender']}</b> <small style='opacity:0.6'>[{msg['time']}]</small><br>
                {msg['text']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Input box
    with st.form("send_form", clear_on_submit=True):
        user_msg = st.text_input("Type your message")
        send = st.form_submit_button("Send")

    if send and user_msg:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        messages.append({"sender": st.session_state.username, "text": user_msg, "time": timestamp})

        # Bot reply (GPT)
        bot_reply = get_gpt_response(user_msg)
        messages.append({"sender": "Bot", "text": bot_reply, "time": timestamp})

        save_messages(messages)
        st.success("Message sent! Refresh to view reply.")
