"""Trends page for the dashboard."""

from __future__ import annotations

from pathlib import Path
import sys

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.charts import (  # noqa: E402
    exposure_box_plot,
    records_exposed_per_year_chart,
    rolling_average_chart,
    trend_area_chart,
    trend_line_chart,
    yoy_growth_chart,
)
from dashboard.components.loader import load_processed_data  # noqa: E402
from dashboard.components.sidebar import render_sidebar  # noqa: E402
from dashboard.utils.helpers import apply_filters, configure_page, load_css  # noqa: E402


configure_page("Trends | Cyber Breach Analysis")
load_css()


def main() -> None:
    """Render the trends page."""

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

    st.markdown('<div class="section-title">Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Year-over-year movement, rolling behavior, and distribution views.</div>', unsafe_allow_html=True)

    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(trend_line_chart(filtered_df), use_container_width=True, config={"displayModeBar": True})
    with c2:
        st.plotly_chart(trend_area_chart(filtered_df), use_container_width=True, config={"displayModeBar": True})

    c3, c4 = st.columns(2)
    with c3:
        st.plotly_chart(rolling_average_chart(filtered_df, window=3), use_container_width=True, config={"displayModeBar": True})
    with c4:
        st.plotly_chart(yoy_growth_chart(filtered_df), use_container_width=True, config={"displayModeBar": True})

    st.markdown("---")
    c5, c6 = st.columns(2)
    with c5:
        st.plotly_chart(records_exposed_per_year_chart(filtered_df), use_container_width=True, config={"displayModeBar": True})
    with c6:
        st.plotly_chart(exposure_box_plot(filtered_df), use_container_width=True, config={"displayModeBar": True})


if __name__ == "__main__":
    main()
