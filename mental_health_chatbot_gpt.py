import streamlit as st
import requests
import time

# Page setup
st.set_page_config(page_title="Together AI Chatbot", layout="centered")
st.title("🧠 Together.ai Mental Health Chatbot")
st.write("Free, open-source LLM powered by Together.ai. No OpenAI or Gemini needed.")

# API Key input
if "together_api_key" not in st.session_state:
    st.session_state.together_api_key = ""

st.session_state.together_api_key = st.sidebar.text_input(
    "🔐 Together.ai API Key", value=st.session_state.together_api_key, type="password"
)

# Model selection
model = st.sidebar.selectbox("🤖 Choose a model", [
    "mistralai/Mistral-7B-Instruct-v0.1",
    "meta-llama/Llama-2-7b-chat-hf",
    "NousResearch/Hermes-2-Pro-Mistral-7B"
])

# Session history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a kind mental health assistant."}]

# Display previous messages
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Mood Buttons
st.subheader("🧠 Choose a Mood")
mood = st.radio("How are you feeling?", ["🙂 Happy", "😔 Sad", "😠 Angry", "😰 Anxious", "💬 Just Chat"], horizontal=True)
mood_prompts = {
    "🙂 Happy": "I'm feeling happy today!",
    "😔 Sad": "I'm feeling really sad lately.",
    "😠 Angry": "I'm frustrated about something.",
    "😰 Anxious": "I'm struggling with anxiety right now.",
    "💬 Just Chat": "Let's talk about something."
}

selected_prompt = mood_prompts[mood] if mood else None

# Manual input or mood prompt
user_input = st.chat_input("Type something..." if mood == "💬 Just Chat" else f"{selected_prompt}")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call Together.ai API
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            headers = {
                "Authorization": f"Bearer {st.session_state.together_api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": model,
                "max_tokens": 200,
                "temperature": 0.7,
                "messages": st.session_state.messages
            }
            res = requests.post(
                "https://api.together.xyz/v1/chat/completions",
                headers=headers,
                json=payload
            )
            if res.status_code == 200:
                reply = res.json()["choices"][0]["message"]["content"]
            else:
                reply = f"❌ Error: {res.status_code} - {res.text}"

            # Typing animation
            full_reply = ""
            msg_box = st.empty()
            for char in reply:
                full_reply += char
                msg_box.markdown(full_reply + "▌")
                time.sleep(0.015)
            msg_box.markdown(full_reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

# Download chat
if len(st.session_state.messages) > 1:
    st.download_button(
        "📥 Download Chat History",
        data="\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[1:]]),
        file_name="chat_history.txt"
    )
