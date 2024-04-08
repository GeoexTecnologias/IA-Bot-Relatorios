import pandas as pd
from langchain_openai import ChatOpenAI
import os
import pymssql
from dotenv import load_dotenv
load_dotenv()


def connect_db():
    server = os.getenv("SERVER")
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    database = os.getenv("DATABASE")
    port = os.getenv("PORT")
    uri = f"mssql+pymssql://{username}:{password}@{server}/{database}"
    return pymssql.connect(server, username, password, database), uri


def query(query):
    conn, uri = connect_db()
    cursor = conn.cursor()
    cursor.execute(query)
    df = pd.read_sql_query(query, conn)
    if len(df) > 0:
        return df
    return False


def projetos_carteiras():
    return query("""
            SELECT ppc.Carteira,ppc.previsao,ppc.ProjetoId,pct.Nome Criterio
                FROM ProjetoProgramacaoCarteira ppc
                RIGHT JOIN ProgramacaoCarteiraTipo pct ON ppc.ProgramacaoCarteiraCriterioId = ppc.ProgramacaoCarteiraCriterioId
            """)
