"""
Talk to Your Database — NL2SQL Agent
Streamlit Frontend
Run: streamlit run app/ui/streamlit_app.py
"""

import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
load_dotenv()

from app.agents.nl2sql_agent import NL2SQLAgent
from app.database.connection import get_db_connection
from app.utils.query_history import save_query, load_history, clear_history
from app.utils.chart_renderer import render_chart

# ─────────────────────────────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Talk to Your Database",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────
# CSS — warm theme matching resume palette
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #FDF6F0; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FEF0E6;
        border-right: 1px solid #E8C9B5;
    }

    /* Primary buttons */
    .stButton > button {
        background-color: #B85C38;
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 500;
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background-color: #9A4A2C;
        color: white;
    }

    /* Text input */
    .stTextArea textarea {
        border: 1.5px solid #E8C9B5;
        border-radius: 8px;
        background: white;
    }
    .stTextArea textarea:focus {
        border-color: #B85C38;
        box-shadow: 0 0 0 2px rgba(184,92,56,0.15);
    }

    /* Metric cards */
    [data-testid="metric-container"] {
        background: white;
        border: 1px solid #E8C9B5;
        border-radius: 10px;
        padding: 12px;
    }

    /* SQL code block */
    .sql-block {
        background: #2C1A0E;
        color: #F0D9C8;
        padding: 16px;
        border-radius: 10px;
        font-family: 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.6;
        white-space: pre-wrap;
        border-left: 4px solid #B85C38;
        margin: 8px 0;
    }

    /* Answer box */
    .answer-box {
        background: white;
        border: 1px solid #E8C9B5;
        border-left: 4px solid #B85C38;
        border-radius: 10px;
        padding: 16px 20px;
        margin: 8px 0;
        font-size: 15px;
        color: #2C1A0E;
        line-height: 1.6;
    }

    /* Explanation box */
    .explain-box {
        background: #FDEBD0;
        border-radius: 8px;
        padding: 12px 16px;
        font-size: 13px;
        color: #7A5C4F;
        margin: 6px 0;
    }

    /* History item */
    .history-item {
        background: white;
        border: 1px solid #E8C9B5;
        border-radius: 8px;
        padding: 10px 14px;
        margin: 6px 0;
        cursor: pointer;
        font-size: 13px;
    }

    /* Error box */
    .error-box {
        background: #FFF0F0;
        border: 1px solid #FFCDD2;
        border-left: 4px solid #E53935;
        border-radius: 10px;
        padding: 14px 18px;
        color: #B71C1C;
    }

    /* Schema table */
    .schema-table {
        font-size: 12px;
        font-family: monospace;
        background: #2C1A0E;
        color: #F0D9C8;
        padding: 12px;
        border-radius: 8px;
        white-space: pre;
        overflow-x: auto;
    }

    /* Section headers */
    h3 { color: #5C3D2E !important; }

    /* Hide Streamlit branding */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "agent": None,
        "db": None,
        "connected": False,
        "messages": [],
        "last_result": None,
        "schema_text": "",
        "table_stats": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# ─────────────────────────────────────────────────────────────────────
# Sidebar — connection + schema explorer
# ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🗄️ Talk to Your DB")
    st.caption("Natural language → SQL, instantly")
    st.divider()

    # ── Connection settings ──────────────────────────────────────────
    st.markdown("### ⚙️ Connection")

    db_url = st.text_input(
        "Database URL",
        value=os.getenv("DATABASE_URL", ""),
        type="password",
        placeholder="postgresql://user:pass@host:5432/db",
        help="Your PostgreSQL connection string",
    )

    openai_key = st.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        placeholder="sk-...",
    )

    col1, col2 = st.columns(2)
    with col1:
        max_rows = st.number_input("Max rows", value=500, min_value=10, max_value=5000, step=50)
    with col2:
        read_only = st.toggle("Read only", value=True, help="Block INSERT/UPDATE/DELETE")

    if st.button("🔌 Connect", use_container_width=True):
        if not db_url:
            st.error("Please enter a Database URL")
        elif not openai_key:
            st.error("Please enter an OpenAI API Key")
        else:
            with st.spinner("Connecting..."):
                try:
                    db = get_db_connection(db_url)
                    if not db.test_connection():
                        st.error("❌ Could not connect. Check your DATABASE_URL.")
                    else:
                        agent = NL2SQLAgent(db, openai_api_key=openai_key)
                        st.session_state.agent = agent
                        st.session_state.db = db
                        st.session_state.connected = True
                        st.session_state.schema_text = agent.get_schema_summary()
                        st.session_state.table_stats = agent.get_table_stats()
                        st.success("✅ Connected!")
                except Exception as e:
                    st.error(f"Connection failed: {e}")

    # ── Schema explorer ──────────────────────────────────────────────
    if st.session_state.connected:
        st.divider()
        st.markdown("### 📋 Schema Explorer")

        stats = st.session_state.table_stats
        for table, count in stats.items():
            st.caption(f"📁 **{table}** — {count:,} rows" if count >= 0 else f"📁 **{table}**")

        with st.expander("View full schema"):
            st.markdown(
                f'<div class="schema-table">{st.session_state.schema_text}</div>',
                unsafe_allow_html=True
            )

        st.divider()
        st.markdown("### 💡 Example Questions")
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

    # ── Query History ─────────────────────────────────────────────────
    st.divider()
    st.markdown("### 🕓 Query History")
    history = load_history()

    if history:
        if st.button("🗑 Clear history", use_container_width=True):
            clear_history()
            st.rerun()

        for entry in history[:8]:
            icon = "✅" if entry["success"] else "❌"
            ts = entry["timestamp"][:16].replace("T", " ")
            if st.button(
                f"{icon} {entry['question'][:40]}...\n_{ts}_",
                key=f"hist_{entry['id']}",
                use_container_width=True,
            ):
                st.session_state["inject_question"] = entry["question"]
    else:
        st.caption("No history yet")


