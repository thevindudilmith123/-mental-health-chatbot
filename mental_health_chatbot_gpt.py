
import streamlit as st
import requests
import json
import hashlib
import os
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="Sinhala-English Chatbot", layout="wide")
lang = st.sidebar.selectbox("🌐 Language", ["English", "සිංහල"])

labels = {
    "English": {
        "login": "Login", "register": "Register", "username": "Username", "password": "Password",
        "hello": "Hello", "mood": "Mood", "export": "Export PDF", "mood_stats": "Mood Stats",
        "moods": ["🙂 Happy", "😔 Sad", "😠 Angry", "😰 Anxious", "💬 Just Chat"],
        "input": "Type your message here...",
        "personalities": ["Therapist", "Motivator", "Coach", "Friend"]
    },
    "සිංහල": {
        "login": "පිවිසෙන්න", "register": "ලියාපදිංචි වන්න", "username": "පරිශීලක නාමය", "password": "මුරපදය",
        "hello": "හෙලෝ", "mood": "මනෝභාවය", "export": "PDF එකක් ලෙස සුරකින්න", "mood_stats": "මනෝභාව ගණන්",
        "moods": ["🙂 සතුටුයි", "😔 දුක්වෙයි", "😠 කෝපයි", "😰 කනස්සල්ලෙන්", "💬 සාමාන්‍ය කතාබසය"],
        "input": "ඔබේ පණිවිඩය මෙහි ටයිප් කරන්න...",
        "personalities": ["මනෝවෙදක", "ප්‍රේරකයා", "පුහුණුකරු", "මිතුරා"]
    }
}
L = labels[lang]

# API key (hardcoded or use sidebar input)
api_key = "Bearer f9883b98aa0011d27802548ea685a4b7756fa7a513043134fdd37cbe650590e1"
model = "mistralai/Mistral-7B-Instruct-v0.1"

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def load_users():
    try:
        with open("users.json", "r") as f:
            return json.load(f)
    except:
        return {}

def save_users(users):
    with open("users.json", "w") as f:
        json.dump(users, f)

def login_user(username, password):
    users = load_users()
    return username in users and users[username] == hash_password(password)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False
    users[username] = hash_password(password)
    save_users(users)
    return True

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "messages" not in st.session_state:
    st.session_state.messages = []

# Auth UI
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
    if st.sidebar.button(L["register"]):
        if register_user(uname, pword):
            st.success("✅ Registered")
        else:
            st.warning("⚠️ Username exists")

if not st.session_state.logged_in:
    st.stop()

# Chat setup
st.markdown(f"### 👋 {L['hello']}, **{st.session_state.username}**")
persona = st.selectbox("🤖 Personality", L["personalities"])
if not any(m["role"] == "system" for m in st.session_state.messages):
    st.session_state.messages.append({
        "role": "system",
        "content": f"You are a helpful {persona.lower()} assistant. Respond kindly."
    })

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

user_input = st.chat_input(L["input"])
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            headers = {
                "Authorization": api_key,
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "max_tokens": 256,
                "temperature": 0.7,
                "messages": st.session_state.messages
            }
            res = requests.post("https://api.together.xyz/v1/chat/completions", headers=headers, json=payload)
            if res.status_code == 200:
                reply = res.json()["choices"][0]["message"]["content"]
            else:
                reply = f"Error: {res.status_code} - {res.text}"
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})
