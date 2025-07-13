import streamlit as st
import requests
import time
import hashlib
import json
import os
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="Chatbot | Sinhala-English", layout="wide")

# 🌐 Language Toggle
lang = st.sidebar.selectbox("🌐 Language", ["English", "සිංහල"])

# UI Labels
labels = {
    "English": {
        "login": "Login", "register": "Register", "username": "Username", "password": "Password",
        "mood": "🧠 Mood", "personalities": ["Therapist", "Motivator", "Coach", "Friend"],
        "moods": ["🙂 Happy", "😔 Sad", "😠 Angry", "😰 Anxious", "💬 Just Chat"],
        "prompts": {
            "🙂 Happy": "I'm feeling 😊 happy today!",
            "😔 Sad": "I'm feeling 😢 a bit down.",
            "😠 Angry": "I'm feeling 😠 frustrated.",
            "😰 Anxious": "I'm feeling 😰 anxious lately.",
            "💬 Just Chat": "Let's chat about anything."
        },
        "input": "Type here...", "hello": "Hello", "export": "📄 Export PDF", "mood_stats": "📈 View Mood Stats"
    },
    "සිංහල": {
        "login": "පිවිසෙන්න", "register": "ලියාපදිංචි වන්න", "username": "පරිශීලක නාමය", "password": "මුරපදය",
        "mood": "🧠 මනෝභාවය", "personalities": ["මනෝවෙදක", "ප්‍රේරකයා", "පුහුණුකරු", "මිතුරා"],
        "moods": ["🙂 සතුටුයි", "😔 දුක්වෙයි", "😠 කෝපයි", "😰 කනස්සල්ලෙන්", "💬 සාමාන්‍ය කතාබසය"],
        "prompts": {
            "🙂 සතුටුයි": "මම අද 😊 සතුටින් සිටිනවා.",
            "😔 දුක්වෙයි": "මම අද 😢 දුකින් පිරී ඇත.",
            "😠 කෝපයි": "මම අද 😠 කෝපයෙන් පිරී ඇත.",
            "😰 කනස්සල්ලෙන්": "මට අද 😰 කනස්සල්ලක් තියෙනවා.",
            "💬 සාමාන්‍ය කතාබසය": "ඕනෑම දෙයක් ගැන කතා කරමු."
        },
        "input": "ඔබට කිව යුතු දේ මෙහි ටයිප් කරන්න...", "hello": "හෙලෝ",
        "export": "📄 PDF ලෙස සුරකින්න", "mood_stats": "📈 මනෝභාව ගණන්"
    }
}
L = labels[lang]

# 🔐 API Key (REPLACE WITH YOURS)
api_key = "Bearer f9883b98aa0011d27802548ea685a4b7756fa7a513043134fdd37cbe650590e1"
model = "mistralai/Mistral-7B-Instruct-v0.1"

# Login / Register
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

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []
if "moods" not in st.session_state:
    st.session_state.moods = []

# Sidebar Login/Register
st.sidebar.title("🔐 " + ("Access" if lang == "English" else "පරිශීලක පිවිසුම"))
mode = st.sidebar.radio("Choose", [L["login"], L["register"]])
uname = st.sidebar.text_input(L["username"])
pword = st.sidebar.text_input(L["password"], type="password")
if mode == L["login"]:
    if st.sidebar.button(L["login"]):
        if login_user(uname, pword):
            st.session_state.logged_in = True
            st.session_state.username = uname
            st.success("✅ Logged in!")
        else:
            st.error("❌ Invalid login.")
else:
    if st.sidebar.button(L["register"]):
        if register_user(uname, pword):
            st.success("✅ Registered.")
        else:
            st.warning("⚠️ Username exists.")

if not st.session_state.logged_in:
    st.stop()

# Personality system prompt
persona = st.selectbox("🤖 " + ("Bot Personality" if lang == "English" else "චරිතය"), L["personalities"])
persona_prompts = {
    "Therapist": "You are a caring mental health therapist.",
    "මනෝවෙදක": "ඔබ මනෝසංවර්ධනයට සහය වන්නාවූ වෛද්‍යවරයෙකි.",
    "Motivator": "You are a motivational coach.",
    "ප්‍රේරකයා": "ඔබ උද්යෝගී චරිතයකි.",
    "Coach": "You are a practical life coach.",
    "පුහුණුකරු": "ඔබ උපදෙස් සහ සහය දෙන්නෙකුයි.",
    "Friend": "You are a friendly companion.",
    "මිතුරා": "ඔබ හිතවත් මිතුරෙකි."
}
if not any(m['role'] == 'system' for m in st.session_state.messages):
    st.session_state.messages.append({
        "role": "system",
        "content": persona_prompts.get(persona, "You are helpful.") + " කරුණාකර හැම විටම සිංහලෙන් පිළිතුරු දක්වන්න."
    })

# Mood
st.markdown(f"### 👋 {L['hello']}, **{st.session_state.username}**")
mood = st.radio(L["mood"], L["moods"], horizontal=True)
prompt = L["prompts"][mood]
if mood != L["moods"][-1]:
    st.session_state.moods.append(mood)

# Show previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Chat input
user_input = st.chat_input(L["input"] if mood == L["moods"][-1] else prompt)
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..." if lang == "English" else "සිතමින්..."):
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

# Save chat to file
os.makedirs("user_logs", exist_ok=True)
with open(f"user_logs/{st.session_state.username}_chat.txt", "w") as f:
    for m in st.session_state.messages:
        f.write(f"{m['role']}: {m['content']}\n")

# Export PDF
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
    if st.button(L["export"]):
        file = export_pdf()
        with open(file, "rb") as f:
            st.download_button(L["export"], f, file_name=file)
with col2:
    if st.button(L["mood_stats"]) and st.session_state.moods:
        df = pd.DataFrame(st.session_state.moods, columns=["Mood"])
        mood_count = df["Mood"].value_counts()
        st.bar_chart(mood_count)
