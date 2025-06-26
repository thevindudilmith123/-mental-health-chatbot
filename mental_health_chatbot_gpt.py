import time  # At the top of your file

# Chat UI after login
if st.session_state.logged_in:
    st.markdown(f"### 💬 Hello **{st.session_state.username}**, how are you feeling today?")

    # Chat input with form
    with st.form("chat_form", clear_on_submit=True):
        user_input = st.text_input("Type your message")
        submitted = st.form_submit_button("Send")

    if submitted and user_input:
        bot_reply = generate_response(user_input)
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Save both user and bot messages
        st.session_state.chat_history.append({
            "role": "user",
            "text": user_input,
            "time": timestamp
        })
        st.session_state.chat_history.append({
            "role": "bot",
            "text": bot_reply,
            "time": timestamp
        })

        # Also write to file
        with open("chat_log_basic.txt", "a") as f:
            f.write(f"{timestamp} | {st.session_state.username} | User: {user_input} | Bot: {bot_reply}\n")

    # Display chat bubbles
    st.markdown("### 🗨️ Chat History")
    for msg in st.session_state.chat_history:
        if msg["role"] == "user":
            st.markdown(
                f"<div style='background-color:#e6f7ff;padding:10px;border-radius:10px;margin-bottom:5px'><strong>🧍‍♂️ You [{msg['time']}]:</strong><br>{msg['text']}</div>",
                unsafe_allow_html=True)
        else:
            st.markdown(
                f"<div style='background-color:#f1f0f0;padding:10px;border-radius:10px;margin-bottom:10px'><strong>🤖 Bot [{msg['time']}]:</strong><br>{msg['text']}</div>",
                unsafe_allow_html=True)

    # Download conversation button
    if st.download_button("📥 Download Chat as .txt", data="\n".join(
        [f"{m['time']} - {m['role'].capitalize()}: {m['text']}" for m in st.session_state.chat_history]),
        file_name="chat_history.txt"):
        st.success("Downloaded successfully!")

    st.markdown("---")
    st.markdown("📘 *This chatbot is for emotional support only. Not a medical tool.*")
