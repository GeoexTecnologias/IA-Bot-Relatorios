from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_community.llms import LlamaCpp
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from dotenv import load_dotenv
from dataframes import store_column_data_types_to_file
from db_interface import DBInterface
import pandas as pd

load_dotenv()


def validate_query(query):

    try:

        if "SQLQuery:" in query:
            query = query.split("SQLQuery:")[1]
        elif "SELECT" in query:
            query = query

        conn = DBInterface().conn
        conn.cursor().execute(query)

        df = pd.read_sql_query(query, conn)

        return True, df
    except Exception as e:

        return False, query


def embedding(tables_names: list[str], file_name: str):
    store_column_data_types_to_file(table_names, file_name)
    tables_schema = open("tables.txt", "r")

    tokens = 0
    for line in tables_schema:
        tokens += len(line.split())
    print(f"Número de tokens: {tokens}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150, chunk_overlap=0, length_function=len
    )

    with open(file_name) as f:
        db_schema = f.read()
    chunks = splitter.create_documents([db_schema])

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
    )

    persist_directory = "./embeddings"

    vector_store = Chroma.from_documents(
        chunks, embeddings, persist_directory=persist_directory
    )


def conversational_retriever_chain(persist_directory: str):
    persist_directory = "./embeddings"
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536)
    vector_store = Chroma(
        persist_directory=persist_directory, embedding_function=embeddings
    )
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.4)
    retriever = vector_store.as_retriever(
        search_type="similarity", search_kwargs={"k": 8}
    )
    memory = ConversationBufferMemory(memory_key="chat_history", return_messages=False)

    crc = ConversationalRetrievalChain.from_llm(
        llm=llm, retriever=retriever, memory=memory, chain_type="stuff"
    )
    return crc


def prompt_template(question: str):
    prompt_template = f"""
    
    Baseado nos dados fornecidos, construa uma consulta SQL usando somente as colunas e tabelas que conhece.
    
    Construa uma consulta sql que resposta a seguinte pergunta:
    
    Pergunta: Quantos projetos estao na carteira de obras de maio até dezembro de 2024?
    
    SQLQuery: SELECT COUNT(p.ProjetoId) AS Total_Projetos
                FROM Projeto p
                JOIN ProjetoProgramacaoCarteira ppc ON ppc.ProjetoId = p.ProjetoId
                WHERE MONTH(ppc.Carteira) BETWEEN 5 AND 12
                AND YEAR(ppc.Carteira) = 2024;
                
    
    Pergunta: {question}
    
    SQLQuery:
    """
    return prompt_template


def generate_response(user_question: str):
    table_names = [
        "Projeto",
        "ProjetoProgramacaoCarteira",
        "ProjetoProgramacaoBoletimProdutividade",
    ]

    file_name = "tables.txt"

    # TODO: descomentar caso mude o table_names embedding(tables_names=table_names, file_name=file_name)
    persist_directory = "./embeddings"
    crc = conversational_retriever_chain(persist_directory=persist_directory)

    formated_question = prompt_template(user_question)

    model_response = crc.invoke(formated_question)["answer"]

    is_valid, response = validate_query(model_response)

    if is_valid:
        return response
    else:
        return model_response


if __name__ == "__main__":
    # table_names = [
    #     "Projeto",
    #     "ProjetoProgramacaoCarteira",
    #     "ProjetoProgramacaoBoletimProdutividade",
    # ]

    # file_name = "tables.txt"
    # # TODO: descomentar caso mude o table_names embedding(tables_names=table_names, file_name=file_name)
    # persist_directory = "./embeddings"
    # crc = conversational_retriever_chain(persist_directory=persist_directory)

    # user_question = str(input("Digite a pergunta: "))

    # prompt_template = prompt_template(user_question)

    # model_response = crc.invoke(prompt_template)["answer"]
    # print(model_response)
    # is_valid, response = validate_query(model_response)

    # if is_valid:
    #     print(response.head())
    #     response.to_csv("./testes/query_result.csv", index=False)
    # else:
    #     print("else response")
    #     print(response)

    user_question = str(input("Digite a pergunta: "))
    response = generate_response(user_question)
    print(response)
