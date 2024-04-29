from openai import OpenAI
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

# /TheBloke/Mistral-7B-Instruct-v0.1-GGUF/blob/main/mistral-7b-instruct-v0.1.Q4_K_M.gguf

template = "<s>[INST] Which Projects are booked for January?[/INST]"
"SELECT * FROM Projeto p WHERE MONTH(p.Carteira) = 1</s> "
"[INST] {question} [/INST]"


prompt = PromptTemplate.from_template(template)

callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

llm = LlamaCpp(
    model_path="./models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
    temperature=0.1,
    max_tokens=500,
    n_gpu_layers=-1,
    top_p=1,
    callback_manager=callback_manager,
    verbose=False
)

question = """
Which projects are booked for the next two years?
"""

prompt = prompt.format(question=question)
print(prompt)
llm.invoke(prompt)
