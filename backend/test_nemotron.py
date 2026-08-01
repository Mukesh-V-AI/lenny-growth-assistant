import os
import requests
from dotenv import load_dotenv
load_dotenv()
headers = {'Authorization': f'Bearer {os.getenv("OPENROUTER_API_KEY")}'}
data = {
    'model': 'nvidia/nemotron-3.5-content-safety:free',
    'messages': [
        {'role': 'system', 'content': 'You are a helpful assistant.'},
        {'role': 'user', 'content': 'What are the biggest mistakes early-stage startups make?'}
    ]
}
res = requests.post('https://openrouter.ai/api/v1/chat/completions', headers=headers, json=data)
print(res.json())
