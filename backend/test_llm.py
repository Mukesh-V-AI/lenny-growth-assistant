import time, requests
url = 'http://localhost:11434/api/generate'
data = {'model': 'llama3', 'prompt': "What is Ada Chen Rekhi's curiosity loop? Explain in 100 words.", 'stream': False}
start = time.time()
try:
    res = requests.post(url, json=data, timeout=120)
    elapsed = time.time() - start
    print(f'Time taken: {elapsed:.2f} seconds')
    print('Response:', res.json().get('response', 'No response field'))
except Exception as e:
    print(f'Error: {e}')
