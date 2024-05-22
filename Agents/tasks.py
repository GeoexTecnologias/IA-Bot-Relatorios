# Tarefa de Verificação
from agents import consultor, gerador_excel, verificador

tarefa_verificacao = Task(
    description=(
        "Verificar se a pergunta pode ser respondida usando as tabelas Projeto e ProjetoProgramacaoCarteira."
        "Os schemas das tabelas sao {schema_verificacao}"
    ),
    expected_output="Resposta indicando se a consulta pode ser realizada",
    agent=verificador,
)

# Tarefa de Consulta
tarefa_consulta = Task(
    description=(
        "Realizar a consulta nas tabelas Projeto e ProjetoProgramacaoCarteira de acordo com a pergunta do usuário."
        "Sabendo que o schema da tabela é: {schema_consulta}"
    ),
    expected_output="Resultados da consulta",
    agent=consultor,
)

# Tarefa de Geração de Excel
tarefa_geracao_excel = Task(
    description=("Gerar um arquivo Excel com os resultados da consulta realizada."),
    expected_output="Arquivo Excel gerado com os resultados da consulta",
    agent=gerador_excel,
)
