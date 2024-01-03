import time
import streamlit as st 
from assistant import run_assistant

st.subheader("OpenAI Financial Assistant")

with st.chat_message("assistant"):
    st.write("Hello 👋")
    st.write("I'm your financial assistant. How can i help you?")

prompt = st.chat_input("Ask me anything...")

if prompt:
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Processing your prompt..."):
            resultArray = run_assistant(prompt)

            if resultArray:
                for result in resultArray:
                    st.info(result)