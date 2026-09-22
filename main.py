import io
import os
from fastapi import FastAPI, File, UploadFile, Security, Depends, HTTPException, status, Request
from fastapi.security import APIKeyHeader
from pypdf import PdfReader
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from typing import List, Dict, Optional
from pydantic import BaseModel
import json
import logging
import time
from datetime import datetime

# Configure Structured Enterprise Logger
logging.basicConfig(
    filename="audit.log",
    level=logging.INFO,
    format="%(message)s"
)
audit_logger = logging.getLogger("audit")

class RAGQueryRequest(BaseModel):
    query: str
    history: Optional[List[Dict[str, str]]] = []

from ml_engine import (
    predict_customer_churn, 
    search_knowledge_base, 
    ingest_document_text, 
    get_knowledge_base_stats, 
    purge_knowledge_base
)

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

@app.post("/query")
@limiter.limit("15/minute")
def answer_query(request: Request, payload: RAGQueryRequest, key: str = Depends(verify_api_key)):
    try:
        return search_knowledge_base(payload.query, chat_history=payload.history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
    
@app.get("/kb-stats")
def kb_stats(key: str = Depends(verify_api_key)):
    return get_knowledge_base_stats()

@app.delete("/purge-kb")
def reset_kb(key: str = Depends(verify_api_key)):
    success = purge_knowledge_base()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to purge ChromaDB.")
    return {"status": "success", "message": "Knowledge base purged successfully."}

@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time_ms = round((time.time() - start_time) * 1000, 2)

    log_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "client_ip": request.client.host if request.client else "unknown",
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code,
        "latency_ms": process_time_ms,
    }

    audit_logger.info(json.dumps(log_entry))
    return response

@app.get("/audit-logs")
def fetch_audit_logs(key: str = Depends(verify_api_key)):
    logs = []
    if os.path.exists("audit.log"):
        with open("audit.log", "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
    return {"total_records": len(logs), "logs": logs[-50:]}