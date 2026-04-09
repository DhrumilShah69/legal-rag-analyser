# Legal Document Analyser — AI-Powered RAG System

An intelligent document analysis system that lets you upload legal documents and ask questions about them in plain English. Built with FastAPI, ChromaDB, Gemini AI, and Streamlit.

## Architecture

PDF Upload → Text Extraction → Chunking → Embedding → ChromaDB Storage
                                                              ↓
User Question → Embed Question → Vector Search → Retrieved Chunks → Gemini AI → Answer

## Tech Stack

- Backend API: FastAPI
- Vector Database: ChromaDB
- AI Model: Google Gemini 2.5 Flash
- Embeddings: Gemini Embedding 001
- Frontend: Streamlit
- PDF Processing: PyPDF2

## Features

- Upload any PDF document
- Ask questions in plain English
- RAG pipeline retrieves only relevant document sections
- View source excerpts for every answer
- Multi-document support
- Delete documents from the vector store

## Setup

### 1. Clone the repository
git clone https://github.com/DhrumilShah69/legal-rag-analyser.git
cd legal-rag-analyser

### 2. Create virtual environment
python -m venv venv
venv\Scripts\activate

### 3. Install dependencies
pip install -r requirements.txt

### 4. Set your Gemini API key
$env:GEMINI_API_KEY="your-key-here"

### 5. Run the backend
cd backend
python main.py

### 6. Run the frontend (new terminal)
cd frontend
streamlit run app.py

Visit http://localhost:8501 to use the app.

## API Endpoints

- GET / — Health check
- POST /upload — Upload and process a PDF
- POST /ask — Ask a question about a document
- GET /documents — List all stored documents
- DELETE /documents/{id} — Delete a document

## How RAG Works

1. Ingestion — PDF is extracted, split into 400-word chunks with 50-word overlap
2. Embedding — Each chunk is converted to a vector using Gemini Embeddings
3. Storage — Vectors stored in ChromaDB with cosine similarity index
4. Retrieval — User question is embedded, top-5 similar chunks retrieved
5. Generation — Retrieved chunks + question sent to Gemini with strict grounding instructions

## Key Technical Decisions

- Chunk overlap — 50-word overlap prevents answers from being cut at chunk boundaries
- Cosine similarity — Measures semantic similarity between question and document chunks
- Grounded prompting — Gemini instructed to answer ONLY from retrieved context, preventing hallucination
