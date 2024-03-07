import pymssql
import pandas as pd
import os
from dotenv import load_dotenv

def connect_database():
    load_dotenv()
    server = os.getenv('SERVER')
    user = os.getenv('USERNAME')
    password = os.getenv('PASSWORD')
    database = os.getenv('DATABASE')
    conn = pymssql.connect(server, user, password, database)
    return conn

conn = connect_database()
print(conn, "conexao estabelecida com sucesso!")
    