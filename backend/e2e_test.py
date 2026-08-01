import requests, time
print('--- Starting E2E RAG Test ---')
print('1. Creating Session...')
res = requests.post('http://localhost:8000/sessions', json={'title': 'Test Session'}, timeout=10)
session_id = res.json()['id']
print(f'Session ID: {session_id}')
print('2. Sending Query...')
start = time.time()
data = {'message': "What is Ada Chen Rekhi's curiosity loop?", 'llm_engine': 'openrouter', 'skill': 'none'}
chat_res = requests.post(f'http://localhost:8000/sessions/{session_id}/chat', json=data, timeout=120)
elapsed = time.time() - start
print(f'Time Taken: {elapsed:.2f} seconds')
print('Response:')
print(chat_res.json())
