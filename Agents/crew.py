from tools import SQLQueryTool

sql_tool = SQLQueryTool()

table_names = ["Projeto", "ProjetoProgramacaCarteira"]
schema_tables = sql_tool.store_column_data_types_to_string()

crew = Crew(
    agents=[verificador, consultor, gerador_excel],
    tasks=[tarefa_verificacao, tarefa_consulta, tarefa_geracao_excel],
    process=Process.sequential,  # Pode ser alterado para processamentos simultâneos se necessário
)

# Início do fluxo de trabalho
result = crew.kickoff(
    inputs={"schema_verificacao": schema_tables, "schema_consulsta": schema_tables}
)
print(result)
