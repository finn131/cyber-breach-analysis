"""Plotly chart builders used throughout the dashboard."""

from __future__ import annotations

from typing import Iterable

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from dashboard.utils.helpers import (
    add_derived_columns,
    get_rolling_average,
    get_yearly_counts,
    get_yearly_records,
    get_yoy_growth,
    parse_list_like,
)


BACKGROUND = "#0D1117"
PANEL = "#161B22"
TEXT = "#C9D1D9"
TITLE = "#F0F6FC"
ACCENT = "#00E5FF"
SUCCESS = "#00C853"
DANGER = "#FF5252"
COLORWAY = [ACCENT, SUCCESS, DANGER, "#7C4DFF", "#FFB300", "#00B8D4"]


def _style_figure(fig: go.Figure, title: str | None = None, height: int = 420) -> go.Figure:
    """Apply the dashboard theme to a Plotly figure."""

    fig.update_layout(
        template="plotly_dark",
        height=height,
        paper_bgcolor=BACKGROUND,
        plot_bgcolor=PANEL,
        font=dict(color=TEXT, family="Inter, Segoe UI, Arial, sans-serif"),
        colorway=COLORWAY,
        margin=dict(l=20, r=20, t=60, b=20),
        showlegend=True,
        title=dict(
            text=title,
            x=0.02,
            xanchor="left",
            font=dict(color=TITLE, size=20),
        )
        if title
        else None,
    )
    fig.update_xaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(gridcolor="rgba(255,255,255,0.08)", zerolinecolor="rgba(255,255,255,0.08)")
    return fig


def _prepare_yearly_frame(df: pd.DataFrame) -> pd.DataFrame:
    frame = add_derived_columns(df)
    if "BreachYear" not in frame.columns:
        return pd.DataFrame(columns=["BreachYear", "Count", "RecordsExposed"])
    yearly = (
        frame.dropna(subset=["BreachYear"])
        .groupby("BreachYear", as_index=False)
        .agg(Count=("BreachYear", "size"), RecordsExposed=("PwnCount", "sum"))
        .sort_values("BreachYear")
        .reset_index(drop=True)
    )
    return yearly


def breaches_per_year_chart(df: pd.DataFrame) -> go.Figure:
    """Return a line chart of breach counts per year."""

    yearly = get_yearly_counts(df)
    fig = px.line(
        yearly,
        x="BreachYear",
        y="Count",
        markers=True,
        labels={"BreachYear": "Breach year", "Count": "Breaches"},
    )
    fig.update_traces(line=dict(color=ACCENT, width=3), marker=dict(size=8))
    return _style_figure(fig, "Breaches per Year")


def records_exposed_per_year_chart(df: pd.DataFrame) -> go.Figure:
    """Return an area chart of exposed records per year."""

    yearly = get_yearly_records(df)
    fig = px.area(
        yearly,
        x="BreachYear",
        y="RecordsExposed",
        labels={"BreachYear": "Breach year", "RecordsExposed": "Records exposed"},
    )
    fig.update_traces(line=dict(color=SUCCESS, width=3), fillcolor="rgba(0, 200, 83, 0.25)")
    return _style_figure(fig, "Records Exposed per Year")


def top_largest_breaches_chart(df: pd.DataFrame, n: int = 10) -> go.Figure:
    """Return a horizontal bar chart of the largest breaches."""

    frame = (
        add_derived_columns(df)
        .sort_values(["PwnCount", "BreachDate"], ascending=[False, False])
        .head(n)
        .copy()
    )
    frame["DisplayName"] = frame["Title"].fillna(frame["Name"]).astype(str)
    fig = px.bar(
        frame.sort_values("PwnCount", ascending=True),
        x="PwnCount",
        y="DisplayName",
        orientation="h",
        labels={"PwnCount": "Records exposed", "DisplayName": "Service"},
        color="PwnCount",
        color_continuous_scale=["#004E64", ACCENT],
        hover_data=["Domain", "BreachDate", "VerifiedLabel"],
    )
    fig.update_layout(coloraxis_showscale=False)
    return _style_figure(fig, "Top 10 Largest Breaches", height=480)


