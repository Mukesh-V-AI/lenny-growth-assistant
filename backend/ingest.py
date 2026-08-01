import os
import subprocess
import glob
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from dotenv import load_dotenv

load_dotenv()

REPO_URL = "https://github.com/ChatPRD/lennys-podcast-transcripts.git"
CLONE_DIR = "./temp_transcripts4"
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/lenny_growth")

def parse_markdown_with_frontmatter(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Simple frontmatter parsing
    guest = "Unknown Guest"
    title = "Unknown Episode"
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter = parts[1]
            content = parts[2]
            
            for line in frontmatter.split('\n'):
                if line.startswith('guest:'):
                    guest = line.replace('guest:', '').strip()
                elif line.startswith('title:'):
                    title = line.replace('title:', '').strip()
                    
    return content, guest, title

import re

def semantic_dialogue_chunker(text, chunk_size=1000):
    # Split by the speaker prefix e.g., "Lenny (00:01:19):"
    turns = re.split(r'\n(?=.*? \(\d{2}:\d{2}:\d{2}\):)', text)
    chunks = []
    current_chunk = ""
    for turn in turns:
        if len(current_chunk) + len(turn) > chunk_size and current_chunk != "":
            chunks.append(current_chunk.strip())
            current_chunk = turn
        else:
            current_chunk += "\n" + turn
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def ingest_transcripts():
    print("Cloning repository locally...")
    if not os.path.exists(CLONE_DIR):
        subprocess.run(["git", "clone", REPO_URL, CLONE_DIR], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("Loading transcripts from local directory...")
    # Load ALL files from the repo as requested
    search_pattern = os.path.join(CLONE_DIR, '**', '*.md')
    file_paths = glob.glob(search_pattern, recursive=True)
    
    print(f"Found {len(file_paths)} episode transcripts.")
    
    all_chunks = []
    
    print("Parsing and chunking documents with metadata injection...")
    for path in file_paths:
        text, guest, title = parse_markdown_with_frontmatter(path)
        
        # Split the text semantically
        raw_chunks = semantic_dialogue_chunker(text, chunk_size=1200)
        
        for i, chunk_text in enumerate(raw_chunks):
            # Inject metadata directly into the chunk text so the LLM and Embedding Model can read it
            enriched_text = f"Episode Title: {title}\nGuest: {guest}\n\n{chunk_text}"
            
            doc = Document(
                page_content=enriched_text,
                metadata={"source": path, "guest": guest, "chunk_id": i}
            )
            all_chunks.append(doc)
            
    print(f"Created a total of {len(all_chunks)} semantic chunks.")

    print("Configuring Lightning-Fast HuggingFace Embeddings...")
    from langchain_huggingface import HuggingFaceEmbeddings
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    print("Connecting to Supabase...")
    from supabase.client import Client, create_client
    from langchain_community.vectorstores import SupabaseVectorStore
    
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not supabase_url or not supabase_key:
        raise ValueError("Missing SUPABASE_URL or SUPABASE_SERVICE_KEY in .env")
        
    supabase: Client = create_client(supabase_url, supabase_key)
    
    print("Writing to Supabase Vector Database in batches of 500...")
    
    vectorstore = SupabaseVectorStore(
        client=supabase,
        embedding=embeddings,
        table_name="documents",
        query_name="hybrid_search_documents"
    )
    
    batch_size = 500
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i:i + batch_size]
        print(f"Inserting batch {i//batch_size + 1}/{(len(all_chunks)//batch_size) + 1} ({len(batch)} chunks)...")
        # Ensure strict structured schema is applied
        for doc in batch:
            doc.metadata = {
                "document_type": "episode" if "episodes" in doc.metadata.get("source", "") else "index",
                "title": doc.metadata.get("title", "Unknown"),
                "guest": doc.metadata.get("guest", "None"),
                "source": doc.metadata.get("source", "Unknown"),
                "chunk_id": doc.metadata.get("chunk_id", 0)
            }
        vectorstore.add_documents(batch)
        
    print("Ingestion complete!")

if __name__ == "__main__":
    ingest_transcripts()
