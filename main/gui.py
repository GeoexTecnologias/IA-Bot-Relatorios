import streamlit as st
from ai_model import generate_query_ai
import pandas as pd
import time
import numpy as np
debug_css_path = 'IA-Bot-Relatorios/main/styles/style.css'
css_path = 'styles/style.css'
with open(css_path) as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

st.title('_Geoex_ :green[AI] 🧠')


if "messages" not in st.session_state:
    st.session_state.messages = []

st.chat_message("assistant").markdown(
    'Olá! Eu sou o _Geoex_ :green[AI], um assistente virtual que pode te ajudar a encontrar informações dados do seu interesse! Como posso te ajudar hoje?')

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
