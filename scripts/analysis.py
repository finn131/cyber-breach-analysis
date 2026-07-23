"""Exploratory analysis helpers for the breach dataset."""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from scripts.cleaning import clean_data, load_data


def _parse_list_like(value: Any) -> list[str]:
    """Parse list-like text stored in the dataset into individual entries."""

    if pd.isna(value):
        return []

    text = str(value).strip()
    if not text:
        return []

    items = []
    for raw_item in text.strip("[]").split(","):
        item = raw_item.strip().strip("'").strip('"').strip()
        if item:
            items.append(item)
    return items


def load_clean_data(path: str | Path | None = None) -> pd.DataFrame:
    """Convenience helper that loads and cleans the dataset."""

    raw_df = load_data(path) if path is not None else load_data()
    return clean_data(raw_df)


def top_services(
    df: pd.DataFrame,
    n: int = 10,
    sort_by: str = "pwncount",
) -> pd.DataFrame:
    """Return the top services by count or breached accounts."""

    frame = df.copy()
    if sort_by == "count":
        result = (
            frame["Name"]
            .value_counts()
            .rename_axis("service")
            .reset_index(name="count")
            .head(n)
        )
        return result

    if "PwnCount" not in frame.columns:
        raise KeyError("PwnCount column is required for pwncount ranking.")

    result = (
        frame.assign(pwncount=frame["PwnCount"].fillna(0).astype("int64"))
        .sort_values(["pwncount", "Name"], ascending=[False, True])
        .loc[:, ["Name", "Title", "Domain", "pwncount"]]
        .head(n)
        .reset_index(drop=True)
    )
    return result


def category_distribution(df: pd.DataFrame, n: int = 15) -> pd.DataFrame:
    """Count the most common data classes across the breach records."""

    if "DataClasses" not in df.columns:
        raise KeyError("DataClasses column is required for category analysis.")

    exploded = (
        df.loc[:, ["DataClasses"]]
        .assign(category=lambda frame: frame["DataClasses"].apply(_parse_list_like))
        .explode("category")
    )
    distribution = (
        exploded["category"]
        .dropna()
        .value_counts()
        .rename_axis("category")
        .reset_index(name="count")
        .head(n)
    )
    return distribution


def summary_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """Return a compact summary of the breach dataset."""

    frame = df.copy()
    stats: dict[str, Any] = {
        "records": int(len(frame)),
        "unique_services": int(frame["Name"].nunique()) if "Name" in frame else None,
        "unique_domains": int(frame["Domain"].nunique()) if "Domain" in frame else None,
        "duplicate_rows": int(frame.duplicated().sum()),
        "missing_domains": int(frame["Domain"].isna().sum()) if "Domain" in frame else None,
        "verified_records": int(frame["IsVerified"].sum()) if "IsVerified" in frame else None,
        "unverified_records": int((~frame["IsVerified"]).sum())
        if "IsVerified" in frame
        else None,
        "sensitive_records": int(frame["IsSensitive"].sum())
        if "IsSensitive" in frame
        else None,
        "retired_records": int(frame["IsRetired"].sum()) if "IsRetired" in frame else None,
        "spam_list_records": int(frame["IsSpamList"].sum())
        if "IsSpamList" in frame
        else None,
        "malware_records": int(frame["IsMalware"].sum()) if "IsMalware" in frame else None,
        "subscription_free_records": int(frame["IsSubscriptionFree"].sum())
        if "IsSubscriptionFree" in frame
        else None,
        "total_pwned_accounts": int(frame["PwnCount"].sum())
        if "PwnCount" in frame
        else None,
        "median_pwned_accounts": float(frame["PwnCount"].median())
        if "PwnCount" in frame
        else None,
        "max_pwned_accounts": int(frame["PwnCount"].max()) if "PwnCount" in frame else None,
    }

    if "BreachDate" in frame:
        breach_year = frame["BreachDate"].dt.year.value_counts().sort_values(ascending=False)
        stats["top_breach_year"] = int(breach_year.index[0]) if not breach_year.empty else None
        stats["top_breach_year_count"] = int(breach_year.iloc[0]) if not breach_year.empty else None

    if "DataClasses" in frame:
        category_counts = category_distribution(frame, n=1)
        if not category_counts.empty:
            stats["top_data_class"] = str(category_counts.iloc[0]["category"])
            stats["top_data_class_count"] = int(category_counts.iloc[0]["count"])

    if "Domain" in frame:
        domain_counts = (
            frame["Domain"].dropna().replace("", pd.NA).dropna().value_counts()
        )
        if not domain_counts.empty:
            stats["top_domain"] = str(domain_counts.index[0])
            stats["top_domain_count"] = int(domain_counts.iloc[0])

    return stats


def service_frequency(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the most common service names in the dataset."""

    return (
        df["Name"]
        .value_counts()
        .rename_axis("service")
        .reset_index(name="count")
        .head(n)
    )


def domain_frequency(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return the most common domains in the dataset."""

    return (
        df["Domain"]
        .replace("", pd.NA)
        .dropna()
        .value_counts()
        .rename_axis("domain")
        .reset_index(name="count")
        .head(n)
    )


def year_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Return breach counts grouped by year."""

    if "BreachDate" not in df.columns:
        raise KeyError("BreachDate column is required for year distribution.")

    year_counts = (
        df.assign(year=df["BreachDate"].dt.year)
        .groupby("year", dropna=False)
        .size()
        .reset_index(name="count")
        .sort_values("year")
        .reset_index(drop=True)
    )
    return year_counts


def naming_patterns(df: pd.DataFrame) -> dict[str, int]:
    """Summarize simple service-name patterns."""

    names = df["Name"].astype(str)
    return {
        "contains_digit": int(names.str.contains(r"\d", regex=True).sum()),
        "all_alpha": int(names.str.match(r"^[A-Za-z]+$", na=False).sum()),
        "short_name_le_5": int(names.str.len().le(5).sum()),
        "title_equals_name": int((df["Title"].astype(str) == names).sum())
        if "Title" in df.columns
        else None,
    }


def main() -> None:
    """Print a compact analysis summary for the cleaned dataset."""

    df = load_clean_data()
    stats = summary_statistics(df)
    print("Summary statistics")
    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\nTop services by pwncount")
    print(top_services(df, n=10, sort_by="pwncount").to_string(index=False))

    print("\nTop categories")
    print(category_distribution(df, n=10).to_string(index=False))


if __name__ == "__main__":
    main()
