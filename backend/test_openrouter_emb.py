import os
from langchain_openai import OpenAIEmbeddings
from dotenv import load_dotenv
load_dotenv()
embeddings = OpenAIEmbeddings(model='nvidia/nemotron-3-embed-1b:free', openai_api_key=os.getenv('OPENROUTER_API_KEY'), openai_api_base='https://openrouter.ai/api/v1')
print(embeddings.embed_query('hello world'))
