from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
import pinecone
from langchain_community.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import pymssql
import pandas as pd
import random
load_dotenv()


def generate_query_ai(index_name, question):
    pc = pinecone.Pinecone(api_key=os.environ['PINECONE_API_KEY'])
    print('index', index_name, 'selected!')

    embeddings = OpenAIEmbeddings()
    vector_store = Pinecone.from_existing_index(
        index_name=index_name, embedding=embeddings)

    llm = ChatOpenAI(model='gpt-4', temperature=0.3)
    retriever = vector_store.as_retriever(
        search_type='similarity', search_kwargs={'k': 10})
    chain = RetrievalQA.from_chain_type(
        llm=llm, chain_type='stuff', retriever=retriever)

    prompt_template = """Gere consultas SQL para SQL Server usando as colunas: {cols}.
    apenas responda como consulta, sem nunhuma outra informação, exceto quando nao for possivel gerar a consulta.
    para responder esta pergunta de forma mais ao pé da letra possível: '{question}',
    use a seguinte estrutura:
    SQLQuery: <consulta_retornada_do_modelo>
    """

    prompt_template = PromptTemplate.from_template(template=prompt_template)
    prompt = prompt_template.format(
        question=question, cols='[Projeto, Nota, ProjetoProgramacaoCarteira]')

    # validando a query
    result = chain.invoke(prompt)['result']

    # pegue somente o que vem depois do SQLQuery:
    result = result.split('SQLQuery:')[1]
    # pegue o que esta entre aspas
    result = result.split('"')[1]

    print(result)

    is_valid = validate_query(result)
    if is_valid:
        if get_query(result):
            return result
        else:
            return 'O relatorio não retornou resultados. Tente outra pergunta. ou pergunte de outra forma'
    else:
        return result


def validate_query(query):
    try:
        conn, uri = connect_db()
        conn.cursor().execute(query)
        return True
    except Exception as e:
        print(e)
        return False


def get_query(query):
    try:
        conn, uri = connect_db()
        cursor = conn.cursor()
        cursor.execute(query)

        df = pd.read_sql_query(query, conn)
        random_number = random.randint(0, 1000)
        df.to_excel(
            f"./outputs/relatorio_ia_{random_number}.xlsx", index=False)
        if len(df) > 0:
            return True
        return False

    except Exception as e:
        print(e)


def connect_db():
    server = os.getenv("SERVER")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    port = os.getenv("PORT")
    uri = f"mssql+pymssql://{username}:{password}@{server}/{database}"
    return pymssql.connect(server, username, password, database), uri


def prompt_template(dialeto, table_info, few_shot_examples, input):
    template = """
    Dada uma pergunta de entrada, primeiro crie uma consulta {dialeto} sintaticamente correta para ser executada, depois examine os resultados da consulta e retorne a resposta.
    Use o seguinte formato:

    Pergunta: "Pergunta aqui"
    SQLQuery: "Consulta SQL a ser executada"
    SQLResult: "Resultado do SQLQuery"
    Resposta: "Resposta final aqui"

    Use apenas as tabelas a seguir:

    {table_info}.

    Alguns exemplos de consultas SQL que se enquadram em perguntas são:

    {few_shot_examples}

    Pergunta: {input}
    """
    prompt_template = PromptTemplate.from_template(template=template)
    return prompt_template.format(dialeto=dialeto, table_info=table_info, few_shot_examples=few_shot_examples, input=input)


if __name__ == "__main__":
    question = input("Digite a pergunta: ")
    table_info = ['Projeto', 'Nota']
    few_shot_examples = ['SELECT * FROM Projeto', 'SELECT * FROM Nota']
    prompt = prompt_template('MS SQL Server', table_info,
                             few_shot_examples, question)
    query = generate_query_ai("geoex-sql-embeddings", prompt)
    print(query)
