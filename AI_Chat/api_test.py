import requests
import json

url = "http://127.0.0.1:8000/generate-response"  # replace with your server's URL
data = {
    "user_question": "Quantos os projetos estao programados para a carteira de obras de maio"
}

response = requests.post(
    url, data=json.dumps(data), headers={"Content-Type": "application/json"}
)

print(response.status_code)
