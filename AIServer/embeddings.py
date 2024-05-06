import pypyodbc as odbc
import os

import pymssql

from dotenv import load_dotenv

from langchain.text_splitter import RecursiveCharacterTextSplitter

from InstructorEmbedding import INSTRUCTOR

import pickle
import faiss

from langchain.vectorstores import FAISS

from langchain.embeddings import HuggingFaceInstructEmbeddings

from langchain_community.embeddings import HuggingFaceEmbeddings


load_dotenv()


def connect_database():

    server = os.environ["SERVER"]

    user = os.environ["USERNAME_DB"]

    password = os.environ["PASSWORD"]

    database = os.environ["DATABASE"]

    conn = pymssql.connect(server, user, password, database)
    cursor = conn.cursor()

    return conn, cursor


def get_columns_dtypes(tables: list):

    conn, cursor = connect_database()

    for table in tables:

        cursor.execute(
            f"""


            SELECT COLUMN_NAME, DATA_TYPE


            FROM INFORMATION_SCHEMA.COLUMNS


            WHERE TABLE_NAME = '{table}'
        """
        )

        rows = cursor.fetchall()

        with open("./rag_data/db_schema_projeto_carteira.txt", "a") as f:

            f.write(f"Table: {table} - Columns:")

            for row in rows:

                f.write(f"({row[0]} {row[1]})")

            f.write("\n")
    conn.close()


def generate_chunks(tables: list):

    get_columns_dtypes(tables=tables)

    db_schema = open("./rag_data/db_schema_projeto_carteira.txt", "r")

    tokens = 0

    for line in db_schema:

        tokens += len(line.split())

    print("Tokens:", tokens)

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150, chunk_overlap=0, length_function=len
    )

    with open("./rag_data/db_schema_projeto_carteira.txt") as f:
        db_schema = f.read()

    chunks = splitter.create_documents([db_schema])

    return chunks


def store_embeddings(docs, embeddings, store_name, path):

    vectorStore = FAISS.from_documents(docs, embeddings)

    with open(f"{path}/faiss_{store_name}.pkl", "wb") as f:

        pickle.dump(vectorStore, f)


def load_embeddings(store_name, path):

    with open(f"{path}/faiss_{store_name}.pkl", "rb") as f:

        VectorStore = pickle.load(f)

    return VectorStore


if __name__ == "__main__":

    load_dotenv()

    tables = ["Projeto", "ProjetoProgramacaoCarteira"]

    chunks = generate_chunks(tables)

    instructor_embeddings = HuggingFaceEmbeddings()

    embedding_store_path = "./embeddings"

    store_embeddings(
        chunks,
        instructor_embeddings,
        store_name="instructEmbeddings",
        path=embedding_store_path,
    )

    print("Embeddings armazenados")

    vector_store = load_embeddings(
        store_name="instructEmbeddings", path=embedding_store_path
    )
