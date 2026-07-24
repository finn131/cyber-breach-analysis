"""Sidebar controls shared across dashboard pages."""

from __future__ import annotations

from dataclasses import asdict

import pandas as pd
import streamlit as st

from dashboard.utils.helpers import DashboardFilters, format_date


def _available_years(df: pd.DataFrame) -> list[int]:
    if "BreachDate" not in df.columns:
        return []
    years = pd.to_datetime(df["BreachDate"], errors="coerce").dt.year.dropna().astype(int).unique()
    return sorted(years.tolist())


def _available_domains(df: pd.DataFrame) -> list[str]:
    if "Domain" not in df.columns:
        return []
    domains = (
        df["Domain"]
        .fillna("")
        .astype(str)
        .str.strip()
        .loc[lambda series: series != ""]
        .value_counts()
        .index.tolist()
    )
    return domains


def render_sidebar(df: pd.DataFrame) -> DashboardFilters:
    """Render the sidebar controls and return the chosen filters."""

    st.sidebar.markdown(
        """
        <div class="sidebar-brand">
            <div class="sidebar-kicker">Cyber Breach Analysis</div>
            <div class="sidebar-title">Dashboard Filters</div>
            <div class="sidebar-subtitle">Refine every page with the same controls.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    years = _available_years(df)
    domains = _available_domains(df)
    min_records = int(df["PwnCount"].fillna(0).min()) if "PwnCount" in df.columns else 0
    max_records = int(df["PwnCount"].fillna(0).max()) if "PwnCount" in df.columns else 0

    search_service = st.sidebar.text_input(
        "Search Service",
        placeholder="Search by service, domain, description, or data class",
        key="search_service",
    )

    selected_years = st.sidebar.multiselect(
        "Year Filter",
        options=years,
        default=[],
        key="year_filter",
        help="Select one or more breach years.",
    )

    selected_domains = st.sidebar.multiselect(
        "Domain Filter",
        options=domains,
        default=[],
        key="domain_filter",
        help="Search and select domains that should remain in the dataset.",
    )

    verified_filter = st.sidebar.selectbox(
        "Verified Filter",
        options=["All", "Verified only", "Unverified only"],
        index=0,
        key="verified_filter",
    )

    records_range = st.sidebar.slider(
        "Records Exposed",
        min_value=min_records,
        max_value=max_records if max_records >= min_records else min_records,
        value=(min_records, max_records if max_records >= min_records else min_records),
        key="records_range",
        help="Limit the range of exposed accounts.",
    )

    st.sidebar.caption(
        f"Current dataset range: {min_records:,} to {max_records:,} records exposed"
    )

    filters = DashboardFilters(
        search_service=search_service.strip(),
        years=tuple(int(year) for year in selected_years),
        domains=tuple(selected_domains),
        verified_filter=verified_filter,
        min_records=int(records_range[0]),
        max_records=int(records_range[1]),
    )
    return filters

