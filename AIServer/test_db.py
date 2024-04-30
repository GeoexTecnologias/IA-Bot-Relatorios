import pypyodbc as odbc
import os
import pymssql
from dotenv import load_dotenv

load_dotenv()


print(os.environ["USERNAME_DB"])


def test_db_pypy():
    driver = os.environ["DRIVER"]
    server_name = os.environ["SERVER"]
    database = os.environ["DATABASE"]
    uid = os.environ["USERNAME_DB"]
    pwd = os.environ["PASSWORD"]

    connection_string = f"""
        DRIVER={{{driver}}};
        SERVER={server_name};
        DATABASE={database};
        uid={uid};
        pwd={pwd};
        Trust_Connection=yes;
        TrustServerCertificate=yes;
    """

    odbc.connect(connection_string)


def connect_with_pymssql():
    server = os.environ["SERVER"]
    user = os.environ["USERNAME_DB"]
    password = os.environ["PASSWORD"]
    database = os.environ["DATABASE"]

    conn = pymssql.connect(server, user, password, database)
    cursor = conn.cursor()
    cursor.execute("SELECT TOP 5* FROM dbo.Projeto")
    row = cursor.fetchone()
    while row:
        print(f"row = {row}")
        row = cursor.fetchone()
    conn.close()


connect_with_pymssql()
