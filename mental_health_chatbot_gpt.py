import streamlit as st
from textblob import TextBlob
import datetime

# App UI
st.set_page_config(page_title="AI Mental Wellness Chatbot", layout="centered")
st.title("🧠 AI Mental Health Chatbot (No API)")
st.caption("This chatbot gives supportive messages based on your feelings.")

# User Input
user_input = st.text_input("💬 How are you feeling today?")

# Sentiment Detector
def get_sentiment(text):
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    if polarity > 0.3:
        return "positive"
    elif polarity < -0.3:
        return "negative"
    else:
        return "neutral"

# Bot Logic
def generate_response(text):
    mood = get_sentiment(text)
    if mood == "positive":
        return "That's wonderful to hear! Keep the positive vibes going 😊"
    elif mood == "negative":
        return "I'm really sorry you're feeling this way. It's okay to take a break. You're not alone 💙"
    else:
        return "Thank you for sharing. I'm here if you want to talk more 💬"

# Show Result
if user_input:
    response = generate_response(user_input)
    st.markdown(f"**Bot:** {response}")

    with open("chat_log_basic.txt", "a") as f:
        f.write(f"{datetime.datetime.now()} | User: {user_input} | Bot: {response}\n")

# Footer
st.markdown("---")
st.markdown("📘 *Note: This chatbot is for emotional support only and not a medical tool.*")
