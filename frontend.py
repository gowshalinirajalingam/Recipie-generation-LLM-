import streamlit as st
import requests

# Backend URL
BACKEND_URL = "http://127.0.0.1:8000/generate_recipe/"

st.title("RecipeMate: Conversational Recipe Bot")

# Initialize session state for conversation history
if "conversation" not in st.session_state:
    st.session_state.conversation = []

# Chat Interface
user_input = st.text_input("Your message:")
if st.button("Send"):
    if user_input:
        print("user_input_FE:", user_input)
        print("conv history:", st.session_state.conversation)
        st.session_state.conversation.append({"role": "user", "content": user_input})
        response = requests.post(
            BACKEND_URL,
            json={"user_input": user_input, "conversation_history": st.session_state.conversation},

        )
        if response.status_code == 200:
            bot_reply = response.json()["response"]
            st.session_state.conversation.append({"role": "assistant", "content": bot_reply})
            # st.write(f"**RecipeMate**: {bot_reply}")
        else:
            st.error("Error in backend processing!")
    else:
        st.warning("Please enter a message.")

# Display conversation history
st.write("### Conversation History")
for message in st.session_state.conversation:
    if message["role"] == "user":
        st.write(f"**You**: {message['content']}")
    else:
        st.write(f"**RecipeMate**: {message['content']}")
