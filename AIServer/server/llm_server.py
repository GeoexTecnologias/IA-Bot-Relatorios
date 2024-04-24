from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
template = """\
[INST] Olá! [/INST]
Olá! Como você está? Sou o Geoex AI, posso te ajudar a gerar relatórios e responder perguntas sobre dados. Como posso te ajudar hoje?
[INST] Estou ótimo, obrigado por perguntar. Você poderia me ajudar com uma tarefa? [/INST]
Claro, ficarei feliz em ajudar! Você poderia fornecer mais detalhes sobre a tarefa que precisa de assistência, como seu propósito e quaisquer requisitos ou restrições? Isso me ajudará a entender melhor como posso ajudar. Além disso, se você tiver alguma pergunta específica ou preocupação, fique à vontade para perguntar, e farei o possível para respondê-la.
[INST] {question} [/INST]
"""
prompt = PromptTemplate.from_template(template)
callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
# The number of layers to put on the GPU. The rest will be on the CPU. If you don't know how many layers there are, you can use -1 to move all to GPU.
n_gpu_layers = -1
# Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
n_batch = 512


while True:

    llm = LlamaCpp(
        model_path="/Users/brunoprado/Documents/Geoex Projetos/Geoex-AI-Relatorios/IA-Relatorios/AIServer/models/mistral-7b-instruct-v0.1.Q2_K.gguf",
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        callback_manager=callback_manager
    )

    question = input("Question: ")

    if question in ['exit', 'quit']:
        break
    prompt = PromptTemplate.from_template(template)
    prompt = prompt.format(question=question)
    response = llm.invoke(prompt)
