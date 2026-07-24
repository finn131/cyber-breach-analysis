"""Interactive data explorer page."""

from __future__ import annotations

from pathlib import Path
import sys

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dashboard.components.loader import load_processed_data  # noqa: E402
from dashboard.components.sidebar import render_sidebar  # noqa: E402
from dashboard.utils.helpers import apply_filters, configure_page, get_filtered_download_name, load_css  # noqa: E402


configure_page("Data Explorer | Cyber Breach Analysis")
load_css()


def _search_table(df: pd.DataFrame, query: str) -> pd.DataFrame:
    if not query.strip():
        return df

    query = query.strip().lower()
    text_columns = [column for column in df.columns if df[column].dtype == "object" or str(df[column].dtype) == "string"]
    if not text_columns:
        return df

    mask = pd.Series(False, index=df.index)
    for column in text_columns:
        mask = mask | df[column].astype(str).str.lower().str.contains(query, na=False)
    return df.loc[mask].copy()


def main() -> None:
    """Render the data explorer."""

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

    st.markdown('<div class="section-title">Data Explorer</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-subtitle">Search, sort, filter, and download the complete processed dataset.</div>', unsafe_allow_html=True)

    local_search = st.text_input(
        "Search within the filtered dataset",
        placeholder="Search any field in the table",
        key="table_search",
    )
    table_df = _search_table(filtered_df, local_search)

    if table_df.empty:
        st.info("No rows match the local table search. Clear the search to see the filtered dataset.")
        st.stop()

    sortable_columns = [column for column in table_df.columns if column not in {"CompromisedData"}]
    sort_column = st.selectbox("Sort by", options=sortable_columns, index=sortable_columns.index("PwnCount") if "PwnCount" in sortable_columns else 0)
    sort_order = st.radio("Sort order", options=["Descending", "Ascending"], horizontal=True)
    ascending = sort_order == "Ascending"

    if sort_column in table_df.columns:
        table_df = table_df.sort_values(sort_column, ascending=ascending, na_position="last")

    export_name = get_filtered_download_name(filters)
    st.download_button(
        label="Download filtered CSV",
        data=table_df.to_csv(index=False).encode("utf-8"),
        file_name=export_name,
        mime="text/csv",
    )

    st.dataframe(
        table_df,
        use_container_width=True,
        hide_index=True,
        height=680,
    )


if __name__ == "__main__":
    main()
