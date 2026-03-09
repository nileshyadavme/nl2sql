import os
import html
import streamlit as st

from app.database.connection import get_db_connection, reset_db_connection
from app.agents.nl2sql_agent import NL2SQLAgent
from app.utils.query_history import load_history, clear_history

def render_sidebar():
    """Renders the left-hand navigation sidebar."""
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
            st.session_state.max_rows = st.number_input(
                "Max rows", 
                value=st.session_state.get("max_rows", 500), 
                min_value=10, 
                max_value=5000, 
                step=50
            )
        with c2:
            st.session_state.read_only = st.toggle(
                "Read only", 
                value=st.session_state.get("read_only", True)
            )

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
