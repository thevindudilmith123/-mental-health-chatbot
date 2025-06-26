
import streamlit as st
import openai
import datetime

# --- Streamlit page config ---
st.set_page_config(page_title="🧠 AI Mental Health Chatbot", layout="centered")
st.title("🧠 AI Mental Health Chatbot")
st.caption("This chatbot offers supportive, empathetic conversations using OpenAI's GPT. Not a substitute for medical care.")

# --- API Key Entry ---
openai_api_key = st.text_input("🔐 Enter your OpenAI API Key", type="password")

# --- User Input ---
user_message = st.text_input("💬 How are you feeling today?")

# --- GPT Response Function ---
def get_gpt_response(prompt):
    openai.api_key = openai_api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a kind, empathetic mental health support assistant. You help users feel calm and supported, without diagnosing."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"⚠️ Error: {e}"

# --- Display Response ---
if openai_api_key and user_message:
    reply = get_gpt_response(user_message)
    st.markdown(f"**Bot:** {reply}")

    # Optional: Save chat log
    with open("chat_log_gpt.txt", "a", encoding="utf-8") as log_file:
        log_file.write(f"{datetime.datetime.now()} | User: {user_message} | Bot: {reply}\n")

# --- Footer ---
st.markdown("---")
st.markdown("📘 *Note: This chatbot does not offer professional medical advice. If you're in crisis, please seek professional help.*")
