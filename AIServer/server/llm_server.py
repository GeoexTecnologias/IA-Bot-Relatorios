from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler


def conversational_mistral(question):
    tables = ['Projeto', 'ProjetoProgramacaoCarteira', 'Nota']

    template = """\
    [INST] Olá! [/INST]
    Olá! Como você está? Sou o Geoex AI, posso te ajudar a gerar relatórios sobre as dados de {tables} e responder perguntas sobre dados. Como posso te ajudar hoje?
    [INST] QUais relatórios voce pode gerar?  [/INST]
    Posso gerar relatórios sobre os dados de {tables}.
    [INST] {question} [/INST]
    """
    prompt = PromptTemplate.from_template(template)
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    # The number of layers to put on the GPU. The rest will be on the CPU. If you don't know how many layers there are, you can use -1 to move all to GPU.
    n_gpu_layers = -1
    # Should be between 1 and n_ctx, consider the amount of VRAM in your GPU.
    n_batch = 512

    llm = LlamaCpp(
        model_path="/Users/brunoprado/Documents/Geoex Projetos/Geoex-AI-Relatorios/IA-Relatorios/AIServer/models/mistral-7b-instruct-v0.1.Q2_K.gguf",
        n_gpu_layers=n_gpu_layers,
        n_batch=n_batch,
        callback_manager=callback_manager
    )

    prompt = PromptTemplate.from_template(template)
    prompt = prompt.format(question=question, tables=tables)
    response = llm.invoke(prompt)


if __name__ == "__main__":
    conversational_mistral('Quais relatórios voce consegue gerar?')
