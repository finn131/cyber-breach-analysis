"""Reusable data loading and cleaning helpers for the breach dataset."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_DATA_PATH = PROJECT_ROOT / "data" / "raw" / "breached_services_info.csv"
PROCESSED_DATA_PATH = (
    PROJECT_ROOT / "data" / "processed" / "cleaned_breach_data.csv"
)

BOOLEAN_COLUMNS = [
    "IsVerified",
    "IsFabricated",
    "IsSensitive",
    "IsRetired",
    "IsSpamList",
    "IsMalware",
    "IsSubscriptionFree",
]

DATE_COLUMNS = ["BreachDate", "AddedDate", "ModifiedDate"]
TEXT_COLUMNS = ["Name", "Title", "Domain", "Description", "LogoPath", "DataClasses"]
NUMERIC_COLUMNS = ["PwnCount"]


def load_data(path: str | Path = RAW_DATA_PATH) -> pd.DataFrame:
    """Load the raw breach dataset from ``path``."""

    return pd.read_csv(path)


def _drop_index_like_column(df: pd.DataFrame) -> pd.DataFrame:
    """Remove the leading CSV index column if it exists."""

    columns_to_drop = [
        column
        for column in df.columns
        if column == "" or str(column).startswith("Unnamed:")
    ]
    if columns_to_drop:
        df = df.drop(columns=columns_to_drop)
    return df


def _standardize_text(series: pd.Series) -> pd.Series:
    """Normalize text by trimming and lowercasing values."""

    return series.astype("string").str.strip().str.lower()


def _coerce_boolean(series: pd.Series) -> pd.Series:
    """Convert common boolean string values to Pandas nullable booleans."""

    normalized = series.astype("string").str.strip().str.lower()
    mapping = {
        "true": True,
        "false": False,
        "1": True,
        "0": False,
        "yes": True,
        "no": False,
    }
    return normalized.map(mapping).astype("boolean")


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the breach dataset and return a normalized copy."""

    cleaned = df.copy()
    cleaned = _drop_index_like_column(cleaned)
    cleaned.columns = [str(column).strip() for column in cleaned.columns]

    for column in TEXT_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = _standardize_text(cleaned[column])

    for column in DATE_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_datetime(cleaned[column], errors="coerce")

    for column in NUMERIC_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = pd.to_numeric(cleaned[column], errors="coerce")

    for column in BOOLEAN_COLUMNS:
        if column in cleaned.columns:
            cleaned[column] = _coerce_boolean(cleaned[column])

    cleaned = cleaned.drop_duplicates().reset_index(drop=True)
    return cleaned


def save_data(df: pd.DataFrame, path: str | Path = PROCESSED_DATA_PATH) -> Path:
    """Save a cleaned dataframe to disk and return the output path."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    return output_path


def main() -> None:
    """Clean the raw CSV and persist the processed dataset."""

    raw_df = load_data()
    cleaned_df = clean_data(raw_df)
    output_path = save_data(cleaned_df)
    print(f"Saved cleaned dataset to {output_path}")
    print(f"Rows: {len(cleaned_df):,}")


if __name__ == "__main__":
    main()
