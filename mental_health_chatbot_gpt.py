import streamlit as st
import openai
import datetime

st.set_page_config(page_title="AI Mental Health Chatbot", layout="centered")
st.title("🧠 GPT Mental Health Chatbot")
st.caption("This chatbot is a supportive tool, not a medical diagnosis system.")

openai_api_key = st.text_input("🔐 Enter your OpenAI API Key", type="password")
user_message = st.text_input("💬 How are you feeling today?")

def get_gpt_response(prompt):
    openai.api_key = openai_api_key
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a kind and caring mental wellness assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=150,
        )
        return response.choices[0].message['content'].strip()
    except Exception as e:
        return f"⚠️ Error: {e}"

if openai_api_key and user_message:
    reply = get_gpt_response(user_message)
    st.markdown(f"**Bot:** {reply}")
    with open("chat_log_gpt.txt", "a") as log:
        log.write(f"{datetime.datetime.now()} | User: {user_message} | Bot: {reply}\n")

st.markdown("---")
st.markdown("📘 *Remember: This is not a replacement for professional mental health support.*")
