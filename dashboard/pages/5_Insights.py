"""Insights page for the dashboard."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.charts import (  # noqa: E402
    data_classes_treemap,
    exposure_box_plot,
    exposure_histogram,
    verified_status_pie_chart,
)
from dashboard.components.loader import load_processed_data  # noqa: E402
from dashboard.components.metrics import MetricCard, render_metric_cards  # noqa: E402
from dashboard.components.sidebar import render_sidebar  # noqa: E402
from dashboard.utils.helpers import apply_filters, compact_number, configure_page, load_css, summarize_dataframe  # noqa: E402


configure_page("Insights | Cyber Breach Analysis")
load_css()


def _insight_card(title: str, body: str) -> str:
    return f"""
    <div class="insight-card">
        <div class="insight-title">{title}</div>
        <div class="insight-body">{body}</div>
    </div>
    """


def main() -> None:
    """Render the insights page."""

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

    st.markdown('<div class="section-title">Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Core statistics, executive takeaways, and supporting distribution charts.</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="chip-row">
            <span class="chip"><strong>Lens:</strong> executive summary</span>
            <span class="chip"><strong>Signal:</strong> biggest risks</span>
            <span class="chip"><strong>Support:</strong> distribution charts</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    render_metric_cards(
        [
            MetricCard("Biggest Breach", summary["biggest_breach"]),
            MetricCard("Average Records Exposed", summary["average_records_exposed"]),
            MetricCard("Median Records", summary["median_records_exposed"]),
            MetricCard("Most Common Domain", summary["most_common_domain"]),
            MetricCard("Total Unique Services", summary["unique_services"]),
        ]
    )

    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)
    left, right = st.columns(2)
    with left:
        st.plotly_chart(verified_status_pie_chart(filtered_df), use_container_width=True, config={"displayModeBar": True})
    with right:
        st.plotly_chart(exposure_histogram(filtered_df), use_container_width=True, config={"displayModeBar": True})

    left2, right2 = st.columns(2)
    with left2:
        st.plotly_chart(data_classes_treemap(filtered_df), use_container_width=True, config={"displayModeBar": True})
    with right2:
        st.plotly_chart(exposure_box_plot(filtered_df), use_container_width=True, config={"displayModeBar": True})

    st.markdown('<div class="soft-divider"></div>', unsafe_allow_html=True)
    insight_left, insight_mid, insight_right = st.columns(3)
    with insight_left:
        st.markdown(
            _insight_card(
                "Biggest Breach",
                f"The largest filtered breach exposed <strong>{compact_number(summary['biggest_breach'])}</strong> accounts.",
            ),
            unsafe_allow_html=True,
        )
    with insight_mid:
        st.markdown(
            _insight_card(
                "Exposure Center",
                f"Average exposure sits near <strong>{compact_number(summary['average_records_exposed'])}</strong> records, while the median is <strong>{compact_number(summary['median_records_exposed'])}</strong>.",
            ),
            unsafe_allow_html=True,
        )
    with insight_right:
        st.markdown(
            _insight_card(
                "Domain Concentration",
                f"<strong>{summary['most_common_domain']}</strong> appears most often, with <strong>{summary['most_common_domain_count']}</strong> records in the filtered dataset.",
            ),
            unsafe_allow_html=True,
        )


if __name__ == "__main__":
    main()
