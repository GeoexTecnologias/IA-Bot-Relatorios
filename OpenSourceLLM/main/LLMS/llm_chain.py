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
