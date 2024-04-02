from langchain.agents.agent_types import AgentType
from langchain_openai import ChatOpenAI
from langchain.prompts.chat import ChatPromptTemplate
from langchain.cache import SQLiteCache
from langchain.vectorstores import Chroma
from langchain.globals import set_llm_cache
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
import pinecone
from langchain.llms import huggingface_hub
from langchain_community.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
import os
from langchain_community.llms import HuggingFaceEndpoint
import pymssql
import pandas as pd
import random
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
load_dotenv()


def is_query_result(prompt, chat_history, cols):
    prompt_template = """
    baseado no historico do chat: {chat_history}
    
    baseado nas colunas: {cols}, responda se a pergunta do usuário é possivel de 
    ser respondida com uma consulta SQL.
    
    Responda:
    
    - 1, se a pergunta do usuário for possivel de ser respondida com uma consulta SQL
    - 0, se a pergunta do usuário não for possivel de ser respondida com uma consulta SQL

    Com base nas instruções responda: {prompt}
    """
    prompt_template = PromptTemplate.from_template(template=prompt_template)
    question = prompt_template.format(
        cols=cols, prompt=prompt, chat_history=chat_history)
    llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.5)
    return llm.invoke(question).content, prompt


def answer_normal_question(prompt, chat_history, cols):
    prompt_template = """
    baseado no historico do chat: {chat_history}
    Seu nome é Geoex AI e voce é o assistente virtual do Geoex, um assistente 
    virtual que pode te ajudar a encontrar informações dados do seu interesse sobre {cols}! 
    Como posso te ajudar hoje?

    Instruções:
    - Voce pode usar emojis
    - Seja educado e bem humorado
    
    Com base nas instruções responda: {prompt}
    """
    prompt_template = PromptTemplate.from_template(template=prompt_template)
    question = prompt_template.format(
        cols=cols, prompt=prompt, chat_history=chat_history)
    llm = ChatOpenAI(model='gpt-3.5-turbo', temperature=0.5)
    return llm.invoke(question).content, prompt


def conversational_retriever_chain(index_name, vector_db):
    if vector_db == 'PC':
        cache = SQLiteCache()
        set_llm_cache(cache)
        pc = pinecone.Pinecone(api_key=os.environ['PINECONE_API_KEY'])
        print('index', index_name, 'selected!')

        embeddings = OpenAIEmbeddings(model='text-embedding-3-small')
        vector_store = Pinecone.from_existing_index(
            index_name=index_name, embedding=embeddings)

    elif vector_db == 'CH':
        persist_directory = '../embeddings/geoex-sql-embeddings-chroma'
        embeddings = OpenAIEmbeddings(
            model='text-embedding-3-small', dimensions=1536)
        vector_store = Chroma(
            persist_directory=persist_directory, embedding_function=embeddings)

    llm = ChatOpenAI(model='gpt-4-0125-preview', temperature=0.3)

    retriever = vector_store.as_retriever(
        search_type='similarity', search_kwargs={'k': 8})
    memory = ConversationBufferMemory(
        memory_key='chat_history', return_messages=False)

    crc = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        chain_type='stuff'
    )
    return crc


def generate_query_ai(index_name, question, chat_history):
    cols = ['Projeto', 'Nota', 'ProjetoProgramacaoCarteira']
    result, prompt = is_query_result(
        question, chat_history=chat_history, cols=cols)

    if result == '1':
        chain = conversational_retriever_chain(index_name, vector_db='CH')
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
    return answer_normal_question(question, chat_history, cols)


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
    
    Dada uma pergunta de entrada, crie uma consulta {dialeto} sintaticamente correta para ser executada.
    Use o seguinte formato:

    SQLQuery: "Consulta SQL a ser executada"
    
    
    Use apenas as tabelas a seguir:

    {table_info}.
    

    Alguns exemplos de consultas SQL que se enquadram em perguntas são:

    {few_shot_examples}
    
    
    Observações: 
        - Seu nome é Geoex AI e voce é o assistente virtual do Geoex
        - Se o input do usuário for como uma conversa normal, seja educado e mais humano possível.
        - Caso o usuário nao entenda, explique para ele o que voce faz e quais dados do banco voce consegue consultar
        - Se o usuário pedir todas as colunas de uma tabela peça para ele especificar quais colunas ele deseja.
        - Usuários podem fazer perguntas sobre como você funciona, o que você faz, o que você consegue consultar, agradecer, e vc deve ser educado etc.

    Pergunta: {input}
    
    - Se o usuário nao especificou, use o ano atual.
    
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
    
    Pergunta: Como voce funciona:
    Resposta: Eu sou um assistente virtual que pode te ajudar a encontrar informações dados do seu interesse!
    """,
    prompt_template = PromptTemplate.from_template(template=template)
    return prompt_template.format(chat_history=chat_history, dialeto=dialect, table_info=cols, few_shot_examples=few_shot_examples, input=question)
