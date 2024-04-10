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
import pymssql

load_dotenv()


def connect_db():
    server = os.getenv("SERVER")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    port = os.getenv("PORT")
    uri = f"mssql+pymssql://{username}:{password}@{server}/{database}"
    return pymssql.connect(server, username, password, database), uri


def query(query):
    conn, uri = connect_db()
    cursor = conn.cursor()
    cursor.execute(query)
    df = pd.read_sql_query(query, conn)
    if len(df) > 0:
        df.to_csv('projetos.csv', index=False)
        return df
    return False


st.set_page_config(page_title="Projetos e Carteiras", page_icon="🧠")

css_path = 'styles/style.css'
with open(css_path) as css:
    st.markdown(f'<style>{css.read()}</style>', unsafe_allow_html=True)

prompt_template = """
ai_instructions:
- sabendo que o dataframe informado contem dados de Projetos e Carteiras de obras, responda a seguinte pergunta:

- responda a pergunta com um dataframe contendo as informações solicitadas

- se o usuário pedir um relatorio ou uma pergunta que precisa ser respondida com um dataframe, 
construa uma consulta SQL para responder a pergunta, no formato ```sql <query>```

user_question: {prompt}
"""

projeto_df = projetos_carteiras()

dataframe_agent = create_pandas_dataframe_agent(
    ChatOpenAI(temperature=0.6, model="gpt-3.5-turbo"),
    pd.read_csv('./pages/projetos.csv'),
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
)
tables = ['Projeto', 'ProjetoProgramacaoCarteira']


st.title('_Geoex_ :green[AI] 🧠 - Projetos e Carteiras')

# if "messages" not in st.session_state:
#     st.session_state.messages = []

# st.chat_message("assistant").markdown(
#     'Olá! Eu sou o _Geoex_ :green[AI], um assistente virtual que pode te ajudar a encontrar informações sobre Projetos e Carteiras de obras! Como posso te ajudar hoje?')

# # Display chat messages from history on app rerun
# for message in st.session_state.messages:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# if prompt := st.chat_input("Como posso te ajudar?"):
#     st.chat_message("user").markdown(prompt)
#     st.session_state.messages.append({"role": "user", "content": prompt})

#     prompt = prompt_template.format(prompt=prompt, tables=tables)
#     response = dataframe_agent.run(prompt)

#     if '```sql' and 'SELECT' in response:
#         response = response.split('```sql')[1].replace('```', '')
#         print(response)
#         response = query(response)

#     elif isinstance(response, pd.DataFrame):
#         with st.status("Buscando os dados..."):
#             st.write("Buscando dados...")
#             time.sleep(2)
#             st.write("Dados Encontrados.")
#             time.sleep(2)
#             st.write("Carregando seus dados...")
#             time.sleep(2)
#         with st.chat_message("assistant"):
#             st.dataframe(response)
#     else:
#         with st.status("Pensando..."):
#             time.sleep(6)
#         st.chat_message("assistant").markdown(response)
#     st.session_state.messages.append(
#         {"role": "assistant", "content": response})

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Como posso te ajudar?"):
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    response = dataframe_agent.run(
        prompt_template.format(prompt=prompt, tables=tables)
    )

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
            time.sleep(3)
        st.chat_message("assistant").markdown(response)
    st.session_state.messages.append(
        {"role": "assistant", "content": response})
