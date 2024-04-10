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
        df.to_csv('./pages/projetos.csv', index=False)
        return df
    return False


def projetos_carteiras():

    proj_join_ppc_query = """SELECT p.ProjetoId,p.Titulo,p.DataCriacao,p.OrgaoExecutor,ppc.Carteira,ppc.Previsao FROM Projeto p
    right join ProjetoProgramacaoCarteira ppc
    on p.ProjetoId = ppc.ProjetoId
    WHERE YEAR(ppc.Carteira) >= YEAR(GETDATE())
    AND YEAR(ppc.Carteira) <= YEAR(GETDATE()) + 1
    ORDER BY ppc.Carteira ASC"""

    return query(proj_join_ppc_query)
