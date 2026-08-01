import time
import subprocess
import requests
import json
import sys

def main():
    print("Testing integration end-to-end...")
    
    # 1. Start the API server in the background
    print("Starting backend API...")
    api_process = subprocess.Popen(
        [r"backend\venv\Scripts\python", "-m", "uvicorn", "backend.app.main:app", "--port", "8000"],
        cwd=r"E:\projects\B12 project\lenny-growth-assistant",
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    try:
        # Give it a few seconds to boot up and initialize the DB schema
        print("Waiting for server to start...")
        time.sleep(5)
        
        # 2. Test fetching sessions
        print("Testing GET /sessions")
        try:
            res = requests.get("http://localhost:8000/sessions")
            res.raise_for_status()
            print("  GET /sessions successful. Response:", res.json())
        except Exception as e:
            print("  GET /sessions failed:", e)
            sys.exit(1)
            
        # 3. Create a new session
        print("\nTesting POST /sessions")
        try:
            res = requests.post("http://localhost:8000/sessions", json={"title": "Integration Test Chat"})
            res.raise_for_status()
            session_data = res.json()
            session_id = session_data["id"]
            print("  POST /sessions successful. Created Session ID:", session_id)
        except Exception as e:
            print("  POST /sessions failed:", e)
            sys.exit(1)
            
        # 4. Send a Chat using Anthropic
        print(f"\nTesting POST /sessions/{session_id}/chat (Engine: Anthropic)")
        payload = {
            "message": "What is product led growth? Summarize in one sentence.",
            "llm_engine": "anthropic",
            "skill": "qna"
        }
        try:
            res = requests.post(f"http://localhost:8000/sessions/{session_id}/chat", json=payload)
            res.raise_for_status()
            chat_data = res.json()
            print("  Anthropic response:", chat_data["reply"])
        except Exception as e:
            print("  Anthropic Chat failed:", e)
            if hasattr(e, 'response') and e.response is not None:
                print("  Response body:", e.response.text)
                
        # 5. Send a Chat using OpenAI for Ship30for30
        print(f"\nTesting POST /sessions/{session_id}/chat (Engine: OpenAI, Skill: ship30for30)")
        payload = {
            "message": "Write an essay about the importance of activation metrics.",
            "llm_engine": "openai",
            "skill": "ship30for30"
        }
        try:
            res = requests.post(f"http://localhost:8000/sessions/{session_id}/chat", json=payload)
            res.raise_for_status()
            chat_data = res.json()
            print("  OpenAI response:", chat_data["reply"])
            print("  Artifact Generated? Type:", chat_data.get("artifact_type"))
            print("  Artifact Preview (first 100 chars):", str(chat_data.get("artifact"))[:100].replace('\n', ' '))
        except Exception as e:
            print("  OpenAI Chat failed:", e)
            if hasattr(e, 'response') and e.response is not None:
                print("  Response body:", e.response.text)

    finally:
        print("\nShutting down backend API...")
        api_process.terminate()

if __name__ == "__main__":
    main()
