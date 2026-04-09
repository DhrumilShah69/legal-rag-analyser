# main.py
# Updated to use the new google-genai package

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
import uuid
import shutil
from models import QuestionRequest, QuestionResponse, DocumentResponse
from rag_engine import RAGEngine

# ── App Setup ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="Legal Document Analyser API",
    description="Upload legal documents and ask questions about them using AI",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploaded_docs", exist_ok=True)

rag_engine = RAGEngine()


@app.get("/")
def root():
    return {"status": "running", "message": "Legal RAG API is live"}


@app.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")
    
    document_id = str(uuid.uuid4())[:8]
    pdf_path = f"uploaded_docs/{document_id}.pdf"
    
    with open(pdf_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    try:
        chunk_count = rag_engine.process_document(pdf_path, document_id)
        return DocumentResponse(
            document_id=document_id,
            filename=file.filename,
            chunk_count=chunk_count,
            message=f"Document processed successfully into {chunk_count} chunks"
        )
    except Exception as e:
        os.remove(pdf_path)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest):
    if not request.document_id:
        raise HTTPException(status_code=400, detail="document_id is required")
    
    try:
        result = rag_engine.answer_question(
            document_id=request.document_id,
            question=request.question,
            top_k=request.top_k
        )
        return QuestionResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents")
def list_documents():
    documents = rag_engine.list_documents()
    return {"documents": documents, "count": len(documents)}


@app.delete("/documents/{document_id}")
def delete_document(document_id: str):
    success = rag_engine.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": f"Document {document_id} deleted successfully"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)