import os
import json
import time
import requests
import pandas as pd
import streamlit as st

# =====================================================================
# 1. PAGE CONFIGURATION & DESIGN SYSTEM INJECTION
# =====================================================================
st.set_page_config(
    page_title="Enterprise AI Platform v2",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed" if "token" not in st.session_state or not st.session_state.token else "expanded"
)

# Configuration & Environment Bindings
API_URL = os.getenv("BACKEND_URL", os.getenv("API_URL", "http://127.0.0.1:8000"))
API_KEY = os.getenv("API_KEY", "ENTERPRISE_SECRET_KEY_2026")

# Session State Initialization
if "token" not in st.session_state:
    st.session_state.token = None
if "role" not in st.session_state:
    st.session_state.role = None
if "username" not in st.session_state:
    st.session_state.username = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "login_username_input" not in st.session_state:
    st.session_state.login_username_input = "admin"
if "login_password_input" not in st.session_state:
    st.session_state.login_password_input = "admin123"

# Load External CSS Design System
css_path = os.path.join(os.path.dirname(__file__), "style.css")
if os.path.exists(css_path):
    with open(css_path, "r", encoding="utf-8") as f:
        custom_css = f.read()
        # If logged out, hide sidebar to make login dashboard full-width
        if not st.session_state.token:
            custom_css += """
            section[data-testid="stSidebar"] {
                display: none !important;
            }
            """
        st.markdown(f"<style>{custom_css}</style>", unsafe_allow_html=True)

# Helper function to perform login
def perform_login(username, password):
    try:
        res = requests.post(
            f"{API_URL}/token",
            data={"username": username, "password": password},
            timeout=5
        )
        if res.status_code == 200:
            data = res.json()
            st.session_state.token = data["access_token"]
            st.session_state.role = data["role"]
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Authentication failed: Invalid username or password.")
    except Exception as e:
        st.error(f"Cannot reach authentication gateway: {e}")

