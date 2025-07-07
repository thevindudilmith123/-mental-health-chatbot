import streamlit as st
import requests
import datetime

# Page setup
st.set_page_config(page_title="Together AI Chatbot", layout="centered")
st.title("🧠 Together.ai Mental Health Chatbot")
st.write("Free, open-source LLM powered by Together.ai. No OpenAI or Gemini needed.")

# API Key input
if "together_api_key" not in st.session_state:
    st.session_state.together_api_key = "f9883b98aa0011d27802548ea685a4b7756fa7a513043134fdd37cbe650590e1"

st.session_state.together_api_key = st.sidebar.text_input(
    "🔐 Together.ai API Key", value=st.session_state.together_api_key, type="password"
)

# Model selection (default is Mistral)
model = st.sidebar.selectbox("🤖 Choose a model", [
    "mistralai/Mistral-7B-Instruct-v0.1",
    "meta-llama/Llama-2-7b-chat-hf",
    "NousResearch/Hermes-2-Pro-Mistral-7B"
])

# Message history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": "You are a supportive mental health assistant."}]

# Display chat history
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# User input
user_input = st.chat_input("Say something...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Together API call
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

            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

# Chat download
if len(st.session_state.messages) > 1:
    st.download_button(
        "📥 Download Chat History",
        data="\n".join([f"{m['role']}: {m['content']}" for m in st.session_state.messages[1:]]),
        file_name="chat_history.txt"
    )
