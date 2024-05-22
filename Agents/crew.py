from tools import SQLServerTool


from crewai import Crew, Agent, Task


from crewai.process import Process


from crewai_tools import BaseTool


from agents import attendant_agent, sql_developer_agent

from tasks import tarefa_verificacao, tarefa_consulta


def main(question):

    sql_server_tool = SQLServerTool()

    tables = ["Projeto", "ProjetoProgramacaoCarteira"]

    schemas = sql_server_tool.save_db_schema(table_names=tables)

    crew = Crew(
        agents=[attendant_agent, sql_developer_agent],
        tasks=[tarefa_verificacao, tarefa_consulta],
        process=Process.sequential,  # Pode ser alterado para processamentos simultâneos se necessário
    )

    # Início do fluxo de trabalho

    result = crew.kickoff(
        inputs={
            "schema_verificacao": schemas,
            "schema_consulta": schemas,
            "question": question,
        }
    )

    print(result)


if __name__ == "__main__":

    question = str(input("pergunte:"))

    main(question)
