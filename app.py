from langchain import OpenAI
from langchain_experimental.agents.agent_toolkits import create_csv_agent
from langchain_openai import ChatOpenAI, OpenAI
from dotenv import load_dotenv
from langchain.cache import SQLiteCache
from langchain.globals import set_llm_cache
from langchain.agents.agent_types import AgentType
from langchain import PromptTemplate
from langchain_community.utilities import SQLDatabase
import os
load_dotenv()

llm = ChatOpenAI()
model = 'gpt-3.5-turbo'
set_llm_cache(SQLiteCache(database_path='./cache/langchain.db'))

# db_uri = f"mssql+pymssql://{os.getenv('USERNAME')}:{os.getenv('PASSWORD')}@{os.getenv('SERVER')}/{os.getenv('DATABASE')}"
# db = SQLDatabase.from_uri(db_uri)

# csv agent
csv_agent = create_csv_agent(
    OpenAI(temperature=0),
    "CellSense_05_metadata.csv",
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

template_csv = '''
baseado na pergunta: "{question}", retorne os nomes qual a tabela e a coluna que e as colunas que juntas podem ter uma consulta para obter a resposta?
'''
prompt_template = PromptTemplate.from_template(template=template_csv)

question = "Quantos projetos estao na carteira de obras de Outubro de 2024"
prompt = prompt_template.format(question=question)
csv_agent.run(prompt)


# text to SQL
# text2sql = ChatOpenAI(model=model, temperature=0)
