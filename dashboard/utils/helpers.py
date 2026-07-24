"""Shared helpers for the Streamlit dashboard."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_breach_data.csv"
CSS_PATH = PROJECT_ROOT / "dashboard" / "assets" / "style.css"


@dataclass(slots=True)
class DashboardFilters:
    """Structured representation of sidebar filters."""

    search_service: str = ""
    years: tuple[int, ...] = ()
    domains: tuple[str, ...] = ()
    verified_filter: str = "All"
    min_records: int = 0
    max_records: int = 0


def load_css() -> None:
    """Inject dashboard CSS into the Streamlit app."""

    if CSS_PATH.exists():
        st.markdown(f"<style>{CSS_PATH.read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)


def configure_page(title: str) -> None:
    """Set a consistent page configuration."""

    st.set_page_config(
        page_title=title,
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="expanded",
    )


def compact_number(value: Any) -> str:
    """Format large numeric values using K/M/B suffixes."""

    if value is None or pd.isna(value):
        return "0"

    try:
        number = float(value)
    except (TypeError, ValueError):
        return str(value)

    sign = "-" if number < 0 else ""
    number = abs(number)
    thresholds = [
        (1_000_000_000_000, "T"),
        (1_000_000_000, "B"),
        (1_000_000, "M"),
        (1_000, "K"),
    ]
    for threshold, suffix in thresholds:
        if number >= threshold:
            scaled = number / threshold
            formatted = f"{scaled:.1f}".rstrip("0").rstrip(".")
            return f"{sign}{formatted}{suffix}"
    if float(number).is_integer():
        return f"{sign}{int(number)}"
    return f"{sign}{number:.0f}"


def format_date(value: Any) -> str:
    """Format datetime-like values for display."""

    if value is None or pd.isna(value):
        return "Unknown"

    timestamp = pd.to_datetime(value, errors="coerce")
    if pd.isna(timestamp):
        return "Unknown"
    return timestamp.strftime("%Y-%m-%d")


def parse_list_like(value: Any) -> list[str]:
    """Parse list-like string values such as DataClasses."""

    if value is None or pd.isna(value):
        return []

    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]

    text = str(value).strip()
    if not text:
        return []

    try:
        parsed = ast.literal_eval(text)
        if isinstance(parsed, list):
            return [str(item).strip() for item in parsed if str(item).strip()]
    except (ValueError, SyntaxError):
        pass

    items = []
    for raw_item in text.strip("[]").split(","):
        item = raw_item.strip().strip("'").strip('"').strip()
        if item:
            items.append(item)
    return items


def format_compromised_data(value: Any) -> str:
    """Convert a DataClasses cell into a readable comma-separated string."""

    items = parse_list_like(value)
    if not items:
        return "Unknown"
    return ", ".join(sorted({item.title() for item in items}))


def add_derived_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add reusable derived fields for filtering and display."""

    frame = df.copy()
    if "BreachDate" in frame.columns:
        frame["BreachYear"] = pd.to_datetime(frame["BreachDate"], errors="coerce").dt.year.astype("Int64")
    else:
        frame["BreachYear"] = pd.Series(dtype="Int64")

    if "DataClasses" in frame.columns:
        frame["CompromisedData"] = frame["DataClasses"].apply(format_compromised_data)
    else:
        frame["CompromisedData"] = "Unknown"

    if "IsVerified" in frame.columns:
        frame["VerifiedLabel"] = frame["IsVerified"].map({True: "Verified", False: "Unverified"}).fillna("Unknown")
    else:
        frame["VerifiedLabel"] = "Unknown"

    return frame


def apply_filters(df: pd.DataFrame, filters: DashboardFilters) -> pd.DataFrame:
    """Filter the dashboard dataframe using sidebar controls."""

    frame = add_derived_columns(df)
    mask = pd.Series(True, index=frame.index)

    if filters.search_service:
        query = filters.search_service.strip().lower()
        text_columns = [
            column
            for column in ["Name", "Title", "Domain", "Description", "DataClasses"]
            if column in frame.columns
        ]
        search_mask = pd.Series(False, index=frame.index)
        for column in text_columns:
            search_mask = search_mask | frame[column].astype(str).str.lower().str.contains(query, na=False)
        mask &= search_mask

    if filters.years:
        mask &= frame["BreachYear"].isin(filters.years)

    if filters.domains:
        domain_series = frame["Domain"].fillna("").astype(str)
        mask &= domain_series.isin(filters.domains)

    if filters.verified_filter == "Verified only" and "IsVerified" in frame.columns:
        mask &= frame["IsVerified"].fillna(False)
    elif filters.verified_filter == "Unverified only" and "IsVerified" in frame.columns:
        mask &= ~frame["IsVerified"].fillna(True)

    if "PwnCount" in frame.columns:
        mask &= frame["PwnCount"].fillna(0).between(filters.min_records, filters.max_records)

    filtered = frame.loc[mask].copy().reset_index(drop=True)
    return filtered


