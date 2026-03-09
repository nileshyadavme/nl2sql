import streamlit as st

def inject_custom_css():
    """Injects the QueryMind dark theme and component styling into Streamlit."""
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
