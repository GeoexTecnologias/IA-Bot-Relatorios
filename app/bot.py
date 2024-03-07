import json
import re
import random_responses

def load_json(file):
    with open(file) as bot_responses:
        return json.load(bot_responses)
    
response_data = load_json('bot.json')

def get_response(input):
    split_message = re.split(r'\s+|[,;?!.-]\s*', input.lower())
    score_list = []
    
    for response in response_data:
        response_score = 0
        required_score = 0
        required_words = response['expected_words']
        
        if required_words:
            for word in split_message:
                if word in required_words:
                    response_score += 1
        if required_score == len(required_words):
            for word in split_message:
                if word in response['user_input']:
                    response_score += 1
                    
        score_list.append(response_score)
        
    best_response = max(score_list)
    response_index = score_list.index(best_response)
    
    if input == "":
        return random_responses.random_string()

    if best_response != 0:
        return response_data[response_index]['bot_response']
    
    
    return random_responses.random_string()
        
def is_gerar_relatorio(input):
    input = input.lower()
    required_words = ['gerar', 'relatorio', 'relatório']
    n_project = re.findall(r'\d+', input)
    input_score = 0
    required_score = 2
    for word in required_words:
        if word in input:
            input_score += 1
    if input_score == required_score and n_project:
        return True
    else:
        return False

while True:
    user_input = input("Você: ")
    if is_gerar_relatorio(user_input):
        print("Geoex Report AI: Relatório gerado com sucesso! Tem mais alguma coisa que eu possa ajudar?")
        continue
    response = get_response(user_input)
    print("Geoex Report AI: " + response)