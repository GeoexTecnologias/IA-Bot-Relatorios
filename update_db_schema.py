from sqlalchemy import create_engine
from sqlalchemy import inspect
import pymssql
from dotenv import load_dotenv
import os
load_dotenv()


def connect_db():
    server = os.getenv("SERVER")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    port = os.getenv("PORT")
    uri = f"mssql+pymssql://{username}:{password}@{server}/{database}"
    return pymssql.connect(server, username, password, database), uri


conn, uri = connect_db()
engine = create_engine(uri)
inspector = inspect(engine)
tabelas = inspector.get_table_names()
# TODO: SET ONLY USABLE TABLES

with open('db_schema.txt', 'w') as f:
    for tabela in tabelas:
        f.write(f'table {tabela} cols: ')
        for coluna in inspector.get_columns(tabela):
            f.write(f'[{coluna["name"]} ')
            f.write(f'{coluna["type"]}]')
        f.write('\n')
        print(f'Escrevendo {tabela} no arquivo')
