"""Service analysis page for the dashboard."""

from __future__ import annotations

from pathlib import Path
import html
import sys

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.charts import top_services_chart  # noqa: E402
from dashboard.components.loader import load_processed_data  # noqa: E402
from dashboard.components.metrics import MetricCard, render_metric_cards  # noqa: E402
from dashboard.components.sidebar import render_sidebar  # noqa: E402
from dashboard.utils.helpers import apply_filters, configure_page, format_date, format_compromised_data, load_css  # noqa: E402


configure_page("Service Analysis | Cyber Breach Analysis")
load_css()


def _service_options(df: pd.DataFrame) -> list[str]:
    if "Name" not in df.columns:
        return []
    return sorted(df["Name"].dropna().astype(str).unique().tolist())


def main() -> None:
    """Render the service analysis page."""

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

    st.markdown('<div class="section-title">Service Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Inspect the largest services and drill into a single breach record.</div>', unsafe_allow_html=True)

    st.plotly_chart(top_services_chart(filtered_df, n=20), use_container_width=True, config={"displayModeBar": True})

    service_names = _service_options(filtered_df)
    if not service_names:
        st.warning("No services available for the selected filters.")
        st.stop()

    selected_service = st.selectbox("Select a service", options=service_names, index=0)
    service_rows = filtered_df.loc[filtered_df["Name"].astype(str) == selected_service].sort_values("PwnCount", ascending=False)
    service_row = service_rows.iloc[0]

    render_metric_cards(
        [
            MetricCard("Service Name", service_row.get("Name", "Unknown")),
            MetricCard("Domain", service_row.get("Domain", "Unknown")),
            MetricCard("Breach Date", format_date(service_row.get("BreachDate"))),
            MetricCard("Records Exposed", service_row.get("PwnCount", 0)),
        ]
    )

    st.markdown("---")
    detail_left, detail_right = st.columns([1.2, 1])
    with detail_left:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">Service Detail Card</div>
                <div class="insight-body"><strong>Description</strong><br>{html.escape(str(service_row.get('Description', 'Unknown')))}</div>
                <div class="insight-body" style="margin-top:0.9rem;"><strong>Compromised Data</strong><br>{html.escape(format_compromised_data(service_row.get('DataClasses')))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with detail_right:
        st.markdown(
            f"""
            <div class="insight-card">
                <div class="insight-title">Breach Snapshot</div>
                <div class="insight-body"><strong>Title:</strong> {html.escape(str(service_row.get('Title', 'Unknown')))}</div>
                <div class="insight-body"><strong>Added Date:</strong> {html.escape(format_date(service_row.get('AddedDate')))}</div>
                <div class="insight-body"><strong>Modified Date:</strong> {html.escape(format_date(service_row.get('ModifiedDate')))}</div>
                <div class="insight-body"><strong>Verification:</strong> {html.escape(str(service_row.get('VerifiedLabel', 'Unknown')))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