# =====================================================================
# 2. LANDING / LOGIN DASHBOARD (WHEN LOGGED OUT)
# =====================================================================
if not st.session_state.token:
    st.markdown("<div class='login-hero-container'>", unsafe_allow_html=True)
    
    col_hero, col_login = st.columns([1.15, 0.85], gap="large")

    # LEFT COLUMN: PLATFORM SHOWCASE & CAPABILITIES
    with col_hero:
        st.markdown("""
            <div class="login-hero-badge">⚡ Enterprise AI Platform • v2.0 Production</div>
            <div class="login-hero-title">Autonomous AI Platform for Enterprise Operations</div>
            <div class="login-hero-subtitle">
                A unified, high-performance gateway integrating predictive machine learning,
                semantic vector retrieval (RAG), and microsecond-level telemetry logging.
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="feature-pill-card">
                <div class="feature-icon-box">📊</div>
                <div>
                    <div class="feature-title">Predictive Customer Risk Engine</div>
                    <div class="feature-desc">Random Forest classifier evaluating customer financial portfolios, assessing churn probability, and triggering automated retention protocols.</div>
                </div>
            </div>

            <div class="feature-pill-card">
                <div class="feature-icon-box">🔍</div>
                <div>
                    <div class="feature-title">Vector Knowledge Intelligence (RAG)</div>
                    <div class="feature-desc">Persistent ChromaDB vector embeddings paired with Groq LLaMA-3.3 70B for grounded enterprise document synthesis with source citations.</div>
                </div>
            </div>

            <div class="feature-pill-card">
                <div class="feature-icon-box">🛡️</div>
                <div>
                    <div class="feature-title">Zero-Trust JWT Security & Audit Hub</div>
                    <div class="feature-desc">Cryptographic OAuth2 bearer tokens, rate-limited endpoints, and ASGI middleware capturing real-time latency and request telemetry.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div class="telemetry-pill-group" style="margin-top: 1.5rem;">
                <div class="telemetry-pill"><div class="pulse-dot"></div>FastAPI v0.141 Online</div>
                <div class="telemetry-pill"><div class="pulse-dot pulse-indigo"></div>ChromaDB Vector Vault</div>
                <div class="telemetry-pill"><div class="pulse-dot"></div>Groq LLaMA-3.3 Active</div>
            </div>
        """, unsafe_allow_html=True)

    # RIGHT COLUMN: GLASSMORPHIC LOGIN CARD
    with col_login:
        st.markdown("""
            <div class="login-form-card">
                <div class="login-card-header">
                    <div class="login-avatar-ring">🔐</div>
                    <div class="login-card-title">Enterprise Gateway Sign-In</div>
                    <div class="login-card-subtitle">Authenticate with corporate credentials to access model pipelines</div>
                </div>
        """, unsafe_allow_html=True)

        user_input = st.text_input("Username", value=st.session_state.login_username_input, placeholder="Username", key="input_user")
        pass_input = st.text_input("Password", value=st.session_state.login_password_input, type="password", placeholder="Password", key="input_pass")

        if st.button("🚀 Authenticate to Platform", type="primary", use_container_width=True):
            perform_login(user_input, pass_input)

        st.markdown("<div style='margin: 1.25rem 0 0.5rem 0; font-size: 0.78rem; font-weight: 700; color: #94a3b8; text-transform: uppercase;'>Quick Demo Access:</div>", unsafe_allow_html=True)
        col_demo1, col_demo2 = st.columns(2)
        with col_demo1:
            if st.button("👑 Sign In as Admin", type="secondary", use_container_width=True):
                perform_login("admin", "admin123")
        with col_demo2:
            if st.button("👤 Sign In as User", type="secondary", use_container_width=True):
                perform_login("user", "user123")

        st.markdown("""
                <div class="demo-account-box">
                    <strong>Pre-configured Roles:</strong><br>
                    • <code>admin</code> / <code>admin123</code> — Full Model, Vector & Audit Access<br>
                    • <code>user</code> / <code>user123</code> — Standard Inference & Q&A
                </div>
                <div style="text-align: center; margin-top: 1rem; font-size: 0.74rem; color: #64748b;">
                    🔒 Protected by Enterprise RSA-256 JWT • OAuth2 Bearer Standard
                </div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# =====================================================================
# 3. AUTHENTICATED USER: SIDEBAR
# =====================================================================
with st.sidebar:
    st.markdown("""
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem;">
            <div style="background: linear-gradient(135deg, #6366f1, #06b6d4); width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 1.2rem; font-weight: bold; color: white;">⚡</div>
            <div>
                <div style="font-weight: 800; font-size: 1.05rem; letter-spacing: -0.02em; color: #f8fafc;">Enterprise AI</div>
                <div style="font-size: 0.72rem; color: #818cf8; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase;">Platform v2.0</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    role_badge_color = "#6366f1" if st.session_state.role == "admin" else "#06b6d4"
    st.markdown(f"""
        <div style="background: rgba(30, 41, 59, 0.5); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 0.85rem 1rem; margin-bottom: 1.25rem; display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 0.65rem;">
                <div style="width: 32px; height: 32px; border-radius: 50%; background: rgba(99, 102, 241, 0.2); border: 1px solid #6366f1; display: flex; align-items: center; justify-content: center; font-size: 0.9rem;">👤</div>
                <div>
                    <div style="font-weight: 700; font-size: 0.88rem; color: #f8fafc;">{st.session_state.username}</div>
                    <div style="font-size: 0.72rem; color: {role_badge_color}; font-weight: 600; text-transform: uppercase;">{st.session_state.role}</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button("Sign Out", use_container_width=True):
            st.session_state.token = None
            st.session_state.role = None
            st.session_state.username = None
            st.session_state.chat_history = []
            st.rerun()
    with col_btn2:
        if st.button("Sync Data", use_container_width=True):
            st.rerun()

    st.markdown("---")

    HEADERS = {
        "X-API-Key": API_KEY,
        "Authorization": f"Bearer {st.session_state.token}"
    }

    st.markdown("<div style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.05em; margin-bottom: 0.5rem;'>Platform Engines</div>", unsafe_allow_html=True)
    nav_options = [
        "📊 ML Customer Risk Predictor",
        "🔍 AI Knowledge Assistant (RAG)"
    ]
    if st.session_state.role == "admin":
        nav_options.append("🛡️ Audit & System Logs")

    selected_engine = st.radio("Navigation", nav_options, label_visibility="collapsed")

    st.markdown("---")
    st.markdown("<div style='font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.05em; margin-bottom: 0.6rem;'>Vector Storage (ChromaDB)</div>", unsafe_allow_html=True)
    
    try:
        stats_res = requests.get(f"{API_URL}/kb-stats", headers=HEADERS, timeout=4)
        if stats_res.status_code == 200:
            kb_data = stats_res.json()
            total_chunks = kb_data.get("total_chunks", 0)
            doc_list = kb_data.get("documents", [])
            
            st.metric("Total Indexed Chunks", total_chunks)
            if doc_list:
                st.caption(f"Active Knowledge Documents ({len(doc_list)}):")
                for d in doc_list:
                    st.markdown(f"<div style='font-size: 0.76rem; color: #94a3b8; background: rgba(15, 23, 42, 0.6); padding: 0.25rem 0.5rem; border-radius: 4px; margin-bottom: 0.25rem;'>📄 {d}</div>", unsafe_allow_html=True)
            else:
                st.caption("No external documents indexed.")
    except Exception:
        st.caption("Vector telemetry currently unavailable.")

    if st.session_state.role == "admin":
        st.markdown("---")
        with st.expander("⚠️ Database Administration"):
            st.caption("Purging removes all ChromaDB embeddings and re-initializes an empty vector collection.")
            confirm_purge = st.checkbox("Confirm database reset", key="chk_purge")
            if st.button("🗑️ Reset Vector Database", type="secondary", disabled=not confirm_purge, use_container_width=True):
                try:
                    purge_res = requests.delete(f"{API_URL}/purge-kb", headers=HEADERS, timeout=5)
                    if purge_res.status_code == 200:
                        st.success("Vector database successfully cleared.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"Purge failed: {purge_res.text}")
                except Exception as ex:
                    st.error(f"Purge error: {ex}")

# =====================================================================
# 4. EXECUTIVE TOP BAR (AUTHENTICATED)
# =====================================================================
st.markdown("""
    <div class="executive-header">
        <div class="executive-title-group">
            <h1>⚡ Enterprise AI Platform <span style="font-size: 0.95rem; background: rgba(99, 102, 241, 0.2); border: 1px solid #6366f1; border-radius: 9999px; padding: 0.2rem 0.65rem; color: #a5b4fc; font-weight: 600; -webkit-text-fill-color: initial;">v2.0 PROD</span></h1>
            <div class="executive-subtitle">Unified Machine Learning & Retrieval-Augmented Generation Gateway</div>
        </div>
        <div class="telemetry-pill-group">
            <div class="telemetry-pill">
                <div class="pulse-dot"></div>
                FastAPI: 8000 Online
            </div>
            <div class="telemetry-pill">
                <div class="pulse-dot pulse-indigo"></div>
                ChromaDB Vector Store
            </div>
            <div class="telemetry-pill">
                <div class="pulse-dot"></div>
                Groq LLaMA-3.3 70B
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# =====================================================================
# 5. ENGINE 1: ML CUSTOMER RISK PREDICTOR
# =====================================================================
if selected_engine == "📊 ML Customer Risk Predictor":
    st.markdown("""
        <div class="glass-card">
            <div class="card-title">📊 Predictive Customer Churn Analytics</div>
            <div class="card-subtitle">Real-time inference using a production-grade Random Forest classification model trained on historical customer accounts.</div>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='font-size: 0.8rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin-bottom: 0.5rem;'>Quick Simulation Profiles:</div>", unsafe_allow_html=True)
    c_p1, c_p2, c_p3 = st.columns(3)
    
    preset_data = None
    with c_p1:
        if st.button("💎 Loyal Low-Risk Customer", use_container_width=True):
            preset_data = {"credit": 780, "age": 42, "tenure": 8, "balance": 45000.0, "products": 2}
    with c_p2:
        if st.button("⚠️ At-Risk High Net Worth", use_container_width=True):
            preset_data = {"credit": 510, "age": 52, "tenure": 2, "balance": 95000.0, "products": 1}
    with c_p3:
        if st.button("⏳ Inactive New Account", use_container_width=True):
            preset_data = {"credit": 620, "age": 28, "tenure": 1, "balance": 8000.0, "products": 3}

    default_credit = preset_data["credit"] if preset_data else 650
    default_age = preset_data["age"] if preset_data else 42
    default_tenure = preset_data["tenure"] if preset_data else 3
    default_balance = preset_data["balance"] if preset_data else 50000.0
    default_products = preset_data["products"] if preset_data else 1

    col_in1, col_in2 = st.columns(2)
    with col_in1:
        with st.container(border=True):
            st.markdown("<div class='card-title'>💳 Financial & Tenure Attributes</div>", unsafe_allow_html=True)
            credit_score = st.slider("Credit Rating Score", min_value=300, max_value=850, value=default_credit, step=5, help="Standard credit rating score scale (300-850)")
            age = st.slider("Customer Age", min_value=18, max_value=100, value=default_age, step=1)
            tenure = st.slider("Relationship Tenure (Years)", min_value=0, max_value=10, value=default_tenure, step=1)

    with col_in2:
        with st.container(border=True):
            st.markdown("<div class='card-title'>🏦 Portfolio & Product Metrics</div>", unsafe_allow_html=True)
            balance = st.number_input("Account Balance (USD)", min_value=0.0, max_value=500000.0, value=default_balance, step=2500.0)
            num_products = st.selectbox("Active Product Portfolio Size", options=[1, 2, 3, 4], index=default_products-1)
            st.caption("Active subscriptions, cards, lines of credit, and investment accounts.")

    submit_btn = st.button("🚀 Run Live Risk Assessment", type="primary", use_container_width=True)

    if submit_btn or preset_data:
        payload = {
            "credit_score": credit_score,
            "age": age,
            "tenure": tenure,
            "balance": balance,
            "num_products": num_products,
        }
        try:
            with st.spinner("Executing model inference..."):
                response = requests.post(f"{API_URL}/predict-churn", json=payload, headers=HEADERS, timeout=5)
                
            if response.status_code == 200:
                data = response.json()
                risk = data.get("prediction", "Unknown")
                prob = data.get("churn_probability", 0.0)
                
                is_high = (risk == "High Risk")
                risk_color_class = "high-risk" if is_high else "low-risk"
                badge_text = "CRITICAL CHURN RISK" if is_high else "HEALTHY ACCOUNT STATUS"
                
                st.markdown(f"""
                    <div class="risk-gauge-container">
                        <div class="gauge-badge {risk_color_class}">{badge_text}</div>
                        <div class="gauge-prob-display {risk_color_class}">{prob}%</div>
                        <div style="font-size: 0.9rem; color: #94a3b8; margin-bottom: 1.25rem;">Estimated Probability of Customer Discontinuation</div>
                        <div class="progress-track">
                            <div class="progress-fill {risk_color_class}" style="width: {prob}%;"></div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown("<div class='glass-card' style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
                st.markdown("<div class='card-title'>📋 Automated Strategic Protocol</div>", unsafe_allow_html=True)
                
                if is_high:
                    st.markdown("""
                        <div class="policy-recommendation-box" style="border-left-color: #ef4444; background: rgba(239, 68, 68, 0.08);">
                            <strong>⚠️ Policy Intervention Mandate:</strong><br>
                            According to internal corporate policy for high-risk accounts (Credit score &lt; 600 or High Balance Exposure):<br>
                            1. <strong>Immediate Retention Offer:</strong> Trigger an authorized <strong>15% promotional discount</strong>.<br>
                            2. <strong>Account Management:</strong> Automatically assign a <strong>Dedicated Account Executive</strong> to schedule a customer success review within 24 hours.<br>
                            3. <strong>Service Level:</strong> Elevate priority ticket queue status.
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown("""
                        <div class="policy-recommendation-box" style="border-left-color: #10b981; background: rgba(16, 185, 129, 0.08);">
                            <strong>✅ Standard Growth Protocol:</strong><br>
                            Account exhibits high stability and retention confidence. Eligible for cross-sell campaigns, premium tier upgrades, and automated quarterly check-in sequences.
                        </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)

            else:
                st.error(f"Inference gateway returned HTTP {response.status_code}: {response.text}")
        except Exception as e:
            st.error(f"Prediction engine communication failed: {e}")

# =====================================================================
# 6. ENGINE 2: AI KNOWLEDGE ASSISTANT (RAG)
# =====================================================================
elif selected_engine == "🔍 AI Knowledge Assistant (RAG)":
    st.markdown("""
        <div class="glass-card">
            <div class="card-title">🔍 Enterprise Knowledge Intelligence (RAG)</div>
            <div class="card-subtitle">Multi-turn generative assistant powered by Groq LLaMA-3.3 and semantic vector embeddings stored in ChromaDB.</div>
        </div>
    """, unsafe_allow_html=True)

    with st.expander("📂 Ingest Internal Documents & Policy Knowledge", expanded=False):
        st.markdown("Upload compliance guidelines, standard operating procedures, or customer support SLAs (`.txt` or `.pdf`).")
        uploaded_files = st.file_uploader(
            "Select Documents to Chunk & Embed",
            type=["txt", "pdf"],
            accept_multiple_files=True
        )
        if uploaded_files and st.button("🚀 Process & Ingest Files", type="primary"):
            progress_bar = st.progress(0)
            total = len(uploaded_files)
            for idx, uf in enumerate(uploaded_files):
                try:
                    files = {"file": (uf.name, uf.getvalue())}
                    resp = requests.post(f"{API_URL}/upload-doc", headers=HEADERS, files=files, timeout=30)
                    if resp.status_code == 200:
                        res_data = resp.json()
                        st.success(f"Successfully vectorized `{res_data.get('filename')}` ({res_data.get('chunks_added', 0)} chunks generated).")
                    else:
                        st.error(f"Failed to ingest `{uf.name}`: {resp.text}")
                except Exception as ex:
                    st.error(f"Error indexing `{uf.name}`: {ex}")
                progress_bar.progress((idx + 1) / total)
            st.rerun()

    st.markdown("<div style='font-size: 0.8rem; font-weight: 700; color: #94a3b8; text-transform: uppercase; margin: 1rem 0 0.5rem 0;'>Recommended Policy Inquiries:</div>", unsafe_allow_html=True)
    chip_col1, chip_col2, chip_col3, chip_col4 = st.columns(4)
    suggested_q = None
    with chip_col1:
        if st.button("What is churn retention policy?", use_container_width=True):
            suggested_q = "What is the retention strategy and discount for churn-risk customers?"
    with chip_col2:
        if st.button("What is premium SLA?", use_container_width=True):
            suggested_q = "What is the guaranteed response time for premium tier support?"
    with chip_col3:
        if st.button("How are high-risk users defined?", use_container_width=True):
            suggested_q = "How does the organization define high-risk customers in terms of credit score and balance?"
    with chip_col4:
        if st.button("Inactivity rules (>90 days)?", use_container_width=True):
            suggested_q = "What automated actions occur when an account is inactive for more than 90 days?"

    col_chat_head1, col_chat_head2 = st.columns([5, 1])
    with col_chat_head2:
        if st.button("🧹 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander(f"📚 Vector Sources ({len(msg['sources'])} retrieved)"):
                    for s in msg["sources"]:
                        st.markdown(f"""
                            <div class="source-citation-card">
                                <div class="citation-header">
                                    <span>📄 {s.get('document', 'Document')}</span>
                                    <span>Chunk #{s.get('chunk_index', 0)}</span>
                                </div>
                                <div class="citation-snippet">"{s.get('snippet', '')}"</div>
                            </div>
                        """, unsafe_allow_html=True)

    user_prompt = st.chat_input("Ask any question regarding company policy, SLA, or churn criteria...")
    prompt_to_send = user_prompt or suggested_q

    if prompt_to_send:
        st.session_state.chat_history.append({"role": "user", "content": prompt_to_send})
        with st.chat_message("user"):
            st.markdown(prompt_to_send)

        with st.chat_message("assistant"):
            with st.spinner("Synthesizing context from vector space and Groq LLM..."):
                try:
                    payload = {
                        "query": prompt_to_send,
                        "history": [
                            {"role": m["role"], "content": m["content"]}
                            for m in st.session_state.chat_history[:-1]
                        ]
                    }
                    res = requests.post(f"{API_URL}/query", json=payload, headers=HEADERS, timeout=20)
                    if res.status_code == 200:
                        ans_data = res.json()
                        answer_text = ans_data.get("answer", "No answer retrieved.")
                        sources = ans_data.get("sources", [])
                        
                        st.markdown(answer_text)
                        
                        if sources:
                            with st.expander(f"📚 Verified Vector Citations ({len(sources)})"):
                                for s in sources:
                                    st.markdown(f"""
                                        <div class="source-citation-card">
                                            <div class="citation-header">
                                                <span>📄 {s.get('document', 'Document')}</span>
                                                <span>Chunk #{s.get('chunk_index', 0)}</span>
                                            </div>
                                            <div class="citation-snippet">"{s.get('snippet', '')}"</div>
                                        </div>
                                    """, unsafe_allow_html=True)

                        st.session_state.chat_history.append({
                            "role": "assistant",
                            "content": answer_text,
                            "sources": sources
                        })
                    else:
                        st.error(f"Assistant Gateway error {res.status_code}: {res.text}")
                except Exception as ex:
                    st.error(f"Failed to query knowledge base: {ex}")

# =====================================================================
# 7. ENGINE 3: AUDIT & SYSTEM LOGS (ADMIN ONLY)
# =====================================================================
elif selected_engine == "🛡️ Audit & System Logs":
    st.markdown("""
        <div class="glass-card">
            <div class="card-title">🛡️ System Telemetry & Request Audit Hub</div>
            <div class="card-subtitle">Real-time latency profiling, API route frequency, and HTTP status codes captured via FastAPI ASGI middleware.</div>
        </div>
    """, unsafe_allow_html=True)

    col_sync, col_export = st.columns([1, 1])
    with col_sync:
        if st.button("🔄 Refresh Audit Stream", use_container_width=True):
            st.rerun()

    try:
        log_res = requests.get(f"{API_URL}/audit-logs", headers=HEADERS, timeout=5)
        if log_res.status_code == 200:
            data = log_res.json()
            total_records = data.get("total_records", 0)
            logs = data.get("logs", [])

            if logs:
                df = pd.DataFrame(logs)
                
                avg_latency = round(df["latency_ms"].mean(), 2) if "latency_ms" in df.columns else 0.0
                success_count = (df["status_code"] < 400).sum() if "status_code" in df.columns else 0
                success_rate = round((success_count / len(df)) * 100, 1) if len(df) > 0 else 100.0

                st.markdown(f"""
                    <div class="kpi-grid">
                        <div class="kpi-card">
                            <div class="kpi-label">Total Logged Calls</div>
                            <div class="kpi-value">{total_records}</div>
                            <div class="kpi-meta">● Active Ledger</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-label">Average Latency</div>
                            <div class="kpi-value">{avg_latency} ms</div>
                            <div class="kpi-meta">● ASGI Dispatch</div>
                        </div>
                        <div class="kpi-card">
                            <div class="kpi-label">Success Rate</div>
                            <div class="kpi-value">{success_rate}%</div>
                            <div class="kpi-meta">● HTTP 2xx/3xx</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                col_f1, col_f2 = st.columns([2, 1])
                with col_f1:
                    search_path = st.text_input("Filter by Path substring", placeholder="e.g. /predict-churn or /query")
                with col_f2:
                    methods = ["ALL"] + sorted(list(df["method"].unique())) if "method" in df.columns else ["ALL"]
                    sel_method = st.selectbox("Filter Method", methods)

                filtered_df = df
                if search_path and "path" in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df["path"].str.contains(search_path, case=False, na=False)]
                if sel_method != "ALL" and "method" in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df["method"] == sel_method]

                st.markdown("#### Detailed Transaction Ledger")
                st.dataframe(filtered_df, use_container_width=True, height=380)

                with col_export:
                    json_data = filtered_df.to_json(orient="records", indent=2)
                    st.download_button(
                        label="📥 Export Ledger JSON",
                        data=json_data,
                        file_name=f"audit_logs_{int(time.time())}.json",
                        mime="application/json",
                        use_container_width=True
                    )
            else:
                st.info("No transaction logs recorded yet. Perform model predictions or queries to generate telemetry.")
        else:
            st.error(f"Unauthorized or failed to retrieve telemetry: HTTP {log_res.status_code}")
    except Exception as ex:
        st.error(f"Failed to connect to backend telemetry service: {ex}")