def summarize_dataframe(df: pd.DataFrame) -> dict[str, Any]:
    """Build summary values for the overview and insights pages."""

    frame = add_derived_columns(df)
    breach_dates = frame["BreachDate"].dropna() if "BreachDate" in frame.columns else pd.Series(dtype="datetime64[ns]")
    pwn = frame["PwnCount"].dropna() if "PwnCount" in frame.columns else pd.Series(dtype="float64")
    domains = frame["Domain"].replace("", pd.NA).dropna() if "Domain" in frame.columns else pd.Series(dtype="object")
    verified = frame["IsVerified"].dropna() if "IsVerified" in frame.columns else pd.Series(dtype="boolean")

    summary: dict[str, Any] = {
        "total_breaches": int(len(frame)),
        "total_services": int(frame["Name"].nunique()) if "Name" in frame.columns else 0,
        "total_domains": int(domains.nunique()) if not domains.empty else 0,
        "total_records_exposed": int(pwn.sum()) if not pwn.empty else 0,
        "earliest_breach": breach_dates.min() if not breach_dates.empty else pd.NaT,
        "latest_breach": breach_dates.max() if not breach_dates.empty else pd.NaT,
        "average_records_exposed": float(pwn.mean()) if not pwn.empty else 0.0,
        "median_records_exposed": float(pwn.median()) if not pwn.empty else 0.0,
        "biggest_breach": int(pwn.max()) if not pwn.empty else 0,
        "most_common_domain": str(domains.value_counts().index[0]) if not domains.empty else "Unknown",
        "most_common_domain_count": int(domains.value_counts().iloc[0]) if not domains.empty else 0,
        "unique_services": int(frame["Name"].nunique()) if "Name" in frame.columns else 0,
        "verified_count": int(verified.sum()) if not verified.empty else 0,
        "unverified_count": int((~verified).sum()) if not verified.empty else 0,
    }
    return summary


def get_yearly_counts(df: pd.DataFrame) -> pd.DataFrame:
    """Return breach counts by year."""

    frame = add_derived_columns(df)
    if "BreachYear" not in frame.columns:
        return pd.DataFrame(columns=["BreachYear", "Count"])
    year_counts = (
        frame.dropna(subset=["BreachYear"])
        .groupby("BreachYear", as_index=False)
        .size()
        .rename(columns={"size": "Count"})
        .sort_values("BreachYear")
        .reset_index(drop=True)
    )
    return year_counts


def get_yearly_records(df: pd.DataFrame) -> pd.DataFrame:
    """Return total exposed accounts by year."""

    frame = add_derived_columns(df)
    if "BreachYear" not in frame.columns:
        return pd.DataFrame(columns=["BreachYear", "RecordsExposed"])
    year_records = (
        frame.dropna(subset=["BreachYear"])
        .groupby("BreachYear", as_index=False)["PwnCount"]
        .sum()
        .rename(columns={"PwnCount": "RecordsExposed"})
        .sort_values("BreachYear")
        .reset_index(drop=True)
    )
    return year_records


def get_rolling_average(df: pd.DataFrame, window: int = 3) -> pd.DataFrame:
    """Return a rolling average of exposed accounts by year."""

    yearly = get_yearly_records(df)
    if yearly.empty:
        return yearly.assign(RollingAverage=pd.Series(dtype="float64"))

    yearly["RollingAverage"] = yearly["RecordsExposed"].rolling(window=window, min_periods=1).mean()
    return yearly


def get_yoy_growth(df: pd.DataFrame) -> pd.DataFrame:
    """Return year-over-year growth for records exposed."""

    yearly = get_yearly_records(df)
    if yearly.empty:
        return yearly.assign(YoYGrowth=pd.Series(dtype="float64"))

    yearly["YoYGrowth"] = yearly["RecordsExposed"].pct_change().mul(100)
    return yearly


def get_recent_records(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the most recent breaches."""

    frame = add_derived_columns(df)
    if "BreachDate" not in frame.columns:
        return frame.head(n)
    recent = (
        frame.sort_values(["BreachDate", "PwnCount"], ascending=[False, False])
        .head(n)
        .reset_index(drop=True)
    )
    return recent


def get_filtered_download_name(filters: DashboardFilters) -> str:
    """Build a filename for filtered exports."""

    parts: list[str] = ["breach_data"]
    if filters.search_service:
        parts.append("search")
    if filters.years:
        parts.append("years")
    if filters.domains:
        parts.append("domains")
    if filters.verified_filter != "All":
        parts.append("verified")
    return "_".join(parts) + ".csv"