def top_domains_chart(df: pd.DataFrame, n: int = 10) -> go.Figure:
    """Return a horizontal bar chart of the most common domains."""

    frame = add_derived_columns(df)
    if "Domain" not in frame.columns:
        empty = pd.DataFrame({"Domain": [], "Count": []})
    else:
        empty = (
            frame["Domain"]
            .fillna("Unknown")
            .replace("", "Unknown")
            .value_counts()
            .head(n)
            .rename_axis("Domain")
            .reset_index(name="Count")
        )
    fig = px.bar(
        empty.sort_values("Count", ascending=True),
        x="Count",
        y="Domain",
        orientation="h",
        labels={"Count": "Occurrences", "Domain": "Domain"},
        color="Count",
        color_continuous_scale=["#002B36", ACCENT],
    )
    fig.update_layout(coloraxis_showscale=False)
    return _style_figure(fig, "Top Domains", height=420)


def trend_line_chart(df: pd.DataFrame) -> go.Figure:
    """Return a line chart for yearly breaches and exposures."""

    yearly = _prepare_yearly_frame(df)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=yearly["BreachYear"],
            y=yearly["Count"],
            mode="lines+markers",
            name="Breaches",
            line=dict(color=ACCENT, width=3),
            hovertemplate="Year %{x}<br>Breaches %{y:,}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=yearly["BreachYear"],
            y=yearly["RecordsExposed"],
            mode="lines+markers",
            name="Records exposed",
            line=dict(color=SUCCESS, width=3),
            hovertemplate="Year %{x}<br>Records exposed %{y:,}<extra></extra>",
        )
    )
    fig.update_xaxes(title_text="Breach year")
    fig.update_yaxes(title_text="Count / records exposed")
    return _style_figure(fig, "Breach and Exposure Trends")


def trend_area_chart(df: pd.DataFrame) -> go.Figure:
    """Return an area chart for yearly exposed records."""

    yearly = get_yearly_records(df)
    fig = px.area(
        yearly,
        x="BreachYear",
        y="RecordsExposed",
        labels={"BreachYear": "Breach year", "RecordsExposed": "Records exposed"},
    )
    fig.update_traces(fillcolor="rgba(0, 229, 255, 0.25)", line=dict(color=ACCENT, width=3))
    return _style_figure(fig, "Records Exposed Area Trend")


def rolling_average_chart(df: pd.DataFrame, window: int = 3) -> go.Figure:
    """Return a rolling average chart for yearly exposure."""

    rolling = get_rolling_average(df, window=window)
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=rolling["BreachYear"],
            y=rolling["RecordsExposed"],
            mode="lines+markers",
            name="Records exposed",
            line=dict(color="#8B949E", width=2, dash="dot"),
            hovertemplate="Year %{x}<br>Records exposed %{y:,}<extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=rolling["BreachYear"],
            y=rolling["RollingAverage"],
            mode="lines+markers",
            name=f"{window}-year rolling average",
            line=dict(color=SUCCESS, width=4),
            hovertemplate="Year %{x}<br>Rolling average %{y:,.0f}<extra></extra>",
        )
    )
    fig.update_xaxes(title_text="Breach year")
    fig.update_yaxes(title_text="Records exposed")
    return _style_figure(fig, f"{window}-Year Rolling Average")


def yoy_growth_chart(df: pd.DataFrame) -> go.Figure:
    """Return a year-over-year growth chart."""

    yoy = get_yoy_growth(df)
    fig = go.Figure(
        data=[
            go.Bar(
                x=yoy["BreachYear"],
                y=yoy["YoYGrowth"],
                marker_color=ACCENT,
                hovertemplate="Year %{x}<br>Growth %{y:.1f}%<extra></extra>",
            )
        ]
    )
    fig.add_hline(y=0, line_width=1, line_color="#8B949E")
    fig.update_xaxes(title_text="Breach year")
    fig.update_yaxes(title_text="Year-over-year growth (%)")
    return _style_figure(fig, "Year-over-Year Growth", height=420)


