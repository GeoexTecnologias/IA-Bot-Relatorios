import time
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import sys
from langchain_openai import ChatOpenAI, OpenAI
from langchain_experimental.agents.agent_toolkits import create_csv_agent, create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from langchain.agents import Tool, AgentExecutor, initialize_agent, create_react_agent
from db_interface import DBInterface
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
        df.to_csv('llm-data/projetos.csv', index=False)
        return df
    return False


def projetos_carteiras():
    proj_join_ppc_query = """SELECT p.ProjetoId,p.Titulo,p.DataCriacao,p.OrgaoExecutor,ppc.Carteira,ppc.Previsao FROM Projeto p
    right join ProjetoProgramacaoCarteira ppc
    on p.ProjetoId = ppc.ProjetoId
    WHERE YEAR(ppc.Carteira) >= YEAR(GETDATE())
    AND YEAR(ppc.Carteira) <= YEAR(GETDATE()) + 1
    ORDER BY ppc.Carteira ASC"""
    return query(proj_join_ppc_query)


prompt_template = """
ai_instructions:
- sabendo que o dataframe informado contem dados de Projetos e Carteiras de obras, responda a seguinte pergunta:

- responda a pergunta com um dataframe contendo as informações solicitadas

- se o usuário agradecer, cumprimentar ou se despedir, responda de forma educada

- se o usuário nao especificar um ano especifico, retorne os dados do ano atual

user_question: {prompt}
"""
db_interface = DBInterface()

projetos_data_tool = create_pandas_dataframe_agent(
    ChatOpenAI(temperature=0.2, model="gpt-3.5-turbo"),
    db_interface.projetos_carteiras(),
    verbose=True,
    agent_type=AgentType.OPENAI_FUNCTIONS,
)

if __name__ == '__main__':
    prompt = str(input("Digite a pergunta: "))

    response = projetos_data_tool.run(
        prompt_template.format(prompt=prompt)
    )
