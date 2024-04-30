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
    [INST] Quais relatórios voce pode gerar?  [/INST]
    Posso gerar relatórios sobre os dados de {tables}.
    [INST] {question} [/INST]
    """
    prompt = PromptTemplate.from_template(template)
    callback_manager = CallbackManager([StreamingStdOutCallbackHandler()])
    n_gpu_layers = -1
    n_batch = 512

    llm = LlamaCpp(
        model_path="../models/mistral-7b-instruct-v0.1.Q4_K_M.gguf",
        temperature=0.4,
        max_tokens=500,
        n_gpu_layers=-1,
        top_p=1,
        callback_manager=callback_manager,
        verbose=True
    )

    prompt = PromptTemplate.from_template(template)
    prompt = prompt.format(question=question, tables=tables)
    response = llm.invoke(prompt)


if __name__ == "__main__":

    while True:
        question = str(input('Digite sua pergunta: '))
        conversational_mistral(question)
