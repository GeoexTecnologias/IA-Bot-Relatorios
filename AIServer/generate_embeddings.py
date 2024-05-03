from sqlalchemy import create_engine
from sqlalchemy import inspect
import pymssql
import pypyodbc as odbc
from dotenv import load_dotenv
import os
from langchain.vectorstores import Chroma
import pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
import pyodbc

load_dotenv()


def connect_db():
    server = os.getenv("SERVER")
    username = os.getenv("USERNAME_DB")
    password = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    port = os.getenv("PORT")
    print(server, username, password, database)
    uri = f"mssql+pymssql://{username}:{password}@{server}/{database}"
    return pymssql.connect(server, username, password, database), uri


""" def connect_db():
    driver = os.environ["DRIVER"]
    server_name = os.environ["SERVER"]
    database = os.environ["DATABASE"]
    uid = os.environ["USERNAME_DB"]
    pwd = os.environ["PASSWORD"]

    connection_string = f"
        DRIVER={{{driver}}};
        SERVER={server_name};
        DATABASE={database};
        uid={uid};
        pwd={pwd};
        Trust_Connection=yes;
        TrustServerCertificate=yes;
    "

    sqlalchemy_url = f"mssql+pyodbc://{uid}:{pwd}@{server_name}/{database}?driver=ODBC+Driver+17+for+SQL+Server&TrustServerCertificate=yes"

    return odbc.connect(connection_string), sqlalchemy_url"""


if __name__ == "__main__":
    VECTOR_DBS = ["PC", "CH"]
    vector_db = VECTOR_DBS[1]

    conn, uri = connect_db()
    engine = create_engine(uri)
    inspector = inspect(engine)
    tabelas = inspector.get_table_names()

    col_to_use = ["Projeto", "Nota", "ProjetoProgramacaoCarteira"]

    tabelas = [tabela for tabela in tabelas if tabela in col_to_use]

    with open("./rag_data/db_schema_proj_projprogcart.txt", "w") as f:
        for tabela in tabelas:
            f.write(f"table {tabela} cols: ")
            for coluna in inspector.get_columns(tabela):
                f.write(f'[{coluna["name"]} ')
                f.write(f'{coluna["type"]}]')
            f.write("\n")
            print(f"Escrevendo {tabela} no arquivo")

    db_schema = open("./rag_data/db_schema.txt", "r")
    tokens = 0
    for line in db_schema:
        tokens += len(line.split())
    print(f"Número de tokens: {tokens}")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150, chunk_overlap=0, length_function=len
    )

    with open("./rag_data/db_schema.txt") as f:
        db_schema = f.read()
    chunks = splitter.create_documents([db_schema])

    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-small",
    )

    if vector_db == "PC":
        pc = pinecone.Pinecone()

        for i in pc.list_indexes().names():
            print("Deletando indice ", i)
            pc.delete_index(i)

        index_name = "geoex-sql-embeddings"
        if index_name not in pc.list_indexes().names():
            print("Criando index", index_name)
            pc.create_index(
                name=index_name,
                dimension=1536,
                metric="cosine",
                spec=pinecone.PodSpec(environment="gcp-starter"),
            )
            print("done")

        vector_store = Pinecone.from_documents(
            chunks, embeddings, index_name=index_name
        )
        print("done")
    elif vector_db == "CH":
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", dimensions=1536)
        persist_directory = "./geoex-sql-embeddings-chroma"
        vector_store = Chroma.from_documents(
            chunks, embeddings, persist_directory=persist_directory
        )