def top_services_chart(df: pd.DataFrame, n: int = 20) -> go.Figure:
    """Return a bar chart of the top services by records exposed."""

    frame = (
        add_derived_columns(df)
        .sort_values(["PwnCount", "BreachDate"], ascending=[False, False])
        .head(n)
        .copy()
    )
    frame["DisplayName"] = frame["Title"].fillna(frame["Name"]).astype(str)
    fig = px.bar(
        frame.sort_values("PwnCount", ascending=True),
        x="PwnCount",
        y="DisplayName",
        orientation="h",
        labels={"PwnCount": "Records exposed", "DisplayName": "Service"},
        hover_data=["Domain", "BreachDate", "VerifiedLabel"],
        color="PwnCount",
        color_continuous_scale=["#003B49", ACCENT],
    )
    fig.update_layout(coloraxis_showscale=False)
    return _style_figure(fig, "Top 20 Services by Exposure", height=640)


def verified_status_pie_chart(df: pd.DataFrame) -> go.Figure:
    """Return a pie chart showing verification status."""

    frame = add_derived_columns(df)
    counts = frame["VerifiedLabel"].value_counts().reset_index()
    counts.columns = ["VerifiedLabel", "Count"]
    fig = go.Figure(
        data=[
            go.Pie(
                labels=counts["VerifiedLabel"],
                values=counts["Count"],
                hole=0.45,
                marker=dict(colors=[SUCCESS, DANGER]),
                textinfo="label+percent",
                hovertemplate="%{label}<br>%{value:,} records<extra></extra>",
            )
        ]
    )
    return _style_figure(fig, "Verified vs Unverified", height=420)


def exposure_histogram(df: pd.DataFrame) -> go.Figure:
    """Return a histogram of records exposed."""

    frame = add_derived_columns(df)
    fig = px.histogram(
        frame,
        x="PwnCount",
        nbins=40,
        labels={"PwnCount": "Records exposed"},
        color_discrete_sequence=[ACCENT],
    )
    fig.update_xaxes(type="log")
    fig.update_traces(hovertemplate="Records exposed %{x:,}<br>Count %{y}<extra></extra>")
    return _style_figure(fig, "Exposure Distribution", height=420)


def data_classes_treemap(df: pd.DataFrame) -> go.Figure:
    """Return a treemap of the most common data classes."""

    frame = add_derived_columns(df)
    if "DataClasses" not in frame.columns:
        treemap_df = pd.DataFrame({"DataClass": [], "Count": []})
    else:
        exploded = frame["DataClasses"].apply(parse_list_like).explode().dropna()
        treemap_df = (
            exploded.value_counts().reset_index()
            .rename(columns={"index": "DataClass", 0: "Count", "count": "Count"})
        )
        treemap_df.columns = ["DataClass", "Count"]

    fig = px.treemap(
        treemap_df,
        path=["DataClass"],
        values="Count",
        color="Count",
        color_continuous_scale=["#0B2E3C", ACCENT],
    )
    fig.update_traces(
        hovertemplate="<b>%{label}</b><br>Count %{value:,}<extra></extra>"
    )
    fig.update_layout(coloraxis_showscale=False)
    return _style_figure(fig, "Data Class Treemap", height=520)


def exposure_box_plot(df: pd.DataFrame) -> go.Figure:
    """Return a box plot for records exposed by verification status."""

    frame = add_derived_columns(df)
    fig = px.box(
        frame,
        x="VerifiedLabel",
        y="PwnCount",
        points="outliers",
        labels={"VerifiedLabel": "Verification status", "PwnCount": "Records exposed"},
        color="VerifiedLabel",
        color_discrete_sequence=[SUCCESS, DANGER],
    )
    fig.update_traces(
        hovertemplate="%{x}<br>Records exposed %{y:,}<extra></extra>"
    )
    fig.update_layout(showlegend=False)
    return _style_figure(fig, "Exposure Box Plot", height=420)

