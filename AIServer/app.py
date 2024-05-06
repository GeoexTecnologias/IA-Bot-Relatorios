from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain.agents.agent_types import AgentType
from langchain_community.llms import LlamaCpp
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate
from dataframes import projeto_carteira
from dotenv import load_dotenv

load_dotenv()

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# llm = LlamaCpp(
#     model_path="./models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
#     temperature=0.1,
#     max_tokens=200,
#     n_gpu_layers=-1,
#     top_p=1,
#     verbose=False,
#     n_ctx=2048,
# )

llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.5)


df_agent = create_pandas_dataframe_agent(llm, projeto_carteira(), verbose=True)

prompt = str(input("Digite sua pergunta: "))
resp = df_agent.invoke(prompt)
print(resp)
