# Import necessary agents and modules
from agents import sql_developer_agent, attendant_agent
from tools import SQLServerTool
from crewai import Task

sql_tool = SQLServerTool()
# Verification Task


tarefa_verificacao = Task(
    description=(
        "User question: '{question}' "
        "Verify if the question can be answered using the tables of the database"
        ""
    ),
    expected_output="Response indicating if the query can be performed on the available tables or not",
    agent=attendant_agent,
)


# SQL Query Task


tarefa_consulta = Task(
    description=("Return a SQL query for the SQL Server dialect"),
    expected_output="query.txt",
    agent=sql_developer_agent,
    tools=[sql_tool],
)


tarefa_finalizar_atendimento = Task(
    description=(
        "Return to the user if you have done the query, otherwise, tell him you can't validate the query with the available data"
    ),
    expected_output="A message to the user",
    agent=sql_developer_agent,
)
