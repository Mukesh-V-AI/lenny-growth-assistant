import os
import uuid
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session as DBSession

from . import models, db
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
import anthropic
import openai as openai_sdk
from dotenv import load_dotenv

load_dotenv(override=True)

# Create tables if they don't exist
models.Base.metadata.create_all(bind=db.engine)

app = FastAPI(title="Lenny Growth Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/lenny_growth")

# Pydantic Schemas
class SessionCreate(BaseModel):
    title: str = "New Chat"

class SessionResponse(BaseModel):
    id: uuid.UUID
    title: str
    created_at: str

class ChatRequest(BaseModel):
    message: str
    llm_engine: str = "openrouter"  # or "openai" or "anthropic"
    skill: str = "qna" # or "ship30for30"

class ChatResponse(BaseModel):
    reply: str
    artifact: Optional[str] = None
    artifact_type: Optional[str] = None
    sources: Optional[list] = []
    latency_ms: Optional[int] = None

def get_vectorstore():
    # Use HuggingFace embeddings which are much faster locally
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return PGVector(
        collection_name="lenny_transcripts",
        connection_string=DATABASE_URL,
        embedding_function=embeddings,
    )

def generate_response(engine: str, system_prompt: str, history: list, user_prompt: str) -> str:
    # Build the messages array for OpenAI-compatible APIs
    openai_messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        openai_messages.append({"role": msg["role"], "content": msg["content"]})
    openai_messages.append({"role": "user", "content": user_prompt})

    # Build the messages array for Anthropic (doesn't use system role in the messages array)
    anthropic_messages = []
    for msg in history:
        anthropic_messages.append({"role": msg["role"], "content": msg["content"]})
    anthropic_messages.append({"role": "user", "content": user_prompt})

    if engine == "anthropic":
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        message = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1500,
            temperature=0.7,
            system=system_prompt,
            messages=anthropic_messages
        )
        return message.content[0].text
    elif engine == "openrouter":
        client = openai_sdk.OpenAI(
            api_key=os.getenv("OPENROUTER_API_KEY").strip(),
            base_url="https://openrouter.ai/api/v1"
        )
        response = client.chat.completions.create(
            model="nvidia/nemotron-3-super-120b-a12b:free",
            messages=openai_messages
        )
        return response.choices[0].message.content
    elif engine == "openai":
        client = openai_sdk.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=openai_messages,
            temperature=0.7
        )
        return res.choices[0].message.content
    else:
        # Local Ollama using OpenAI compatible API
        client = openai_sdk.OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")
        res = client.chat.completions.create(
            model="llama3",
            messages=openai_messages,
            temperature=0.7
        )
        return res.choices[0].message.content

# Routes
@app.get("/sessions", response_model=List[SessionResponse])
def get_sessions(database: DBSession = Depends(db.get_db)):
    # For a real app, you'd filter by user_id
    sessions = database.query(models.Session).order_by(models.Session.created_at.desc()).all()
    return [{"id": s.id, "title": s.title, "created_at": s.created_at.isoformat()} for s in sessions]

@app.post("/sessions", response_model=SessionResponse)
def create_session(req: SessionCreate, database: DBSession = Depends(db.get_db)):
    # Ensure there's a dummy user for now
    user = database.query(models.User).first()
    if not user:
        user = models.User()
        database.add(user)
        database.commit()
    
    new_session = models.Session(user_id=user.id, title=req.title)
    database.add(new_session)
    database.commit()
    database.refresh(new_session)
    return {"id": new_session.id, "title": new_session.title, "created_at": new_session.created_at.isoformat()}

@app.get("/sessions/{session_id}/messages")
def get_messages(session_id: uuid.UUID, database: DBSession = Depends(db.get_db)):
    import json
    messages = database.query(models.Message).filter(models.Message.session_id == session_id).order_by(models.Message.created_at).all()
    res = []
    for m in messages:
        sources = []
        if m.sources_json:
            try:
                sources = json.loads(m.sources_json)
            except:
                pass
        res.append({
            "role": m.role, 
            "content": m.content, 
            "artifact": m.artifact_content, 
            "artifact_type": m.artifact_type,
            "sources": sources,
            "latency_ms": m.latency_ms,
            "llm_engine": m.llm_engine,
            "token_count": m.token_count
        })
    return res

