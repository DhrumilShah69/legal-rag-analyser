# vector_store.py
# Updated to use the new google-genai package

import chromadb
from google import genai
from google.genai import types
import os

class VectorStore:
    def __init__(self):
        # Persistent ChromaDB — saves to disk so data survives restarts
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # New google-genai client
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    
    def get_or_create_collection(self, document_id: str):
        return self.client.get_or_create_collection(
            name=document_id,
            metadata={"hnsw:space": "cosine"}
        )
    
    def get_embedding(self, text: str) -> list:
        # New SDK way of generating embeddings
        result = self.genai_client.models.embed_content(
            model="gemini-embedding-001",
            contents=text
        )
        return result.embeddings[0].values
    
    def add_chunks(self, document_id: str, chunks: list[str]):
        collection = self.get_or_create_collection(document_id)
        
        embeddings = []
        for chunk in chunks:
            embedding = self.get_embedding(chunk)
            embeddings.append(embedding)
        
        collection.add(
            documents=chunks,
            embeddings=embeddings,
            ids=[f"{document_id}_chunk_{i}" for i in range(len(chunks))]
        )
    
    def search(self, document_id: str, question: str, top_k: int = 5) -> list[str]:
        collection = self.get_or_create_collection(document_id)
        query_embedding = self.get_embedding(question)
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=min(top_k, collection.count())
        )
        return results["documents"][0] if results["documents"] else []
    
    def delete_collection(self, document_id: str):
        try:
            self.client.delete_collection(document_id)
            return True
        except:
            return False
    
    def list_collections(self) -> list[str]:
        return [col.name for col in self.client.list_collections()]