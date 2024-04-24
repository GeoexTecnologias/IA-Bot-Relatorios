from openai import OpenAI
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate

template = "<s>[INST] Which Projects are booked for January?[/INST]"
"SELECT * FROM Projeto p WHERE MONTH(p.Carteira) = 1</s> "
"[INST] {question} [/INST]"


prompt = PromptTemplate.from_template(template)

# Callbacks support token-wise streaming
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])

# Make sure the model path is correct for your system!
llm = LlamaCpp(
    model_path="./models/mistral-7b-instruct-v0.1.Q2_K.gguf",
    temperature=0.1,
    max_tokens=500,
    n_gpu_layers=-1,
    top_p=1,
    callback_manager=callback_manager,
    verbose=False,  # Verbose is required to pass to the callback manager
)

question = """
Which projects are booked for the next two years?
"""

prompt = prompt.format(question=question)
print(prompt)
llm.invoke(prompt)
