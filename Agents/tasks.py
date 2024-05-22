# Import necessary agents and modules
from agents import sql_developer_agent, attendant_agent


from crewai import Task


# Verification Task


tarefa_verificacao = Task(
    description=(
        "User question: '{question}' "
        "Verify if the question can be answered using the tables Projeto and ProjetoProgramacaoCarteira. "
        "The structure of the tables are {schema_verificacao}."
    ),
    expected_output="Response indicating whether the query can be performed on the available tables",
    agent=attendant_agent,
)


# SQL Query Task


tarefa_consulta = Task(
    description=(
        "Return a SQL query for the SQL Server dialect, knowing that we have the tables with the structure: {schema_consulta}."
    ),
    expected_output="query.txt",
    agent=sql_developer_agent,
)


tarefa_finalizar_atendimento = Task(
    description=(
        "Return to the user if you have done the query, otherwise, tell him you can't validate the query with the available data"
    ),
    expected_output="A message to the user",
    agent=sql_developer_agent,
)
