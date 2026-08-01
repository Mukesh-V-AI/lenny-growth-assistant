# Product Requirements Document (PRD)
## The Lenny Growth Assistant

### 1. Overview
**The Lenny Growth Assistant** is an advanced, production-ready, full-stack AI conversational workspace. It acts as a specialized junior partner for Product Managers and Growth Engineers, trained exclusively on the transcripts of *Lenny's Podcast*. It enables users to ask complex questions, synthesize insights, and instantly generate high-quality, formatted essays and UI components within an immersive side-by-side workspace.

### 2. Target Persona
- **Product Managers (Early-to-Senior):** Seeking rapid, grounded advice on growth frameworks, retention strategies, and leadership directly from industry experts (e.g., Adam Fishman, Ada Chen Rekhi).
- **Growth Engineers / Marketers:** Looking to rapidly synthesize complex product insights into highly formatted, actionable content (like Ship30for30 essays or LinkedIn threads) without wasting time fighting generic AI outputs.

### 3. Core Objectives
1. **100% Grounded Q&A:** The assistant must *never* hallucinate using general training data. Every answer must be strictly derived from the podcast transcripts and properly cited.
2. **Advanced Skill System (Ship30for30):** The assistant must encode human taste. Instead of generating generic prose, it must use the "Hook → Concept → Evidence → Application → CTA" framework to produce 1250-word atomic essays.
3. **Immersive UI/UX:** Users should not need to copy/paste code or markdown to visualize it. The application must feature a live Interactive Artifact Workbench that renders HTML, CSS, and Markdown side-by-side with the chat.
4. **LLM Agnosticism:** Users must be able to securely switch between local, private models (Ollama) and high-power cloud models (Anthropic, OpenAI) instantly.

### 4. Functional Requirements

#### 4.1 Knowledge Base & Retrieval (RAG)
- **Ingestion:** The system must fetch and parse markdown transcripts from `github.com/ChatPRD/lennys-podcast-transcripts`.
- **Semantic Dialogue Chunking:** Transcripts must be parsed intelligently by speaker turns (e.g., `Lenny:`, `Guest:`) to preserve conversational context, avoiding blind character limits that sever questions from answers.
- **Vector Search:** The system must use high-speed embeddings (e.g., HuggingFace `all-MiniLM-L6-v2`) and PostgreSQL (`pgvector`) for extremely fast, local context retrieval.

#### 4.2 Agentic Skill Router
- **Q&A Routing:** General questions are routed to a strict RAG prompt that demands source citations.
- **Ship30for30 Routing:** Requests using this skill are routed to an advanced AI writing protocol, enforcing strict stylistic rules, banning filler words ("delve", "tapestry"), and outputting heavy markdown.

#### 4.3 Workspace UI & Artifacts
- **Split-Pane Architecture:** The left pane houses the conversational chat thread. The right pane houses the Artifact Viewer.
- **Dynamic Rendering:** The frontend must automatically detect markdown or code blocks in the assistant's payload and render them interactively in the right pane.

#### 4.4 Session Management
- **Persistence:** All chats, UI state, and user history must be persistently saved to PostgreSQL.
- **ChatGPT Parity:** Users must be able to start new sessions and retain context within the active thread.

### 5. Success Metrics
- **Retrieval Accuracy:** >95% of generated answers correctly cite the appropriate podcast guest/episode.
- **Hallucination Rate:** <1% of responses include information not present in the vector store.
- **Latency:** Local LLM (Ollama) time-to-first-token < 2 seconds. RAG Vector Search < 500ms.
