import streamlit as st
from ai_model import generate_query_ai
import pandas as pd
import time
import numpy as np

st.title("Geoex AI")


if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como posso te ajudar?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = generate_query_ai(
        "geoex-sql-embeddings", prompt, st.session_state.messages)

    if isinstance(response, pd.DataFrame):
        with st.status("Buscando os dados..."):
            st.write("Buscando dados...")
            time.sleep(2)
            st.write("Dados Encontrados.")
            time.sleep(2)
            st.write("Carregando seus dados...")
            time.sleep(2)
        with st.chat_message("assistant"):
            st.dataframe(response)
    else:
        with st.status("Pensando..."):
            time.sleep(6)

        with st.chat_message("assistant"):
            def stream_data():
                for word in response.split(" "):
                    yield word + " "
                    time.sleep(0.02)
            st.write_stream(stream_data)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
