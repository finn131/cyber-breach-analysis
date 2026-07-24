"""Landing page for the Cyber Breach Analysis dashboard."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.charts import breaches_per_year_chart, top_domains_chart  # noqa: E402
from dashboard.components.loader import load_processed_data  # noqa: E402
from dashboard.components.metrics import MetricCard, render_metric_cards  # noqa: E402
from dashboard.components.sidebar import render_sidebar  # noqa: E402
from dashboard.utils.helpers import (  # noqa: E402
    apply_filters,
    compact_number,
    configure_page,
    format_date,
    get_recent_records,
    load_css,
    summarize_dataframe,
)


configure_page("Cyber Breach Analysis Dashboard")
load_css()


def main() -> None:
    """Render the dashboard landing page."""

    try:
        with st.spinner("Loading processed breach data..."):
            df = load_processed_data()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    if df.empty:
        st.warning("The processed dataset is empty. Please verify the input file.")
        st.stop()

    filters = render_sidebar(df)
    filtered_df = apply_filters(df, filters)

    st.markdown(
        """
        <div class="hero-shell">
            <div class="hero-kicker">Cyber Breach Analysis Dashboard</div>
            <h1 class="hero-title">Interactive Data Analysis using Streamlit, Pandas and Plotly</h1>
            <p class="hero-subtitle">
                Explore breach activity, exposed account volumes, recurring domains, and service-level
                details using a modern multi-page dashboard built on the processed cybersecurity dataset.
            </p>
            <p class="hero-note">
                Use the sidebar filters to refine every page. Search a service, narrow the years, or focus
                on verified incidents to explore the breach landscape from different angles.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if filtered_df.empty:
        st.warning("No records match the current filters. Try widening the sidebar filters.")
        st.stop()

    summary = summarize_dataframe(filtered_df)

    st.markdown('<div class="section-title">Dataset Summary</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">The metrics below react to the current sidebar filters.</div>', unsafe_allow_html=True)

    render_metric_cards(
        [
            MetricCard("Total Breaches", summary["total_breaches"]),
            MetricCard("Total Services", summary["total_services"]),
            MetricCard("Total Domains", summary["total_domains"]),
            MetricCard("Total Records Exposed", summary["total_records_exposed"]),
            MetricCard("Earliest Breach", summary["earliest_breach"], subtitle=format_date(summary["earliest_breach"])),
            MetricCard("Latest Breach", summary["latest_breach"], subtitle=format_date(summary["latest_breach"])),
        ]
    )

    st.markdown("---")
    left, right = st.columns(2)
    with left:
        st.plotly_chart(breaches_per_year_chart(filtered_df), use_container_width=True, config={"displayModeBar": True})
    with right:
        st.plotly_chart(top_domains_chart(filtered_df), use_container_width=True, config={"displayModeBar": True})

    st.markdown("---")
    st.markdown('<div class="section-title">Recent Records</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Most recent breach entries in the filtered dataset.</div>', unsafe_allow_html=True)

    recent = get_recent_records(filtered_df, n=10)
    show_columns = [
        column
        for column in ["Name", "Domain", "BreachDate", "PwnCount", "VerifiedLabel", "CompromisedData"]
        if column in recent.columns
    ]
    st.dataframe(
        recent.loc[:, show_columns],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown(
        """
        <div class="footer-note">
            Navigate through the sidebar pages to open the Overview, Trends, Service Analysis, Data Explorer, and Insights views.
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
