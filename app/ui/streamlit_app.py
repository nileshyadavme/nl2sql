"""
Talk to Your Database — NL2SQL Agent
Streamlit Frontend — Modern Dark UI
Run: uv run streamlit run app/ui/streamlit_app.py
"""

import os
import sys
import html
import streamlit as st
import pandas as pd
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
load_dotenv()

from app.agents.nl2sql_agent import NL2SQLAgent
from app.database.connection import get_db_connection, reset_db_connection
from app.utils.query_history import save_query, load_history, clear_history
from app.utils.chart_renderer import render_chart

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QueryMind · NL2SQL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Design System ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

  /* ── Base reset ── */
  *, *::before, *::after { box-sizing: border-box; }

  html, body, .stApp {
    background-color: #0D1117 !important;
    color: #E6EDF3 !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
  }

  /* ── Hide Streamlit chrome ── */
  #MainMenu, footer, header, .stDeployButton { visibility: hidden !important; }
  .block-container { padding: 1.5rem 2rem 3rem 2rem !important; max-width: 100% !important; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: #161B22 !important;
    border-right: 1px solid #21262D !important;
    padding: 0 !important;
  }
  [data-testid="stSidebar"] > div:first-child { padding: 1.5rem 1.25rem; }
  [data-testid="stSidebarNavItems"] { display: none; }

  /* ── Typography ── */
  h1, h2, h3, h4 {
    font-family: 'Inter', sans-serif !important;
    color: #E6EDF3 !important;
    letter-spacing: -0.02em;
  }
  p, span, label, .stMarkdown { color: #8B949E !important; }

  /* ── Inputs ── */
  .stTextInput input, .stTextArea textarea, .stNumberInput input {
    background: #0D1117 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px !important;
    color: #E6EDF3 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .stTextInput input:focus, .stTextArea textarea:focus {
    border-color: #388BFD !important;
    box-shadow: 0 0 0 3px rgba(56,139,253,0.12) !important;
    outline: none !important;
  }
  .stTextInput label, .stTextArea label, .stNumberInput label {
    color: #8B949E !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    margin-bottom: 4px !important;
  }

  /* ── Buttons ── */
  .stButton > button {
    background: #21262D !important;
    color: #E6EDF3 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 0.45rem 1rem !important;
    transition: all 0.15s ease !important;
    letter-spacing: 0.01em;
  }
  .stButton > button:hover {
    background: #2D333B !important;
    border-color: #8B949E !important;
    color: #E6EDF3 !important;
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
  }
  .stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2EA043, #238636) !important;
    border-color: #238636 !important;
    color: #fff !important;
  }
  .stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #3FB950, #2EA043) !important;
    border-color: #3FB950 !important;
    box-shadow: 0 4px 16px rgba(46,160,67,0.35) !important;
  }

  /* ── Toggle ── */
  [data-testid="stToggle"] { margin-top: 4px; }
  [data-testid="stToggle"] label { color: #8B949E !important; font-size: 13px !important; }

  /* ── Selectbox ── */
  .stSelectbox [data-baseweb="select"] > div {
    background: #0D1117 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px !important;
    color: #E6EDF3 !important;
  }

  /* ── Metrics ── */
  [data-testid="metric-container"] {
    background: #161B22 !important;
    border: 1px solid #21262D !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    transition: border-color 0.2s, transform 0.2s;
  }
  [data-testid="metric-container"]:hover {
    border-color: #388BFD !important;
    transform: translateY(-2px);
  }
  [data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #8B949E !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  [data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #E6EDF3 !important;
    font-size: 22px !important;
    font-weight: 700 !important;
  }

  /* ── Tabs ── */
  .stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #21262D !important;
    gap: 0 !important;
  }
  .stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: #8B949E !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 0.6rem 1.25rem !important;
    border-bottom: 2px solid transparent !important;
    transition: color 0.15s, border-color 0.15s;
  }
  .stTabs [aria-selected="true"] {
    color: #E6EDF3 !important;
    border-bottom-color: #388BFD !important;
    background: transparent !important;
  }
  .stTabs [data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 1rem 0 !important;
  }

  /* ── Dataframe ── */
  [data-testid="stDataFrame"] {
    border: 1px solid #21262D !important;
    border-radius: 10px !important;
  }
  .dvn-scroller { background: #0D1117 !important; }
  [data-testid="glideDataEditor"] { background: #0D1117 !important; }

  /* ── Expander ── */
  [data-testid="stExpander"] {
    background: #161B22 !important;
    border: 1px solid #21262D !important;
    border-radius: 10px !important;
  }
  [data-testid="stExpander"] summary { color: #8B949E !important; font-size: 13px !important; }

  /* ── Spinner ── */
  .stSpinner > div { border-top-color: #388BFD !important; }

  /* ── Alerts ── */
  .stAlert { border-radius: 10px !important; }
  [data-testid="stNotification"] { background: #1C2128 !important; border-color: #30363D !important; }

  /* ── Scrollbar ── */
  ::-webkit-scrollbar { width: 6px; height: 6px; }
  ::-webkit-scrollbar-track { background: #0D1117; }
  ::-webkit-scrollbar-thumb { background: #30363D; border-radius: 3px; }
  ::-webkit-scrollbar-thumb:hover { background: #8B949E; }

  /* ── Custom components ── */
  .qm-brand {
    display: flex; align-items: center; gap: 10px;
    padding: 0 0 1.25rem 0;
    border-bottom: 1px solid #21262D;
    margin-bottom: 1.25rem;
  }
  .qm-brand-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #388BFD, #2EA043);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
  }
  .qm-brand-title {
    font-size: 16px; font-weight: 700;
    color: #E6EDF3 !important;
    letter-spacing: -0.02em;
  }
  .qm-brand-sub {
    font-size: 11px; color: #8B949E !important;
    font-weight: 400;
  }

  .qm-section-label {
    font-size: 10px; font-weight: 600;
    color: #8B949E !important;
    text-transform: uppercase; letter-spacing: 0.1em;
    padding: 0.6rem 0 0.4rem 0;
    display: block;
  }

  .qm-status-badge {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px; font-weight: 600;
  }
  .qm-status-connected {
    background: rgba(46,160,67,0.15);
    color: #3FB950;
    border: 1px solid rgba(46,160,67,0.3);
  }
  .qm-status-disconnected {
    background: rgba(248,81,73,0.12);
    color: #F85149;
    border: 1px solid rgba(248,81,73,0.3);
  }

  .qm-answer-card {
    background: #161B22;
    border: 1px solid #21262D;
    border-left: 3px solid #388BFD;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0 1rem 0;
    font-size: 14px;
    line-height: 1.7;
    color: #E6EDF3 !important;
  }
  .qm-error-card {
    background: rgba(248,81,73,0.07);
    border: 1px solid rgba(248,81,73,0.25);
    border-left: 3px solid #F85149;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    margin: 0.5rem 0 1rem 0;
    font-size: 14px;
    color: #F85149 !important;
  }
  .qm-sql-block {
    background: #0D1117;
    border: 1px solid #21262D;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    font-family: 'JetBrains Mono', 'Courier New', monospace;
    font-size: 13px;
    line-height: 1.65;
    color: #79C0FF !important;
    white-space: pre-wrap;
    word-break: break-word;
    position: relative;
  }
  .qm-explain-pill {
    background: rgba(56,139,253,0.08);
    border: 1px solid rgba(56,139,253,0.2);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    font-size: 13px;
    color: #79C0FF !important;
    margin-top: 0.75rem;
  }
  .qm-question-header {
    font-size: 15px; font-weight: 600;
    color: #E6EDF3 !important;
    display: flex; align-items: center; gap: 8px;
    margin-bottom: 0.25rem;
  }
  .qm-timestamp {
    font-size: 11px;
    color: #8B949E !important;
    margin-bottom: 0.5rem;
  }
  .qm-divider {
    height: 1px;
    background: #21262D;
    margin: 1.5rem 0;
    border: none;
  }
  .qm-empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: #8B949E !important;
  }
  .qm-empty-icon {
    font-size: 48px;
    margin-bottom: 1rem;
    display: block;
    filter: grayscale(0.3);
  }
  .qm-empty-title {
    font-size: 18px; font-weight: 600;
    color: #8B949E !important;
    margin-bottom: 0.5rem;
  }
  .qm-empty-sub {
    font-size: 13px;
    color: #6E7681 !important;
    max-width: 400px;
    margin: 0 auto 2rem;
    line-height: 1.6;
  }
  .qm-feature-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
    gap: 1rem;
    margin: 2rem 0;
  }
  .qm-feature-card {
    background: #161B22;
    border: 1px solid #21262D;
    border-radius: 12px;
    padding: 1.25rem;
    text-align: center;
    transition: border-color 0.2s, transform 0.2s;
  }
  .qm-feature-card:hover {
    border-color: #388BFD;
    transform: translateY(-2px);
  }
  .qm-feature-icon { font-size: 24px; margin-bottom: 0.5rem; display: block; }
  .qm-feature-title {
    font-size: 13px; font-weight: 600;
    color: #E6EDF3 !important;
    margin-bottom: 0.25rem;
  }
  .qm-feature-desc { font-size: 12px; color: #6E7681 !important; line-height: 1.5; }

  .qm-schema-box {
    background: #0D1117;
    border: 1px solid #21262D;
    border-radius: 10px;
    padding: 1rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    line-height: 1.7;
    color: #8B949E !important;
    max-height: 300px;
    overflow-y: auto;
    white-space: pre;
  }
  .qm-history-item {
    background: #0D1117;
    border: 1px solid #21262D;
    border-radius: 8px;
    padding: 0.6rem 0.875rem;
    margin: 0.35rem 0;
    font-size: 12px;
    color: #8B949E !important;
    cursor: pointer;
    transition: border-color 0.15s, background 0.15s;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  .qm-history-item:hover {
    background: #161B22;
    border-color: #388BFD;
    color: #E6EDF3 !important;
  }
  .qm-tag-success { color: #3FB950; }
  .qm-tag-fail { color: #F85149; }

  .qm-chip {
    display: inline-block;
    background: #21262D;
    border: 1px solid #30363D;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 12px;
    color: #8B949E !important;
    margin: 3px;
    cursor: pointer;
    transition: all 0.15s;
  }
  .qm-chip:hover {
    background: #2D333B;
    border-color: #388BFD;
    color: #E6EDF3 !important;
  }
  .qm-main-title {
    font-size: 28px; font-weight: 700;
    color: #E6EDF3 !important;
    letter-spacing: -0.03em;
    margin-bottom: 0.25rem;
  }
  .qm-main-sub {
    font-size: 14px; color: #8B949E !important;
    margin-bottom: 0;
  }
  .qm-gradient-text {
    background: linear-gradient(90deg, #388BFD, #3FB950);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
</style>
""", unsafe_allow_html=True)


# ─── Session state ──────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "agent": None, "db": None, "connected": False,
        "messages": [], "last_result": None,
        "schema_text": "", "table_stats": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    # Brand
    connected = st.session_state.connected
    status_cls = "qm-status-connected" if connected else "qm-status-disconnected"
    status_dot = "●" if connected else "●"
    status_txt = "Connected" if connected else "Disconnected"

    st.markdown(f"""
    <div class="qm-brand">
      <div class="qm-brand-icon">⚡</div>
      <div>
        <div class="qm-brand-title">QueryMind</div>
        <div class="qm-brand-sub">NL → SQL · Gemini Powered</div>
      </div>
    </div>
    <div class="qm-status-badge {status_cls}">{status_dot} {status_txt}</div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Connection panel
    st.markdown('<span class="qm-section-label">🗄 Database</span>', unsafe_allow_html=True)
    
    use_demo = st.toggle("Use bundled Demo DB", value=False)
    
    db_url = st.text_input(
        "Connection URL",
        value="sqlite:///sample.db" if use_demo else os.getenv("DATABASE_URL", ""),
        type="password" if not use_demo else "default",
        placeholder="postgresql://user:pass@host:5432/db",
        label_visibility="collapsed",
        disabled=use_demo
    )



    c1, c2 = st.columns(2)
    with c1:
        max_rows = st.number_input("Max rows", value=500, min_value=10, max_value=5000, step=50)
    with c2:
        read_only = st.toggle("Read only", value=True)

    btn_label = "🔄 Reconnect" if connected else "⚡ Connect"
    if st.button(btn_label, use_container_width=True, type="primary"):
        gemini_env_key = os.getenv("GEMINI_API_KEY")
        if not db_url:
            st.error("Database URL required")
        elif not gemini_env_key:
            st.error("GEMINI_API_KEY not found in environment (.env)")
        else:
            with st.spinner("Connecting..."):
                try:
                    reset_db_connection()
                    db = get_db_connection(db_url)
                    if not db.test_connection():
                        st.error("❌ Cannot connect. Check URL.")
                    else:
                        agent = NL2SQLAgent(db, gemini_api_key=gemini_env_key)
                        st.session_state.agent = agent
                        st.session_state.db = db
                        st.session_state.connected = True
                        st.session_state.schema_text = agent.get_schema_summary()
                        st.session_state.table_stats = agent.get_table_stats()
                        st.success("✅ Connected")
                        st.rerun()
                except Exception as e:
                    st.error(f"Failed: {e}")

    # Schema explorer
    if st.session_state.connected:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="qm-section-label">📋 Schema</span>', unsafe_allow_html=True)
        stats = st.session_state.table_stats
        for table, count in stats.items():
            count_str = f"{count:,}" if count >= 0 else "?"
            st.markdown(
                f'<div class="qm-history-item" title="{table}">📁 <b style="color:#E6EDF3">{table}</b>&ensp;<span style="float:right;color:#388BFD">{count_str}</span></div>',
                unsafe_allow_html=True,
            )

        with st.expander("View full schema"):
            st.markdown(
                f'<div class="qm-schema-box">{html.escape(st.session_state.schema_text)}</div>',
                unsafe_allow_html=True,
            )

        # Example queries
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="qm-section-label">💡 Try these</span>', unsafe_allow_html=True)
        examples = [
            "Top 10 customers by revenue",
            "Monthly sales trend for 2024",
            "Products with highest return rate",
            "Customers inactive for 90+ days",
            "Average order value by category",
        ]
        for ex in examples:
            if st.button(f"↗ {ex}", key=f"ex_{ex}", use_container_width=True):
                st.session_state["inject_question"] = ex
                st.rerun()

    # History
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="qm-section-label">🕓 History</span>', unsafe_allow_html=True)
    history = load_history()
    if history:
        if st.button("🗑 Clear", use_container_width=True):
            clear_history()
            st.rerun()
        for entry in history[:6]:
            icon = "✅" if entry["success"] else "❌"
            ts = entry["timestamp"][:16].replace("T", " ")
            label = f'{icon} {entry["question"][:35]}...' if len(entry["question"]) > 35 else f'{icon} {entry["question"]}'
            if st.button(label, key=f"hist_{entry['id']}", use_container_width=True):
                st.session_state["inject_question"] = entry["question"]
                st.rerun()
    else:
        st.caption("No history yet.")


# ─── Main area ──────────────────────────────────────────────────────────────────

if not st.session_state.connected:
    # ── Landing / not connected ──────────────────────────────────────
    st.markdown("""
    <div style="padding: 2rem 0 1rem 0;">
      <div class="qm-main-title">
        Ask your database anything.<br>
        <span class="qm-gradient-text">In plain English.</span>
      </div>
      <div class="qm-main-sub">Connect your PostgreSQL database and start querying with natural language — powered by Gemini.</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="qm-divider">', unsafe_allow_html=True)

    st.markdown("""
    <div class="qm-feature-grid">
      <div class="qm-feature-card">
        <span class="qm-feature-icon">🧠</span>
        <div class="qm-feature-title">Schema-Aware AI</div>
        <div class="qm-feature-desc">Automatically reads your tables, columns, and relationships</div>
      </div>
      <div class="qm-feature-card">
        <span class="qm-feature-icon">⚡</span>
        <div class="qm-feature-title">Instant SQL</div>
        <div class="qm-feature-desc">Gemini generates, runs, and explains queries in seconds</div>
      </div>
      <div class="qm-feature-card">
        <span class="qm-feature-icon">📊</span>
        <div class="qm-feature-title">Auto Charts</div>
        <div class="qm-feature-desc">Results automatically visualised as bars, lines, or scatter plots</div>
      </div>
      <div class="qm-feature-card">
        <span class="qm-feature-icon">🔒</span>
        <div class="qm-feature-title">Read-Only Safe</div>
        <div class="qm-feature-desc">Read-only mode blocks all writes — your data stays safe</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<span class="qm-section-label">🐳 Quick Start with sample data</span>', unsafe_allow_html=True)
    with st.expander("Spin up a demo PostgreSQL"):
        st.code("""docker run --name nl2sql-db \\
  -e POSTGRES_USER=admin \\
  -e POSTGRES_PASSWORD=password \\
  -e POSTGRES_DB=ecommerce \\
  -p 5432:5432 -d postgres:15

psql postgresql://admin:password@localhost:5432/ecommerce \\
  -f sample_data/seed.sql""", language="bash")
        st.caption("Then use: `postgresql://admin:password@localhost:5432/ecommerce`")

else:
    # ── Connected — query interface ───────────────────────────────────

    # Header
    st.markdown("""
    <div style="margin-bottom: 1.5rem;">
      <div class="qm-main-title" style="font-size:22px;">Query Console</div>
      <div class="qm-main-sub">Write a question, get SQL · results · insights</div>
    </div>
    """, unsafe_allow_html=True)

    # Metrics row
    stats = st.session_state.table_stats
    if stats:
        metric_cols = st.columns(min(len(stats), 5))
        for i, (table, count) in enumerate(list(stats.items())[:5]):
            with metric_cols[i % len(metric_cols)]:
                st.metric(table, f"{count:,}" if count >= 0 else "—")

    st.markdown('<hr class="qm-divider">', unsafe_allow_html=True)

    # Question input
    injected = st.session_state.get("inject_question", None)

    with st.container():
        question = st.text_area(
            "Your question",
            value=injected or "",
            height=90,
            placeholder='e.g.  "Show me the top 10 customers by total order value this year"',
            key="question_input",
            label_visibility="collapsed",
        )
        r1, r2, r3 = st.columns([2, 1, 8])
        with r1:
            run_clicked = st.button("⚡ Run Query", type="primary", use_container_width=True)
        with r2:
            if st.button("✕ Clear", use_container_width=True):
                st.session_state.messages = []
                st.rerun()

    # Run agent
    if run_clicked and question.strip():
        st.session_state.pop("inject_question", None)
        with st.spinner("Thinking... reading schema → writing SQL → executing"):
            result = st.session_state.agent.run(
                question=question.strip(),
                max_rows=max_rows,
            )
            st.session_state.last_result = result
            st.session_state.messages.append(result)
            save_query(result.question, result.sql_query, result.answer, result.success)

    # Results
    if st.session_state.messages:
        for result in reversed(st.session_state.messages):
            now = datetime.now().strftime("%H:%M")
            st.markdown(
                f'<div class="qm-question-header">💬 {html.escape(result.question)}</div>'
                f'<div class="qm-timestamp">{now}</div>',
                unsafe_allow_html=True,
            )

            if not result.success:
                st.markdown(
                    f'<div class="qm-error-card">⚠️ {html.escape(result.answer)}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f'<div class="qm-answer-card">💡 {html.escape(result.answer)}</div>',
                    unsafe_allow_html=True,
                )

                tab_sql, tab_data, tab_chart = st.tabs(["⌨ SQL", "⊞ Data", "∿ Chart"])

                with tab_sql:
                    st.markdown(
                        f'<div class="qm-sql-block">{html.escape(result.sql_query)}</div>',
                        unsafe_allow_html=True,
                    )
                    if result.explanation:
                        st.markdown(
                            f'<div class="qm-explain-pill">💬 {html.escape(result.explanation)}</div>',
                            unsafe_allow_html=True,
                        )
                    if result.sql_query and result.sql_query != "Could not extract SQL":
                        st.download_button(
                            "⬇ Download SQL",
                            data=result.sql_query,
                            file_name="query.sql",
                            mime="text/plain",
                            key=f"dl_sql_{hash(result.question)}",
                        )

                with tab_data:
                    if result.columns and result.rows:
                        df = pd.DataFrame(result.rows, columns=result.columns)
                        st.dataframe(df, use_container_width=True, height=320)
                        r_count, r_dl = st.columns([8, 2])
                        with r_count:
                            st.caption(f"{len(result.rows):,} rows returned")
                        with r_dl:
                            st.download_button(
                                "⬇ CSV",
                                data=df.to_csv(index=False),
                                file_name="results.csv",
                                mime="text/csv",
                                key=f"dl_csv_{hash(result.question)}",
                            )
                    else:
                        st.caption("No tabular data returned.")

                with tab_chart:
                    if result.columns and result.rows:
                        fig = render_chart(
                            result.columns, result.rows,
                            title=result.question[:60],
                        )
                        if fig:
                            st.plotly_chart(fig, use_container_width=True)
                        else:
                            st.caption("No suitable chart for this result shape.")
                    else:
                        st.caption("No data to visualise.")

            st.markdown('<hr class="qm-divider">', unsafe_allow_html=True)

    else:
        # Empty state
        st.markdown("""
        <div class="qm-empty-state">
          <span class="qm-empty-icon">📡</span>
          <div class="qm-empty-title">Ready to query</div>
          <div class="qm-empty-sub">Type a question above or pick one from the sidebar to get started. Results, SQL, and charts appear here.</div>
        </div>
        """, unsafe_allow_html=True)