@app.post("/sessions/{session_id}/chat", response_model=ChatResponse)
def chat(session_id: uuid.UUID, req: ChatRequest, database: DBSession = Depends(db.get_db)):
    try:
        # Update Session Title if it's the first message
        session = database.query(models.Session).filter(models.Session.id == session_id).first()
        if session and session.title == "New Chat":
            session.title = req.message[:30] + ("..." if len(req.message) > 30 else "")
            database.commit()

        # Save User Message
        user_msg = models.Message(session_id=session_id, role="user", content=req.message)
        database.add(user_msg)
        database.commit()

        # Fetch Chat History (last 10 messages)
        past_messages = database.query(models.Message).filter(
            models.Message.session_id == session_id,
            models.Message.id != user_msg.id # Exclude the message we just added
        ).order_by(models.Message.created_at.desc()).limit(10).all()
        
        # Reverse to chronological order
        past_messages.reverse()
        history = [{"role": m.role, "content": m.content} for m in past_messages]

        # RAG Context
        context = ""
        extracted_sources = []
        import time, json
        start_time = time.time()
        try:
            from supabase.client import Client, create_client
            from langchain_huggingface import HuggingFaceEmbeddings
            import os
            
            supabase_url = os.environ.get("SUPABASE_URL")
            supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
            supabase: Client = create_client(supabase_url, supabase_key)
            
            embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
            query_vector = embeddings.embed_query(req.message)
            
            response = supabase.rpc("hybrid_search_documents", {
                "query_text": req.message,
                "query_embedding": query_vector,
                "match_count": 3
            }).execute()
            
            with open("debug_search.log", "w") as f:
                f.write(f"Query: {req.message}\n")
                f.write(f"URL: {supabase_url}\n")
                f.write(f"Vector Len: {len(query_vector)}\n")
                f.write(f"Response Data Len: {len(response.data) if response and response.data else 'None'}\n")
            
            final_docs = [{"document": d["content"], "cmetadata": d["metadata"]} for d in response.data]
            
            # Build context string and extract UI sources using the structured schema
            context_parts = []
            for d in final_docs:
                doc_text = d["document"]
                meta = d["cmetadata"]
                
                # Leverage our new strictly typed structured schema!
                title = meta.get("title", "Unknown Episode")
                
                extracted_sources.append({
                    "title": title,
                    "url": meta.get("source", ""),
                    "timestamp": ""
                })
                context_parts.append(f"Source Title: {title}\nContent: {doc_text}")
                
            context = "\n\n".join(context_parts)
            
        except Exception as vec_err:
            import traceback
            with open("vector_error.log", "w") as f:
                f.write(traceback.format_exc())
            print("Vector store search failed:", vec_err)
            context = "No context available (RAG search failed)."
        
        system_prompt = f"""You are a helpful and intelligent AI built to answer product management and growth questions. You have access to a Knowledge Base consisting of transcripts from Lenny's Podcast.

Knowledge Base Context:
{context}

Please answer the user's question accurately but CONCISELY. 
1. Use the Knowledge Base Context to ground your answer whenever possible.
2. CRITICAL: NEVER hallucinate or generate URLs. ONLY cite the exact 'Source Title' provided in the context above. Do not include 'https://' links under any circumstances.
3. Keep your answers brief and to the point (under 3 short paragraphs) unless the user explicitly asks for a long, detailed guide.
4. If the exact answer is not available in the context, do not refuse to answer. Instead, use your best judgment to provide a short, helpful answer."""
        
        if req.skill == "ship30for30":
            system_prompt = f"""You are the Lenny Growth Assistant. Your task is to write a high-quality Ship30for30 essay using the provided context.

Follow this advanced AI writing protocol:
1. **Framework:** Use the "Hook → Context → Core Argument → Evidence/Examples → Counterpoint → CTA" structure.
2. **Format:** Output the essay in Markdown. It must be approx 1250 words. Use heavy bolding for scannability, bullet density, and plenty of white space.
3. **Voice:** Practical, authoritative, slightly contrarian, conversational, and ZERO fluff. Short punchy lines.
4. **Banned Words:** NEVER use "AI tells" like: delve, tapestry, unlock, symphony, dance, game-changer, deep dive, or leverage. Replace weak verbs with strong ones.
5. **Content:** Base the essay STRICTLY on the Knowledge Base Context below.

Return ONLY the clean markdown essay. DO NOT include any introductory or concluding pleasantries outside the essay itself.

Knowledge Base Context:
{context}"""
        
        # Generate Response using raw SDKs
        reply_text = generate_response(req.llm_engine, system_prompt, history, req.message)
        
        latency_ms = int((time.time() - start_time) * 1000)
        token_count = len(reply_text.split(" ")) # rough estimate for now

        artifact_content = None
        artifact_type = None
        final_reply = reply_text

        if req.skill == "ship30for30":
            artifact_content = reply_text
            artifact_type = "markdown"
            final_reply = "I have generated the Ship30for30 essay for you based on Lenny's insights."

        # Save AI Message
        ai_msg = models.Message(
            session_id=session_id, 
            role="assistant", 
            content=final_reply,
            has_artifact=(artifact_content is not None),
            artifact_content=artifact_content,
            artifact_type=artifact_type,
            sources_json=json.dumps(extracted_sources),
            latency_ms=str(latency_ms),
            llm_engine=req.llm_engine,
            token_count=str(token_count)
        )
        database.add(ai_msg)
        database.commit()
            
        return ChatResponse(
            reply=final_reply,
            artifact=artifact_content,
            artifact_type=artifact_type,
            sources=extracted_sources,
            latency_ms=latency_ms
        )
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
