import pymssql
import os
from dotenv import load_dotenv
import pandas as pd
load_dotenv()


class DBInterface:
    def __init__(self):
        self.server = os.getenv("SERVER")
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")
        self.database = os.getenv("DATABASE")
        self.port = os.getenv("PORT")
        self.uri = f"mssql+pymssql://{self.username}:{self.password}@{self.server}/{self.database}"
        self.conn = pymssql.connect(
            self.server, self.username, self.password, self.database)

    def query(self, query, nome_arquivo):
        cursor = self.conn.cursor()
        cursor.execute(query)
        df = pd.read_sql_query(query, self.conn)
        if len(df) > 0:
            return df
        return False

    def projetos_carteiras(self):
        proj_join_ppc_query = """SELECT p.ProjetoId,p.Titulo,p.DataCriacao,p.OrgaoExecutor,ppc.Carteira,ppc.Previsao FROM Projeto p
        right join ProjetoProgramacaoCarteira ppc
        on p.ProjetoId = ppc.ProjetoId
        WHERE YEAR(ppc.Carteira) >= YEAR(GETDATE())
        AND YEAR(ppc.Carteira) <= YEAR(GETDATE()) + 1
        ORDER BY ppc.Carteira ASC"""

        file_name = 'projetos'
        df = self.query(proj_join_ppc_query, 'projetos')
        df['Carteira'] = pd.to_datetime(df['Carteira'])
        df.to_csv(f'llm-data/{file_name}.csv', index=False)

        return df

    def close(self):
        self.conn.close()
