import os
from supabase.client import Client, create_client
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
load_dotenv()
supabase_url = os.environ.get('SUPABASE_URL')
supabase_key = os.environ.get('SUPABASE_SERVICE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)
embeddings = HuggingFaceEmbeddings(model_name='all-MiniLM-L6-v2')
query = 'What are the biggest mistakes early-stage startups make when trying to scale their growth, according to Casey Winters?'
print('Embedding...')
query_vector = embeddings.embed_query(query)
print('Searching...')
try:
    res = supabase.rpc('hybrid_search_documents', {'query_text': query, 'query_embedding': query_vector, 'match_count': 5}).execute()
    print('Found chunks:', len(res.data))
except Exception as e:
    print('Error:', e)
