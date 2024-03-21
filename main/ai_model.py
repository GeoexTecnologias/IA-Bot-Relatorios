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
        llm=llm, chain_type='stuff', retriever=retriever)

    return chain


def conversational_retriever_chain(index_name):
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

    # Conversational Retrieval Chain

    crc = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        chain_type='stuff'
    )
    return crc


def generate_query_ai(index_name, question):

    chain = conversational_retriever_chain(index_name)
    prompt = prompt_template(question)
    result = chain.invoke(prompt)['answer']

    if 'SQLQuery' not in result:
        return result

    result = result.split('SQLQuery:')[1]
    print(result)

    if validate_query(result):
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
            return True, df
        return False, None

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


def prompt_template(question):
    template = """
    Dada uma pergunta de entrada, primeiro crie uma consulta {dialeto} sintaticamente correta para ser executada, depois examine os resultados da consulta e retorne a resposta sempre em portugues.
    Use o seguinte formato:

    SQLQuery: "Consulta SQL a ser executada ou resposta da pergunta."
    
    Use apenas as tabelas a seguir:

    {table_info}.

    Alguns exemplos de consultas SQL que se enquadram em perguntas são:

    {few_shot_examples}
    
    Observações: 
        - Em consultas com datas e que o usuário nao especificou o ano, use o ano atual.
        - Se o input do usuário for como uma conversa normal, seja educado e mais humano possível.
        - Caso o usuário nao entenda, explique para ele o que voce faz e quais dados do banco voce consegue consultar
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

    
    
    """,
    prompt_template = PromptTemplate.from_template(template=template)
    return prompt_template.format(dialeto=dialect, table_info=cols, few_shot_examples=few_shot_examples, input=question)


if __name__ == "__main__":
    while True:
        question = input("Digite a pergunta: ")
        if question == 'tchau':
            print('Estou aqui para ajudar! Até a próxima')
            break
        query = generate_query_ai("geoex-sql-embeddings", question)
        print(query)
