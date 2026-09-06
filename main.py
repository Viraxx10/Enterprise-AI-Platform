import io
import os
from fastapi import FastAPI, File, UploadFile, Security, Depends, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from pydantic import BaseModel
from pypdf import PdfReader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from ml_engine import predict_customer_churn, search_knowledge_base, ingest_document_text

# 1. Rate Limiting Setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Enterprise AI Platform API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 2. API Key Authentication Setup
API_KEY_NAME = "X-API-Key"
EXPECTED_API_KEY = os.getenv("API_KEY", "ENTERPRISE_SECRET_KEY_2026")
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API Key"
        )
    return api_key

class ChurnRequest(BaseModel):
    credit_score: int
    age: int
    tenure: int
    balance: float
    num_products: int

@app.get("/")
def root():
    return {
        "status": "healthy",
        "message": "Enterprise AI Platform API is live",
        "docs": "/docs"
    }

@app.post("/predict-churn")
@limiter.limit("10/minute")
def predict_churn(request: Request, data: ChurnRequest, key: str = Depends(verify_api_key)):
    risk_label, churn_prob = predict_customer_churn(
        data.credit_score,
        data.age,
        data.tenure,
        data.balance,
        data.num_products
    )
    return {"prediction": risk_label, "churn_probability": churn_prob}

@app.get("/search-docs")
@limiter.limit("15/minute")
def search_docs(request: Request, query: str, key: str = Depends(verify_api_key)):
    return search_knowledge_base(query)

@app.post("/upload-doc")
@limiter.limit("5/minute")
def upload_document(request: Request, file: UploadFile = File(...), key: str = Depends(verify_api_key)):
    content = file.file.read()
    extracted_text = ""

    if file.filename.endswith(".pdf"):
        pdf_reader = PdfReader(io.BytesIO(content))
        for page in pdf_reader.pages:
            text = page.extract_text()
            if text:
                extracted_text += text + "\n"
    else:
        extracted_text = content.decode("utf-8", errors="ignore")

    if not extracted_text.strip():
        return {"status": "error", "message": "No readable text found in document."}

    chunk_count = ingest_document_text(extracted_text, file.filename)
    return {
        "status": "success",
        "filename": file.filename,
        "chunks_added": chunk_count
    }