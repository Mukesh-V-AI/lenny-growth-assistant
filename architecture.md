# System Architecture

This document details the architectural decisions, database schema, agentic routing logic, and system interactions for the Lenny Growth Assistant.

## High-Level Workflow
1. **User Input:** The user sends a query from the Next.js frontend, optionally toggling the LLM engine or a specific "Skill" (e.g., Ship30for30).
2. **API Layer (FastAPI):** The backend receives the request via `/sessions/{session_id}/chat`.
3. **Database (PostgreSQL):** The user's message is persisted to the database. Previous chat history (last 10 messages) is retrieved.
4. **Vector Search (RAG):** The user's message is vectorized locally using HuggingFace (`all-MiniLM-L6-v2`) and queried against the PostgreSQL `pgvector` database to retrieve semantically grouped conversation turns from Lenny's transcripts.
5. **Agentic Routing:** The backend injects the context and history into the system prompt. Based on the selected "Skill", a distinct prompting framework is applied.
6. **LLM Engine:** The query is routed to the user's selected LLM Engine (Anthropic, OpenAI, OpenRouter, or Local Ollama).
7. **Response & UI Render:** The response is parsed. If it contains an artifact (like a Markdown essay), the backend tags it. The frontend dynamically renders the artifact in the side-by-side Artifact Viewer.

## Database Schema (PostgreSQL via SQLAlchemy)

The application relies on a robust relational structure to persist state and history:

- **Users Table:** 
  - `id` (UUID)
  - `email` (String, unique)
- **Sessions Table:**
  - `id` (UUID)
  - `user_id` (UUID, Foreign Key)
  - `title` (String) - Automatically generated based on the first message.
  - `created_at` (Timestamp)
- **Messages Table:**
  - `id` (UUID)
  - `session_id` (UUID, Foreign Key)
  - `role` (String) - `user` or `assistant`
  - `content` (Text) - The primary chat text.
  - `artifact_content` (Text, nullable) - Holds the generated code/markdown.
  - `artifact_type` (String, nullable) - e.g., `markdown`, `html`
  - `created_at` (Timestamp)

## Agentic Routing Logic

The FastAPI backend uses an intelligent routing mechanism to handle different requests:

### 1. The General Q&A Skill
- **Logic:** Injects retrieved context into a highly rigid system prompt.
- **Constraints:** The model is strictly instructed to answer *only* from the context. If the answer is not present, it must state it lacks the information. If it answers, it must explicitly cite the Source URLs. 
- **Relaxation:** The agent is trained to infer intent intelligently (e.g., matching episode titles to guest names).

### 2. The Ship30for30 Skill
- **Logic:** Triggers a massive system prompt overhaul based on advanced AI prompting playbooks.
- **Constraints:** Forces the AI to adopt a structural framework (Hook → Context → Core Argument → Evidence → Counterpoint → CTA). It bans typical AI filler words ("delve", "tapestry") and mandates a 1250-word length with heavy markdown bolding.
- **Routing:** Triggers the frontend's Artifact Viewer to display the resulting essay side-by-side.

## LLM Engine Toggle Switch

The system is completely engine-agnostic. The `generate_response()` function in `main.py` acts as a multiplexer:
- If `engine == 'anthropic'`: Uses the Anthropic SDK (`claude-3-5-sonnet-20240620`).
- If `engine == 'openai'`: Uses the OpenAI SDK (`gpt-4o`).
- If `engine == 'openrouter'`: Passes the request to OpenRouter (`meta-llama/llama-3.1-8b-instruct`).
- If `engine == 'ollama'`: Connects to the local `localhost:11434/v1` server using an OpenAI-compatible client wrapper, executing the local `llama3` model securely on the user's laptop for the demo submission.
