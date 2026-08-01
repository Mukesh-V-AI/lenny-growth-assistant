# Lenny Growth Assistant 🚀

An Agentic AI Engineer internship project built by a final-year student at CIT, Coimbatore.

The Lenny Growth Assistant is a full-stack, AI-powered conversational web application. It acts as an intelligent junior partner, trained specifically on the transcripts of *Lenny's Podcast*, to answer complex Product Management and Growth questions. 

Beyond standard conversational Q&A, the assistant features a highly specialized **Ship30for30 Content Generator** skill that synthesizes insights into perfectly formatted, 1250-word essays right before your eyes in a built-in Artifact Viewer workspace.

## 🌟 Key Features
- **Strict Semantic RAG:** Ingests 37,000+ conversational podcast chunks. The backend utilizes a custom Semantic Dialogue Chunker to ensure the AI never loses conversational context, answering strictly from Lenny's transcripts.
- **Ship30for30 Generation Engine:** Uses advanced "Chain of Thought" prompting to architect, formulate, and output 1250-word Markdown essays strictly adhering to the Hook → Concept → Evidence format.
- **Native Artifact Viewer UI:** Automatically detects when the AI generates Markdown or HTML/CSS, rendering it beautifully side-by-side with the chat.
- **Engine Agnostic:** Seamlessly toggle between Cloud AI models (Anthropic Claude, OpenAI, OpenRouter) and Local LLMs (Ollama) instantly from the UI.
- **Persistent Sessions:** Full ChatGPT-style session management stored persistently via PostgreSQL.

## 🛠 Architecture & Tech Stack
- **Frontend:** Next.js + React. Features a beautiful glassmorphic UI, responsive split-pane Artifact Viewer, and real-time LLM dropdown toggling.
- **Backend API:** FastAPI. Handles LLM orchestration, session management, Agentic Skill routing (Q&A vs. Ship30for30), and database operations.
- **Database:** PostgreSQL (pgvector). Stores Chat History, Sessions, and 384-dimensional HuggingFace vector embeddings.
- **AI Models:** Integrates deeply with Anthropic SDK, OpenAI SDK, and Ollama Local Models.
- **Vector Embeddings:** `all-MiniLM-L6-v2` via HuggingFace for lightning-fast semantic local search.

## 🚀 Local Deployment Instructions

Follow these steps to test the application locally on your machine.

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL (with `pgvector` extension enabled)
- Ollama (running locally with `llama3` pulled)

### 2. Database Setup
Create a local PostgreSQL database named `lenny_growth` (for storing user chat sessions locally).
For the Vector RAG database, create a Supabase project and enable the `vector` extension. Run the provided SQL migration scripts to create the `documents` table and the `hybrid_search_documents` RPC function.

### 3. Backend Setup
Navigate to the backend directory and set up your virtual environment:
```bash
cd backend
python -m venv venv
source venv/Scripts/activate  # On Windows
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` directory:
```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/lenny_growth
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
OPENROUTER_API_KEY=your_openrouter_key
```

### 4. Vector Database Ingestion
To populate the RAG database with Lenny's transcripts, run the custom ingestion script. This will clone the transcripts and batch-insert them into the PostgreSQL vector store:
```bash
python ingest.py
```
*(Note: This process takes ~2-5 minutes depending on your CPU).*

### 5. Run the Backend API
```bash
uvicorn app.main:app --reload --port 8000
```
The FastAPI backend will now be running on `http://localhost:8000`.

### 6. Run the Frontend Application
In a new terminal window, navigate to the frontend directory:
```bash
cd frontend
npm install
npm run dev
```
The application will launch on `http://localhost:3000`. 

## 🤖 Testing the Application
1. **Local LLM Test:** Open the UI, select "Ollama (llama3)" from the dropdown, and ask a product management question. The assistant will query the local LLM and retrieve insights strictly from the transcripts.
2. **Ship30for30 Test:** Click the "Ship30for30" skill toggle and prompt the AI to write an essay on Product-Market Fit. The AI will generate a highly structured markdown essay, which will render instantly in the side-by-side Artifact Viewer.
