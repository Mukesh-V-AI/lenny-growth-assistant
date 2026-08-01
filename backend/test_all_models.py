import os
import sys
from dotenv import load_dotenv

# Load env before importing main
load_dotenv(override=True)

# Add backend to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.main import generate_response

system_prompt = "You are a helpful assistant. Reply with only the word 'SUCCESS'."
history = []
user_prompt = "Hello!"

models = ["openrouter", "openai", "anthropic", "ollama"]

for model in models:
    print(f"\n--- Testing {model.upper()} ---")
    try:
        response = generate_response(model, system_prompt, history, user_prompt)
        print(f"SUCCESS: {response.strip()}")
    except Exception as e:
        print(f"ERROR: {e}")
