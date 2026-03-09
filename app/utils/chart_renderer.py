import re
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Optional


def render_chart(columns: List[str], rows: List[list], title: str = "") -> Optional[go.Figure]:
    """
    Auto-detect the best chart type from query result columns/rows.

    Rules:
    - 1 text column + 1 numeric column  → Bar chart
    - 1 date/time column + 1 numeric    → Line chart
    - 2 numeric columns                 → Scatter plot
    - Otherwise                         → No chart (just table)
    """
    if not columns or not rows:
        return None

    df = pd.DataFrame(rows, columns=columns)

    # Identify column types
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    text_cols = df.select_dtypes(include="object").columns.tolist()
    # Only check non-numeric columns for date-likeness to avoid misclassifying revenue etc.
    date_cols = [c for c in text_cols if _looks_like_date(c, df)]

    # ── Line chart: date + numeric ──────────────────────────────────
    if date_cols and numeric_cols:
        x_col = date_cols[0]
        y_col = numeric_cols[0]
        try:
            df[x_col] = pd.to_datetime(df[x_col])
            df = df.sort_values(x_col)
        except Exception:
            pass
        fig = px.line(
            df, x=x_col, y=y_col,
            title=title or f"{y_col} over {x_col}",
            markers=True,
            color_discrete_sequence=["#388BFD"],
        )
        return _style_fig(fig)

    # ── Bar chart: text category + numeric ──────────────────────────
    if text_cols and numeric_cols:
        x_col = text_cols[0]
        y_col = numeric_cols[0]
        df_plot = df[[x_col, y_col]].dropna()

        # Limit to top 20 for readability
        if len(df_plot) > 20:
            df_plot = df_plot.nlargest(20, y_col)

        fig = px.bar(
            df_plot, x=x_col, y=y_col,
            title=title or f"{y_col} by {x_col}",
            color_discrete_sequence=["#388BFD"],
        )
        fig.update_layout(xaxis_tickangle=-35)
        return _style_fig(fig)

    # ── Scatter: two numeric columns ────────────────────────────────
    if len(numeric_cols) >= 2:
        fig = px.scatter(
            df, x=numeric_cols[0], y=numeric_cols[1],
            title=title or f"{numeric_cols[0]} vs {numeric_cols[1]}",
            color_discrete_sequence=["#388BFD"],
        )
        return _style_fig(fig)

    return None


def _looks_like_date(col_name: str, df: pd.DataFrame) -> bool:
    """Heuristic: column name contains date/time keywords OR values have explicit date separators."""
    date_keywords = {"date", "time", "month", "year", "day", "week", "created", "updated"}
    # Split column name into words (handles: order_date, createdAt, updated_time, etc.)
    tokens = set(re.split(r"[_\-\s]+", col_name.lower()))
    if tokens & date_keywords:
        return True
    # Skip numeric columns — never treat plain numbers as dates
    if pd.api.types.is_numeric_dtype(df[col_name]):
        return False
    # Only classify as date if values contain explicit date separators: 2024-01 or 01/01/2024
    # We deliberately do NOT call pd.to_datetime — pandas 2.x parses arbitrary strings.
    date_sep_pattern = re.compile(r"\d{4}-\d{1,2}|\d{1,2}/\d{1,2}/\d{2,4}|\d{4}/\d{1,2}")
    sample = df[col_name].dropna().head(5).astype(str)
    return any(date_sep_pattern.search(v) for v in sample)


def _style_fig(fig: go.Figure) -> go.Figure:
    """Apply dark theme styling to all charts."""
    fig.update_layout(
        plot_bgcolor="#0D1117",
        paper_bgcolor="#161B22",
        font=dict(family="Inter, -apple-system, sans-serif", color="#8B949E", size=12),
        title_font=dict(color="#E6EDF3", size=14, family="Inter"),
        margin=dict(l=40, r=20, t=50, b=40),
        xaxis=dict(
            gridcolor="#21262D", linecolor="#30363D",
            tickfont=dict(color="#8B949E"),
            title_font=dict(color="#8B949E"),
        ),
        yaxis=dict(
            gridcolor="#21262D", linecolor="#30363D",
            tickfont=dict(color="#8B949E"),
            title_font=dict(color="#8B949E"),
        ),
    )
    return fig
