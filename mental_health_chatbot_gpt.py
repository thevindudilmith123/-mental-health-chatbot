import streamlit as st
from transformers import pipeline

# Title and instructions
st.set_page_config(page_title="Free LLM Chatbot", layout="centered")
st.title("🤖 Open-Source Mental Health Chatbot (Free LLM)")
st.write("This chatbot runs on a free, open-source model via Hugging Face Transformers. No API key required.")

# Load LLM pipeline (uses distilgpt2 for lightweight use)
@st.cache_resource
def load_model():
    return pipeline("text-generation", model="distilgpt2", max_new_tokens=100)

generator = load_model()

# Initialize session history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for entry in st.session_state.messages:
    with st.chat_message(entry["role"]):
        st.markdown(entry["content"])

# Chat input
user_input = st.chat_input("Say something...")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate bot reply
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generator(user_input)[0]["generated_text"]
            cleaned = response[len(user_input):].strip().split("
")[0]
            st.markdown(cleaned)
            st.session_state.messages.append({"role": "assistant", "content": cleaned})
