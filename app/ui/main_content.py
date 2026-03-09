import html
import pandas as pd
import streamlit as st
from datetime import datetime

from app.utils.query_history import save_query
from app.utils.chart_renderer import render_chart

def render_main_content():
    """Renders the main content area of the application."""
    if not st.session_state.connected:
        _render_landing_page()
    else:
        _render_query_console()

def _render_landing_page():
    """Renders the splash screen and feature overview when disconnected."""
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

def _render_query_console():
    """Renders the AI chat interface, metrics, and result tabs."""
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
        run_clicked = False
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
            max_rows = st.session_state.get("max_rows", 500)
            result = st.session_state.agent.run(
                question=question.strip(),
                max_rows=max_rows,
            )
            st.session_state.last_result = result
            st.session_state.messages.append(result)
            save_query(result.question, result.sql_query, result.answer, result.success)

    # Results History
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
                            key=f"dl_sql_{hash(result.question)}_{now}",
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
                                key=f"dl_csv_{hash(result.question)}_{now}",
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
