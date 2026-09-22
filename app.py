import os
import requests
import streamlit as st

# Uses Docker service name 'backend' in containers, falls back to localhost for manual runs
API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
HEADERS = {"X-API-Key": "ENTERPRISE_SECRET_KEY_2026"}

st.set_page_config(
    page_title="Enterprise AI Platform", page_icon="🤖", layout="wide"
)

st.title("🤖 Enterprise AI Platform")
st.markdown(
    "Dashboard connecting to **FastAPI**, **Scikit-Learn**, **ChromaDB**, and"
    " **Groq**."
)

st.sidebar.header("Navigation")
page = st.sidebar.radio(
    "Select Engine",
    ["ML Customer Risk Predictor", "AI Knowledge Assistant (RAG)", "Audit & System Logs"],
)

# 1. ML CUSTOMER RISK PREDICTOR
if page == "ML Customer Risk Predictor":
  st.subheader("📊 Customer Churn Risk Assessment")
  st.write(
      "Submit customer details to get a live prediction from the Random Forest"
      " model."
  )

  col1, col2 = st.columns(2)
  with col1:
    credit_score = st.number_input(
        "Credit Score", min_value=300, max_value=850, value=650
    )
    age = st.number_input("Age", min_value=18, max_value=100, value=42)
    tenure = st.number_input(
        "Tenure (Years)", min_value=0, max_value=10, value=3
    )

  with col2:
    balance = st.number_input(
        "Account Balance ($)", min_value=0.0, value=50000.0, step=1000.0
    )
    num_products = st.selectbox(
        "Number of Products Used", options=[1, 2, 3, 4], index=0
    )

  if st.button("Predict Churn Risk", type="primary"):
    payload = {
        "credit_score": credit_score,
        "age": age,
        "tenure": tenure,
        "balance": balance,
        "num_products": num_products,
    }
    try:
      response = requests.post(f"{API_URL}/predict-churn", json=payload, headers=HEADERS)
      if response.status_code == 200:
        data = response.json()
        risk = data["prediction"]
        prob = data["churn_probability"]
        if risk == "High Risk":
          st.error(f"⚠️ **Result:** {risk} | **Churn Probability:** {prob}%")
        else:
          st.success(f"✅ **Result:** {risk} | **Churn Probability:** {prob}%")
      else:
        st.error(f"Server returned error code: {response.status_code}")
    except requests.exceptions.ConnectionError:
      st.error(
          "⚠️ Connection Error: Ensure FastAPI server is running on"
          " http://127.0.0.1:8000"
      )

# 2. AI KNOWLEDGE ASSISTANT (RAG)
elif page == "AI Knowledge Assistant (RAG)":
    st.subheader("🔍 Enterprise Knowledge Assistant")

    # Dynamic Document Upload Section
    st.markdown("#### 📂 Ingest Documents into ChromaDB")
    uploaded_files = st.file_uploader(
        "Upload Policy or Technical Documents (Batch Supported)", 
        type=["txt", "pdf"], 
        accept_multiple_files=True
    )

    if uploaded_files and st.button("Ingest Documents", type="secondary"):
        with st.spinner("Chunking text and generating vector embeddings..."):
            for uploaded_file in uploaded_files:
                try:
                    files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                    response = requests.post(f"{API_URL}/upload-doc", headers=HEADERS, files=files)
                    if response.status_code == 200:
                        info = response.json()
                        st.success(f"✅ Ingested `{info.get('filename')}` ({info.get('chunks_added', 0)} chunks added).")
                    else:
                        st.error(f"Failed to ingest `{uploaded_file.name}`: {response.text}")
                except Exception as e:
                    st.error(f"Upload error on `{uploaded_file.name}`: {e}")

    st.markdown("---")
    st.markdown("#### 💬 Enterprise Q&A Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    col1, col2 = st.columns([6, 1])
    with col2:
        if st.button("🧹 Clear Chat"):
            st.session_state.chat_history = []
            st.rerun()

    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question based on uploaded policies..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Analyzing context and drafting response..."):
                try:
                    payload = {
                        "query": prompt,
                        "history": st.session_state.chat_history[:-1]
                    }
                    res = requests.post(f"{API_URL}/query", json=payload, headers=HEADERS)
                    if res.status_code == 200:
                        ans_data = res.json()
                        bot_reply = ans_data.get("answer", "No answer received.")
                        st.markdown(bot_reply)
                        st.session_state.chat_history.append({"role": "assistant", "content": bot_reply})
                    else:
                        st.error(f"Error {res.status_code}: {res.text}")
                except Exception as ex:
                    st.error(f"Failed to connect to backend: {ex}")

# --- SIDEBAR: Document Management ---
st.sidebar.title("📚 Knowledge Base")

if st.sidebar.button("🔄 Refresh Stats"):
    st.rerun()

try:
    stats_res = requests.get(f"{API_URL}/kb-stats", headers=HEADERS)
    if stats_res.status_code == 200:
        stats = stats_res.json()
        st.sidebar.metric("Total Chunks", stats.get("total_chunks", 0))
        st.sidebar.caption("Indexed Files:")
        docs = stats.get("documents", [])
        if docs:
            for doc in docs:
                st.sidebar.markdown(f"- `{doc}`")
        else:
            st.sidebar.write("No documents indexed.")
except Exception:
    st.sidebar.error("Could not fetch KB stats.")

st.sidebar.markdown("---")

if st.sidebar.button("🗑️ Purge Knowledge Base", type="primary"):
    purge_res = requests.delete(f"{API_URL}/purge-kb", headers=HEADERS)
    if purge_res.status_code == 200:
        st.sidebar.success("Database purged!")
        st.rerun()
    else:
        st.sidebar.error("Purge failed.")
        
# 3. AUDIT & SYSTEM LOGS
elif page == "Audit & System Logs":
    st.subheader("🛡️ Enterprise Audit & Request Logs")
    st.caption("Live latency, route tracking, and status monitoring from FastAPI middleware.")

    if st.button("🔄 Refresh Logs"):
        st.rerun()

    try:
        log_res = requests.get(f"{API_URL}/audit-logs", headers=HEADERS)
        if log_res.status_code == 200:
            data = log_res.json()
            st.metric("Total Logged Requests", data.get("total_records", 0))
            logs = data.get("logs", [])
            if logs:
                st.dataframe(logs, use_container_width=True)
            else:
                st.info("No audit logs recorded yet.")
        else:
            st.error(f"Failed to fetch logs: {log_res.status_code}")
    except Exception as e:
        st.error(f"Could not connect to backend audit service: {e}")