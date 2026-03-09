"""
Talk to Your Database — NL2SQL Agent
Streamlit Frontend — Modern Dark UI
Run: uv run streamlit run app/ui/streamlit_app.py
"""

import os
import sys
import streamlit as st

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from dotenv import load_dotenv
load_dotenv()

from app.ui.styles import inject_custom_css
from app.ui.sidebar import render_sidebar
from app.ui.main_content import render_main_content

# ─── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QueryMind · NL2SQL",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Design System ─────────────────────────────────────────────────────────────
inject_custom_css()

# ─── Session state ──────────────────────────────────────────────────────────────
def init_state():
    defaults = {
        "agent": None, "db": None, "connected": False,
        "messages": [], "last_result": None,
        "schema_text": "", "table_stats": {},
        "max_rows": 500, "read_only": True
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ─── Composing UI ───────────────────────────────────────────────────────────────
render_sidebar()
render_main_content()
