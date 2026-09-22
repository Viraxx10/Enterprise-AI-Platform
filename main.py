import io
import os
from dotenv import load_dotenv

load_dotenv()

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
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# 1. App & Rate Limiting Setup
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Enterprise AI Platform API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# JWT Security Configurations
SECRET_KEY = "SUPER_SECRET_JWT_KEY_CHANGE_IN_PRODUCTION"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Mock User Database (In production, load from PostgreSQL/SQLite)
FAKE_USERS_DB = {
    "admin": {
        "username": "admin",
        "hashed_password": pwd_context.hash("admin123"),
        "role": "admin"
    },
    "user": {
        "username": "user",
        "hashed_password": pwd_context.hash("user123"),
        "role": "standard"
    }
}
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None:
            raise credentials_exception
        return {"username": username, "role": role}
    except JWTError:
        raise credentials_exception

def require_admin(current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this action."
        )
    return current_user

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = FAKE_USERS_DB.get(form_data.username)
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"]}

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
def reset_kb(admin_user: dict = Depends(require_admin)):
    success = purge_knowledge_base()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to purge ChromaDB.")
    return {"status": "success", "message": f"Knowledge base purged by admin '{admin_user['username']}'."}

@app.get("/audit-logs")
def fetch_audit_logs(admin_user: dict = Depends(require_admin)):
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