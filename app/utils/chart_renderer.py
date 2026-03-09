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
    date_cols = [c for c in df.columns if _looks_like_date(c, df)]

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
            color_discrete_sequence=["#B85C38"],
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
            color_discrete_sequence=["#B85C38"],
        )
        fig.update_layout(xaxis_tickangle=-35)
        return _style_fig(fig)

    # ── Scatter: two numeric columns ────────────────────────────────
    if len(numeric_cols) >= 2:
        fig = px.scatter(
            df, x=numeric_cols[0], y=numeric_cols[1],
            title=title or f"{numeric_cols[0]} vs {numeric_cols[1]}",
            color_discrete_sequence=["#B85C38"],
        )
        return _style_fig(fig)

    return None


def _looks_like_date(col_name: str, df: pd.DataFrame) -> bool:
    """Heuristic: column name contains date/time keywords OR values parse as dates."""
    date_keywords = ["date", "time", "month", "year", "day", "week", "created", "updated", "at"]
    if any(kw in col_name.lower() for kw in date_keywords):
        return True
    try:
        pd.to_datetime(df[col_name].dropna().head(3))
        return True
    except Exception:
        return False


def _style_fig(fig: go.Figure) -> go.Figure:
    """Apply consistent warm styling to all charts."""
    fig.update_layout(
        plot_bgcolor="#FDF6F0",
        paper_bgcolor="#FDF6F0",
        font=dict(family="Inter, sans-serif", color="#2C1A0E"),
        title_font_size=14,
        margin=dict(l=40, r=20, t=50, b=40),
    )
    return fig
