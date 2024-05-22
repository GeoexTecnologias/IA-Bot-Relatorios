from crewai import Agent, Task, Crew, Process
from crewai_tools import FileReadTool
from tools import SQLQueryTool
from langchain_community.llms import Ollama
from tasks import tarefa_consulta, tarefa_geracao_excel, tarefa_verificacao

# Configurando a ferramenta SQLQueryTool
sql_tool = SQLQueryTool()

# Configurando o LLM
llm = Ollama(model="llama3")

# Agente Verificador
verificador = Agent(
    role="Verificador de viabilidade de relatórios",
    goal="Verificar se a pergunta pode ser respondida com os relatórios disponíveis",
    verbose=True,
    memory=True,
    backstory=(
        "Você é um especialista em análise de relatórios, com a capacidade de determinar "
        "rapidamente se uma consulta pode ser respondida com os dados disponíveis."
    ),
    llm=llm,
)

# Agente Consultor
consultor = Agent(
    role="Senior SQL Developer",
    goal="Realizar apenas consultas nas tabelas disponíveis",
    verbose=True,
    memory=True,
    backstory=(
        "Você é um especialista em realizar consultas detalhadas em bases de dados, "
        "capaz de extrair informações precisas conforme solicitado."
    ),
    tools=[sql_tool],
    llm=llm,
)

# Agente Gerador de Excel
gerador_excel = Agent(
    role="Gerador de Excel",
    goal="Gerar arquivos Excel com os resultados das consultas realizadas",
    verbose=True,
    memory=True,
    backstory=(
        "Você é um especialista em manipulação de dados, com a capacidade de gerar relatórios Excel "
        "de forma rápida e eficiente."
    ),
    output_file="relatorio.xlsx",
    tools=[sql_tool],
    llm=llm,
)

# Aqui você pode definir tarefas e a formação da sua Crew, como no exemplo anterior
# Exemplo de formação da Crew
crew = Crew(
    agents=[verificador, consultor, gerador_excel],
    tasks=[],  # Adicione suas tarefas aqui
    process=Process.sequential,
)

# Executar a Crew
result = crew.kickoff(inputs={"some_input_key": "some_input_value"})
print(result)
