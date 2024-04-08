import time
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from langchain_community.llms import Ollama
import os
from database.db import projetos_carteiras
from langchain_openai import ChatOpenAI, OpenAI
from langchain_experimental.agents.agent_toolkits import create_csv_agent, create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType


load_dotenv()

st.set_page_config(page_title="Projetos e Carteiras", page_icon="🧠")

css_path = 'styles/style.css'
with open(css_path) as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

prompt_template = """
Seu nome é Geoex AI, voce é um Assistente baseado em IA que analisa dados sobre projetos e carteiras de obras. 
Caso nao consiga executar o codigo, informe ao usuário que reformule a pergunta.
Voce pode retornar dados em formato de tabela 
Caso o usuário nao especifique data use o ano atual.
Responda: {prompt}
"""
agent = create_pandas_dataframe_agent(
    ChatOpenAI(temperature=0.4, model="gpt-3.5-turbo"),
    projetos_carteiras(),
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
)
tables = ['Projetos', 'Carteiras', 'Previsao',
          'Situação', 'VlProjeto(valor do projeto)']


st.title('_Geoex_ :green[AI] 🧠 - Projetos e Carteiras')

if "messages" not in st.session_state:
    st.session_state.messages = []

st.chat_message("assistant").markdown(
    'Olá! Eu sou o _Geoex_ :green[AI], um assistente virtual que pode te ajudar a encontrar informações sobre Projetos e Carteiras de obras! Como posso te ajudar hoje?')

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como posso te ajudar?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    # prompt = prompt_template.format(
    #     chat_history=st.session_state.messages, prompt=prompt, tables=tables)

    prompt = prompt_template.format(prompt=prompt, tables=tables)
    response = agent.run(prompt)

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
        st.chat_message("assistant").markdown(response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
