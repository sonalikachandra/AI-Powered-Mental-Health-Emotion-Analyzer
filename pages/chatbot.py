import streamlit as st
import openai

# ------------------------- AZURE OPENAI CONFIGURATION -------------------------
AZURE_OPENAI_KEY = "Fj1KPt7grC6bAkNja7daZUstpP8wZTXsV6Zjr2FOxkO7wsBQ5SzQJQQJ99BCACHYHv6XJ3w3AAAAACOGL3Xg"
AZURE_OPENAI_ENDPOINT = "https://ai-aihackthonhub282549186415.openai.azure.com/"
AZURE_GPT4_DEPLOYMENT = "gpt-4"
AZURE_GPT4_API_VERSION = "2025-01-01-preview"

# ------------------------- SETUP AZURE OPENAI CLIENT -------------------------
openai.api_type = "azure"
openai.api_key = "Fj1KPt7grC6bAkNja7daZUstpP8wZTXsV6Zjr2FOxkO7wsBQ5SzQJQQJ99BCACHYHv6XJ3w3AAAAACOGL3Xg"
openai.api_base = "https://ai-aihackthonhub282549186415.openai.azure.com/"  # Example: "https://your-resource-name.openai.azure.com/"
openai.api_version = "2024-02-15-preview"  # Check the correct version in Azure

# ------------------------- STREAMLIT UI -------------------------
st.set_page_config(page_title="🩺 AI Medical Assistant", layout="wide")

st.title("🩺 AI Medical Assistant Chatbot")
st.write("💬 Ask about symptoms, medications, first-aid, or medical advice.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_input = st.chat_input("Ask a medical question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.spinner("Analyzing medical data... ⚕"):
        try:
            response = openai.ChatCompletion.create(
                engine=AZURE_GPT4_DEPLOYMENT,
                messages=[{"role": "system", "content": "Medical assistant AI"}, *st.session_state.messages]
            )
            bot_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

            with st.chat_message("assistant"):
                st.markdown(bot_reply)
        except Exception as e:
            st.error(f"⚠ Error: {e}")