# ─────────────────────────────────────────────────────────────────────
# Main area
# ─────────────────────────────────────────────────────────────────────
st.markdown("# 💬 Talk to Your Database")
st.caption("Ask questions in plain English — get SQL, results, and charts automatically")

if not st.session_state.connected:
    # ── Not connected state ──────────────────────────────────────────
    st.info("👈 Enter your Database URL and OpenAI API Key in the sidebar to get started.")

    st.markdown("---")
    st.markdown("### 🚀 How it works")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**1️⃣ Connect**\nEnter your PostgreSQL URL and OpenAI key")
    with col2:
        st.markdown("**2️⃣ Ask**\nType any question in plain English")
    with col3:
        st.markdown("**3️⃣ Agent runs**\nLangChain agent reads schema, writes + runs SQL")
    with col4:
        st.markdown("**4️⃣ Get results**\nSee answer, SQL, table, and auto-generated chart")

    with st.expander("📦 Don't have a database? Use the sample data"):
        st.markdown("Run this to spin up a demo PostgreSQL with e-commerce data:")
        st.code("""
docker run --name nl2sql-db \\
  -e POSTGRES_USER=admin \\
  -e POSTGRES_PASSWORD=password \\
  -e POSTGRES_DB=ecommerce \\
  -p 5432:5432 -d postgres:15

psql postgresql://admin:password@localhost:5432/ecommerce \\
  -f sample_data/seed.sql
        """, language="bash")
        st.caption("Then use: `postgresql://admin:password@localhost:5432/ecommerce`")

else:
    # ── Connected — main query interface ─────────────────────────────

    # Metrics row
    stats = st.session_state.table_stats
    cols = st.columns(len(stats) if stats else 1)
    for i, (table, count) in enumerate(stats.items()):
        with cols[i % len(cols)]:
            st.metric(table, f"{count:,} rows" if count >= 0 else "—")

    st.markdown("---")

    # ── Question input ───────────────────────────────────────────────
    injected = st.session_state.pop("inject_question", None)

    question = st.text_area(
        "Ask a question about your data",
        value=injected or "",
        height=80,
        placeholder='e.g. "Show me the top 10 customers by total order value"',
        key="question_input",
    )

    col_run, col_clear = st.columns([1, 5])
    with col_run:
        run_clicked = st.button("▶ Run Query", type="primary", use_container_width=True)
    with col_clear:
        if st.button("✕ Clear", use_container_width=False):
            st.session_state.messages = []
            st.rerun()

    # ── Run the agent ─────────────────────────────────────────────────
    if run_clicked and question.strip():
        with st.spinner("🤖 Agent is thinking... (reading schema → writing SQL → executing)"):
            result = st.session_state.agent.run(
                question=question.strip(),
                max_rows=max_rows,
            )
            st.session_state.last_result = result
            st.session_state.messages.append(result)
            save_query(result.question, result.sql_query, result.answer, result.success)

    # ── Display results ───────────────────────────────────────────────
    if st.session_state.messages:
        for result in reversed(st.session_state.messages):
            with st.container():
                # Question header
                st.markdown(f"**❓ {result.question}**")

                if not result.success:
                    st.markdown(
                        f'<div class="error-box">⚠️ {result.answer}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    # Answer
                    st.markdown(
                        f'<div class="answer-box">💬 {result.answer}</div>',
                        unsafe_allow_html=True
                    )

                    # SQL + Explanation in tabs
                    tab_sql, tab_data, tab_chart = st.tabs(["🔍 SQL", "📊 Data", "📈 Chart"])

                    with tab_sql:
                        st.markdown(
                            f'<div class="sql-block">{result.sql_query}</div>',
                            unsafe_allow_html=True
                        )
                        if result.explanation:
                            st.markdown(
                                f'<div class="explain-box">💡 {result.explanation}</div>',
                                unsafe_allow_html=True
                            )
                        if result.sql_query:
                            st.download_button(
                                "⬇ Download SQL",
                                data=result.sql_query,
                                file_name="query.sql",
                                mime="text/plain",
                                key=f"dl_sql_{result.question[:20]}",
                            )

                    with tab_data:
                        if result.columns and result.rows:
                            df = pd.DataFrame(result.rows, columns=result.columns)
                            st.dataframe(df, use_container_width=True, height=300)
                            st.caption(f"{len(result.rows)} rows returned")

                            csv = df.to_csv(index=False)
                            st.download_button(
                                "⬇ Download CSV",
                                data=csv,
                                file_name="results.csv",
                                mime="text/csv",
                                key=f"dl_csv_{result.question[:20]}",
                            )
                        else:
                            st.caption("No tabular data to display for this query.")

                    with tab_chart:
                        if result.columns and result.rows:
                            fig = render_chart(
                                result.columns,
                                result.rows,
                                title=result.question[:60],
                            )
                            if fig:
                                st.plotly_chart(fig, use_container_width=True)
                            else:
                                st.caption("No suitable chart could be auto-generated for this result shape.")
                        else:
                            st.caption("No data to chart.")

                st.markdown("---")
