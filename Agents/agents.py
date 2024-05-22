from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool, tool
from tools import SQLServerTool
from langchain_community.llms import Ollama
import pymssql
from dotenv import load_dotenv
import os


# Configurando a ferramenta SQLQueryTool


@tool
def validate_sql(query):
    """


    Validates the SQL schema to ensure the required tables and columns are present.



    Parameters:


    schemas (dict): A dictionary representing the schema of the database.


    expected_tables (dict): A dictionary representing the expected tables and columns.



    Returns:


    bool: True if the schema is valid, False otherwise.
    """

    load_dotenv()

    server = os.getenv("SERVER_DB")

    username = os.getenv("USERNAME_DB")

    password = os.getenv("PASSWORD_DB")

    database = os.getenv("DATABASE")

    conn = pymssql.connect(
        server=server,
        user=username,
        password=password,
        database=database,
    )

    try:

        cursor = conn.cursor(as_dict=True)

        cursor.execute(query)

        conn.close()

        return "Query OK"

    except pymssql.Error as e:

        return f"Database query failed: {e}"


# Configurando o LLM


llm = Ollama(model="llama3")

tables = ["Projeto", "ProjetoProgramacaoCarteira"]
schema = SQLServerTool().save_db_schema(table_names=tables)

# Agente Verificador

attendant_agent = Agent(
    role="Report attendant",
    goal=(
        "You analyze the users' questions and depending on the question, you pass it on to the DBA,"
        "which develops the SQL query that generates the report the user wants"
        "If the question doesn't make sense, end the interaction"
        f"The database of our company has the following tables {tables}"
        f"with the following structure: {schema}"
    ),
    verbose=True,
    memory=True,
    backstory=("You are an attendant who passes demands to the Senior SQL Developer"),
    llm=llm,
    cach=True,
)


# Agente Consultor

sql_developer_agent = Agent(
    role="Senior SQL Developer",
    goal=(
        "You are an experienced SQL Developer who generates SQL queries"
        "for SQL Server based on the questions given to you by the attendant"
        f"The database of our company has the following tables {tables}"
        f"with the following structure: {schema}"
    ),
    verbose=True,
    memory=True,
    backstory=(
        "You are an experienced SQL developer who only makes queries with the columns and tables you know"
        "You specialize in queries for SQL Server databases"
    ),
    tools=[validate_sql],
    llm=llm,
    cache=True,
)
