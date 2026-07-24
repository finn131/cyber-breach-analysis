"""Overview page for the dashboard."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.charts import (  # noqa: E402
    breaches_per_year_chart,
    records_exposed_per_year_chart,
    top_domains_chart,
    top_largest_breaches_chart,
)
from dashboard.components.loader import load_processed_data  # noqa: E402
from dashboard.components.metrics import MetricCard, render_metric_cards  # noqa: E402
from dashboard.components.sidebar import render_sidebar  # noqa: E402
from dashboard.utils.helpers import apply_filters, configure_page, format_date, get_recent_records, load_css, summarize_dataframe  # noqa: E402


configure_page("Overview | Cyber Breach Analysis")
load_css()


def main() -> None:
    """Render the overview page."""

    try:
        df = load_processed_data()
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    filters = render_sidebar(df)
    filtered_df = apply_filters(df, filters)

    if filtered_df.empty:
        st.warning("No records match the current filters. Please widen your selection.")
        st.stop()

    summary = summarize_dataframe(filtered_df)

    st.markdown('<div class="section-title">Overview</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Key breach metrics and the highest-impact views of the filtered dataset.</div>', unsafe_allow_html=True)

    render_metric_cards(
        [
            MetricCard("Total Breaches", summary["total_breaches"]),
            MetricCard("Total Services", summary["total_services"]),
            MetricCard("Total Domains", summary["total_domains"]),
            MetricCard("Total Records Exposed", summary["total_records_exposed"]),
            MetricCard("Earliest Breach", format_date(summary["earliest_breach"])),
            MetricCard("Latest Breach", format_date(summary["latest_breach"])),
        ]
    )

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(breaches_per_year_chart(filtered_df), use_container_width=True, config={"displayModeBar": True})
    with c2:
        st.plotly_chart(records_exposed_per_year_chart(filtered_df), use_container_width=True, config={"displayModeBar": True})

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(top_largest_breaches_chart(filtered_df, n=10), use_container_width=True, config={"displayModeBar": True})
    with c4:
        st.plotly_chart(top_domains_chart(filtered_df, n=10), use_container_width=True, config={"displayModeBar": True})

    st.markdown("---")
    st.markdown('<div class="section-title">Recent Records</div>', unsafe_allow_html=True)
    recent = get_recent_records(filtered_df, n=12)
    st.dataframe(
        recent.loc[:, [column for column in ["Name", "Domain", "BreachDate", "PwnCount", "VerifiedLabel", "CompromisedData"] if column in recent.columns]],
        use_container_width=True,
        hide_index=True,
    )


if __name__ == "__main__":
    main()
