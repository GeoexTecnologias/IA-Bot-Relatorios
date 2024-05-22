from crewai_tools import BaseTool
import pymssql
from dotenv import load_dotenv
import os


class DatabaseQueryTool(BaseTool):
    name: str = "DatabaseQueryTool"
    description: str = "Tool to execute a query on a MSSQL database."

    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def _run(self, query: str) -> str:
        result = []
        try:
            conn = pymssql.connect(
                server=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
            )
            cursor = conn.cursor(as_dict=True)
            cursor.execute(query)
            for row in cursor:
                result.append(row)
            conn.close()
        except pymssql.Error as e:
            return f"Database query failed: {e}"

        return result


if __name__ == "__main__":
    load_dotenv()
    host = os.getenv("SERVER_DB")
    user = os.getenv("USERNAME_DB")
    password = os.getenv("PASSWORD_DB")
    database = os.getenv("DATABASE")

    db_tool = DatabaseQueryTool(
        host=host,
        user=user,
        password=password,
        database=database,
    )

    query = "SELECT top 1 * FROM Projeto"
    result = db_tool._run(query)
    print(result)
