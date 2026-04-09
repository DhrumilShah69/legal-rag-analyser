# rag_engine.py
# Updated to use the new google-genai package

import PyPDF2
from google import genai
import os
from vector_store import VectorStore

class RAGEngine:
    def __init__(self):
        # New google-genai client
        self.genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        self.vector_store = VectorStore()
    
    def extract_text(self, pdf_path: str) -> str:
        text = ""
        with open(pdf_path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"\n[Page {page_num + 1}]\n{page_text}"
        return text

    def split_into_chunks(self, text: str, chunk_size: int = 400, overlap: int = 50) -> list[str]:
        words = text.split()
        chunks = []
        i = 0
        while i < len(words):
            chunk = " ".join(words[i : i + chunk_size])
            chunks.append(chunk)
            i += chunk_size - overlap
        return chunks

    def process_document(self, pdf_path: str, document_id: str) -> int:
        print(f"Extracting text from {pdf_path}...")
        text = self.extract_text(pdf_path)
        
        print(f"Splitting into chunks...")
        chunks = self.split_into_chunks(text)
        print(f"Created {len(chunks)} chunks")
        
        print(f"Generating embeddings and storing in ChromaDB...")
        self.vector_store.add_chunks(document_id, chunks)
        
        return len(chunks)

    def answer_question(self, document_id: str, question: str, top_k: int = 5) -> dict:
        relevant_chunks = self.vector_store.search(document_id, question, top_k)
        
        if not relevant_chunks:
            return {
                "answer": "No relevant information found in the document.",
                "sources": [],
                "document_id": document_id
            }
        
        context = "\n\n---\n\n".join([
            f"[Excerpt {i+1}]\n{chunk}" 
            for i, chunk in enumerate(relevant_chunks)
        ])
        
        prompt = f"""You are a legal document analyst. Your job is to answer questions 
about legal documents accurately and clearly.

Here are the most relevant excerpts from the document:

{context}

---

Important instructions:
- Answer ONLY based on the excerpts provided above
- If the answer is not in the excerpts, say "This information is not found in the provided document sections"
- Be precise and cite which excerpt your answer comes from
- Use simple language to explain legal terms

Question: {question}

Answer:"""

        # New SDK way of generating text
        response = self.genai_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        
        return {
            "answer": response.text,
            "sources": relevant_chunks,
            "document_id": document_id
        }
    
    def list_documents(self) -> list[str]:
        return self.vector_store.list_collections()
    
    def delete_document(self, document_id: str) -> bool:
        return self.vector_store.delete_collection(document_id)