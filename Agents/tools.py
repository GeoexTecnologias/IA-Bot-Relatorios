import pymssql
from dotenv import load_dotenv
import os


class SQLServerTool:
    name: str = "SQL Server Utility Tool"
    description: str = (
        "This tool allows for executing SQL queries and retrieving database schema information from a SQL Server database."
    )

    def __init__(self):
        load_dotenv()
        self.server = os.getenv("SERVER_DB")
        self.username = os.getenv("USERNAME_DB")
        self.password = os.getenv("PASSWORD_DB")
        self.database = os.getenv("DATABASE")

    def _connect(self):
        return pymssql.connect(
            server=self.server,
            user=self.username,
            password=self.password,
            database=self.database,
        )

    def _run(self, query: str) -> list:
        try:
            conn = self._connect()
            cursor = conn.cursor(as_dict=True)
            cursor.execute(query)
            conn.close()
            return "Query OK"
        except pymssql.Error as e:
            return f"Database query failed: {e}"

        return result

    def save_db_schema(self, table_names: list) -> str:
        try:
            conn = self._connect()
            cursor = conn.cursor(as_dict=True)
            schema_str = ""

            for table_name in table_names:
                cursor.execute(
                    f"""
                    SELECT COLUMN_NAME, DATA_TYPE 
                    FROM INFORMATION_SCHEMA.COLUMNS
                    WHERE TABLE_NAME = '{table_name}'
                    """
                )
                rows = cursor.fetchall()
                schema_str += f"Table: {table_name}\n"
                for row in rows:
                    schema_str += f"[{row['COLUMN_NAME']} {row['DATA_TYPE']}],"
                schema_str += "\n"

            conn.close()
            return schema_str

        except pymssql.Error as e:
            return f"Failed to retrieve schema: {e}"


if __name__ == "__main__":
    db_tool = SQLServerTool()

    query = "SELECT TOP 1 * FROM Projeto"
    result = db_tool._run(query)
    if isinstance(result, list):
        print("Query executed successfully")
    else:
        print(result)  # Print the error message

    tables = ["Projeto", "ProjetoProgramacaoCarteira"]
    schema = db_tool.save_db_schema(table_names=tables)
    if "Failed to retrieve schema" in schema:
        print(schema)  # Print the error message
    else:
        print("Schema saved\n")
