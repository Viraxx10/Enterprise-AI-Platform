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
    ["ML Customer Risk Predictor", "AI Knowledge Assistant (RAG)"],
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
  uploaded_file = st.file_uploader(
      "Upload a PDF or TXT policy document:", type=["pdf", "txt"]
  )

  if uploaded_file is not None:
    if st.button("Ingest Document", type="secondary"):
      with st.spinner("Chunking text and generating vector embeddings..."):
        try:
          files = {
              "file": (
                  uploaded_file.name,
                  uploaded_file.getvalue(),
                  uploaded_file.type,
              )
          }
          response = requests.post(f"{API_URL}/upload-doc", 
             files={"file": (uploaded_file.name, uploaded_file.getvalue())},headers=HEADERS)
          if response.status_code == 200:
            info = response.json()
            st.success(
                f"✅ Successfully ingested `{info['filename']}`"
                f" ({info['chunks_added']} chunks indexed)."
            )
          else:
            st.error(f"Failed to ingest document. Code: {response.status_code}")
        except Exception as e:
          st.error(f"Upload error: {e}")

  st.markdown("---")
  st.markdown("#### 💬 Ask Questions")
  query = st.text_input(
      "Enter your question:",
      placeholder="e.g., How do we handle accounts that are inactive for more than 90 days?",
  )

  if st.button("Submit Question", type="primary"):
        if query.strip():
            with st.spinner("Searching ChromaDB and synthesizing answer with Groq..."):
                try:
                    response = requests.get(f"{API_URL}/search-docs", params={"query": query}, headers=HEADERS)
                    if response.status_code == 200:
                        result = response.json()
                        st.markdown("### Answer")
                        st.info(result.get("answer", "No response received."))
                        
                        sources = result.get("sources", [])
                        if sources:
                            st.markdown("#### 📚 Reference Citations")
                            for idx, src in enumerate(sources, start=1):
                                with st.expander(f"Source {idx}: {src.get('document')} (Chunk {src.get('chunk_index')})"):
                                    st.caption(f"**Extracted Text Snippet:**")
                                    st.write(f"> {src.get('snippet')}")
                        else:
                            st.caption("No external source metadata available.")
                    else:
                        st.error(f"Server returned error code: {response.status_code}")
                except requests.exceptions.ConnectionError:
                    st.error("⚠️ Connection Error: Ensure FastAPI server is running on http://127.0.0.1:8000")
        else:
            st.warning("Please type a question before submitting.")