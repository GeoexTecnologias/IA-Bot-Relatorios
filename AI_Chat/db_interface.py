import pymssql
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv()


class DBInterface:
    def __init__(self):
        self.server = os.getenv("SERVER")
        self.username = os.getenv("USERNAME_DB")
        self.password = os.getenv("PASSWORD")
        self.database = os.getenv("DATABASE")
        self.port = os.getenv("PORT")
        self.uri = f"mssql+pymssql://{self.username}:{self.password}@{self.server}/{self.database}"
        self.conn = pymssql.connect(
            self.server, self.username, self.password, self.database
        )

    def query(self, query, nome_arquivo):
        cursor = self.conn.cursor()
        cursor.execute(query)
        df = pd.read_sql_query(query, self.conn)
        if len(df) > 0:
            df.to_csv(f"./dataframes/{nome_arquivo}.csv", index=False)
            return df
        return False

    def close(self):
        self.conn.close()
