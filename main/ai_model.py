from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import pinecone
from langchain_community.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
import pymssql
import pandas as pd
import random
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
load_dotenv()


def generate_gpt4(index_name):
    pc = pinecone.Pinecone(api_key=os.environ['PINECONE_API_KEY'])
    print('index', index_name, 'selected!')

    embeddings = OpenAIEmbeddings()
    vector_store = Pinecone.from_existing_index(
        index_name=index_name, embedding=embeddings)

    llm = ChatOpenAI(model='gpt-4', temperature=0.3)
    retriever = vector_store.as_retriever(
        search_type='similarity', search_kwargs={'k': 10})

    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=True)
    chain = RetrievalQA.from_chain_type(
        llm=llm, chain_type='retrieval_qa', retriever=retriever)

    return chain


def conversational_retriever_chain(index_name):
    cache = SQLiteCache()
    set_llm_cache(cache)
    pc = pinecone.Pinecone(api_key=os.environ['PINECONE_API_KEY'])
    print('index', index_name, 'selected!')

    embeddings = OpenAIEmbeddings()
    vector_store = Pinecone.from_existing_index(
        index_name=index_name, embedding=embeddings)

    llm = ChatOpenAI(model='gpt-4', temperature=0)
    retriever = vector_store.as_retriever(
        search_type='similarity', search_kwargs={'k': 5})
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=False)

    crc = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        chain_type='stuff'
    )
    return crc

# TODO: Adicionar messages como parametro para manter a conversa


def generate_query_ai(index_name, question, chat_history):

    chain = conversational_retriever_chain(index_name)
    prompt = prompt_template(question, chat_history)
    result = chain.invoke(prompt)['answer']

    if 'SQLQuery' not in result:
        if 'Resposta:' in result:
            return result.split('Resposta:')[1]
        return result

    try:
        result = result.split('SQLQuery:')[1]
        result = result.split('"')[1]
        if validate_query(result):
            df = get_query(result)
            return df
        else:
            return 'Não foi possível gerar o relatório. Tente outra pergunta. ou pergunte de outra forma'
    except Exception as e:
        return 'Não foi possível gerar o relatório. Tente outra pergunta. ou pergunte de outra forma'


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
        if len(df) > 0:
            return df
        return False
    except Exception as e:
        return 'Nao foi possível realizar a consulta. Tente novamente.'


def connect_db():
    server = os.getenv("SERVER")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    port = os.getenv("PORT")
    uri = f"mssql+pymssql://{username}:{password}@{server}/{database}"
    return pymssql.connect(server, username, password, database), uri


def prompt_template(question, chat_history):
    template = """
    baseado nas mensagens anteriores {chat_history}
    
    Dada uma pergunta de entrada, primeiro crie uma consulta {dialeto} sintaticamente correta para ser executada, depois examine os resultados da consulta e retorne a resposta sempre em portugues.
    Use o seguinte formato:

    SQLQuery: "Consulta SQL a ser executada ou resposta da pergunta."
    
    Use apenas as tabelas a seguir:

    {table_info}.

    Alguns exemplos de consultas SQL que se enquadram em perguntas são:

    {few_shot_examples}
    
    Observações: 
        - Seu nome é GeoAI e voce é o assistente virtual do Geoex, voce é educado e muito divertido.
        - Em consultas com datas e que o usuário nao especificou o ano, use o ano atual.
        - Se o input do usuário for como uma conversa normal, seja educado e mais humano possível.
        - Caso o usuário nao entenda, explique para ele o que voce faz e quais dados do banco voce consegue consultar
        - Se o usuário pedir todos os dados de uma tabela, limite a quantidade de linhas retornadas para 2000.
        - Se o usuário pedir todas as colunas de uma tabela peça para ele especificar quais colunas ele deseja.
        - Usuários podem fazer perguntas sobre como você funciona, o que você faz, o que você consegue consultar, agradecer, e vc deve ser educado etc.
        - Suas respostas devem ser em markdown quando nao forem consultas SQL.
    Pergunta: {input}
    """
    dialect = 'MS SQL Server'
    cols = ['Projeto', 'Nota', 'ProjetoProgramacaoCarteira']
    few_shot_examples = """
    Pergunta: Quais projetos/obras estao programados para serem executados nas carteiras de maio até dezembro deste ano?
    SQLQuery: SELECT Projeto.Titulo 
                FROM Projeto 
                INNER JOIN ProjetoProgramacaoCarteira 
                ON Projeto.ProjetoId = ProjetoProgramacaoCarteira.ProjetoId 
                WHERE ProjetoProgramacaoCarteira.Carteira BETWEEN CONVERT(date, CONVERT(varchar(4), YEAR(GETDATE())) + '-05-01') AND CONVERT(date, CONVERT(varchar(4), YEAR(GETDATE())) + '-12-31')

    Pergunta: Quais sao as colunas da tabela Projeto?
    SQLQuery: "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = 'Projeto'"
    
    
    """,
    prompt_template = PromptTemplate.from_template(template=template)
    return prompt_template.format(chat_history=chat_history, dialeto=dialect, table_info=cols, few_shot_examples=few_shot_examples, input=question)


if __name__ == "__main__":
    while True:
        question = input("Digite a pergunta: ")
        if question == 'tchau':
            print('Estou aqui para ajudar! Até a próxima')
            break
        query = generate_query_ai("geoex-sql-embeddings", question)
        print(query)
