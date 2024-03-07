import random

def random_string():
    random_responses = [
        "Olá, como posso ajudar? Sou um bot de geracao de relatorios. para gerar basta me informar 'Gerar relatorio' e o numero do projeto.",
        "Não entendi, poderia reformular? me informe 'Gerar relatorio' e o numero do projeto.",
        "Me desculpe, não entendi. Poderia me informar 'Gerar relatorio' e o numero do projeto?",
        "Acho que não fui feito para entender isso. Poderia me informar 'Gerar relatorio' e o numero do projeto?",
    ]
    list_count = len(random_responses)
    random_index = random.randint(0, list_count - 1)
    return random_responses[random_index]
    