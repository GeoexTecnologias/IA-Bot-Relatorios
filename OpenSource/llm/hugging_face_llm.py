import os
from dotenv import load_dotenv
from langchain_community.llms import HuggingFaceEndpoint
from langchain.prompts import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from deep_translator import GoogleTranslator


class HuggingFaceLLM():
    def __init__(self, repo_id, max_length, temperature):
        load_dotenv()
        self.repo_id = repo_id
        self.max_length = max_length
        self.temperature = temperature
        self.llm = HuggingFaceEndpoint(
            repo_id=repo_id)

    def invoke(self, question):
        translator = GoogleTranslator(source='pt', target='en')
        question = translator.translate(question)
        response = self.llm.invoke(
            question)
        translated_response = translator.translate(response)
        return translated_response

    def define_prompt_template(self, template, template_args):  # Corrigindo aqui
        prompt_template = PromptTemplate.from_template(template=template)
        return prompt_template.format(**template_args)


if __name__ == '__main__':
    load_dotenv()
    llm = HuggingFaceLLM(
        repo_id='mistralai/Mistral-7B-v0.1',
        max_length=100,
        temperature=0.7
    )
    template = """
    You're a reporting bot. Your task is to assess user intent and categorize the user's question after <<<>>> between these categories:

    query
    non-query

    You will only respond with the category. Do not include the word "Category". Do not provide explanations or notes.

    Knowing that the avaible tables of the database are: {cols}
    ####
    Some examples:

    Question: What projects are ongoing this month?
    Category: query

    Question: Does the Project Portfolio have a project named "Project X"?
    Category: query

    Question: What projects are scheduled for the April portfolio?
    Category: consultation

    Question: Hi, how are you?
    Category: non-query
    
    Question: How can you help me?
    Category: non-query
    
    Question: What is your name?
    Category: non-query
    ###

    <<<
    question: {question}
    >>>
    """
    question = str(input('Digite sua pergunta:'))
    template_args = {
        'question': question,
        'cols': ['Projeto', 'Nota', 'ProjetoProgramacaoCarteira']
    }

    prompt = llm.define_prompt_template(template, template_args)
    print(prompt)
    response = llm.invoke(prompt)
    print(response)
