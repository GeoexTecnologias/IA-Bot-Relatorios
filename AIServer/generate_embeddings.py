from sqlalchemy import create_engine
from sqlalchemy import inspect
import pymssql
from dotenv import load_dotenv
import os
from langchain.vectorstores import Chroma
import pinecone
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Pinecone
load_dotenv()


def connect_db():
    server = os.getenv("SERVER")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    port = os.getenv("PORT")
    uri = f"mssql+pymssql://{username}:{password}@{server}/{database}"
    return pymssql.connect(server, username, password, database), uri


if __name__ == '__main__':
    VECTOR_DBS = ['PC', 'CH']
    vector_db = VECTOR_DBS[1]

    conn, uri = connect_db()
    engine = create_engine(uri)
    inspector = inspect(engine)
    tabelas = inspector.get_table_names()

    col_to_use = ['Projeto', 'Nota', 'ProjetoProgramacaoCarteira']

    tabelas = [tabela for tabela in tabelas if tabela in col_to_use]

    with open('./rag_data/db_schema.txt', 'w') as f:
        for tabela in tabelas:
            f.write(f'table {tabela} cols: ')
            for coluna in inspector.get_columns(tabela):
                f.write(f'[{coluna["name"]} ')
                f.write(f'{coluna["type"]}]')
            f.write('\n')
            print(f'Escrevendo {tabela} no arquivo')

    db_schema = open('./rag_data/db_schema.txt'', 'r')
    tokens = 0
    for line in db_schema:
        tokens += len(line.split())
    print(f'Número de tokens: {tokens}')

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=150,
        chunk_overlap=0,
        length_function=len
    )

    with open('./rag_data/db_schema.txt'') as f:
        db_schema = f.read()
    chunks = splitter.create_documents([db_schema])

    embeddings = OpenAIEmbeddings(model='text-embedding-3-small',)

    if vector_db == 'PC':
        pc = pinecone.Pinecone()

        for i in pc.list_indexes().names():
            print('Deletando indice ', i)
            pc.delete_index(i)

        index_name = 'geoex-sql-embeddings'
        if index_name not in pc.list_indexes().names():
            print('Criando index', index_name)
            pc.create_index(
                name=index_name,
                dimension=1536,
                metric='cosine',
                spec=pinecone.PodSpec(
                    environment='gcp-starter'
                )

            )
            print('done')

        vector_store = Pinecone.from_documents(
            chunks, embeddings, index_name=index_name)
        print('done')
    elif vector_db == 'CH':
        embeddings = OpenAIEmbeddings(
            model='text-embedding-3-small', dimensions=1536)
        persist_directory = './geoex-sql-embeddings-chroma'
        vector_store = Chroma.from_documents(
            chunks, embeddings, persist_directory=persist_directory)
