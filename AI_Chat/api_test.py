import requests
import json


data = {
    "user_question": "Quantos os projetos estao programados para a carteira de obras de maio"
}

response = requests.post(
    url, data=json.dumps(data), headers={"Content-Type": "application/json"}
)

print(response.status_code)
