# models.py
# This file defines the "shape" of data that our API accepts and returns.
# Pydantic automatically validates the data — if someone sends wrong data,
# FastAPI returns a clear error message automatically.

from pydantic import BaseModel
from typing import Optional

# When someone asks a question, the request body must look like this
class QuestionRequest(BaseModel):
    question: str                        # The question text — required
    document_id: Optional[str] = None   # Which document to search — optional
    top_k: int = 5                       # How many chunks to retrieve — default 5

# When our API answers a question, the response will look like this
class QuestionResponse(BaseModel):
    answer: str                  # The actual answer from Gemini
    sources: list[str]           # The exact chunks used to generate the answer
    document_id: str             # Which document was searched

# When a document is uploaded successfully, we return this
class DocumentResponse(BaseModel):
    document_id: str             # Unique ID we assign to the document
    filename: str                # Original filename
    chunk_count: int             # How many chunks it was split into
    message: str                 # Success message