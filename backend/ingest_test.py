import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores.pgvector import PGVector
from dotenv import load_dotenv

load_dotenv()

loader = TextLoader('./temp_transcripts4/episodes/ada-chen-rekhi/transcript.md', encoding='utf-8')
docs = loader.load()
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(docs)
embeddings = OllamaEmbeddings(model='nomic-embed-text')
PGVector.from_documents(embedding=embeddings, documents=chunks, collection_name='lenny_transcripts', connection_string=os.getenv('DATABASE_URL'), pre_delete_collection=False)
print('Ada Chen Rekhi embedded successfully!')
