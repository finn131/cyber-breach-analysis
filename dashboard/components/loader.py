"""Data loading helpers for the dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "cleaned_breach_data.csv"
DATE_COLUMNS = ["BreachDate", "AddedDate", "ModifiedDate"]
BOOLEAN_COLUMNS = [
    "IsVerified",
    "IsFabricated",
    "IsSensitive",
    "IsRetired",
    "IsSpamList",
    "IsMalware",
    "IsSubscriptionFree",
]


def _coerce_boolean(series: pd.Series) -> pd.Series:
    """Normalize boolean-like values into nullable booleans."""

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


@st.cache_data(show_spinner=False)
def load_processed_data(path: str | Path = PROCESSED_DATA_PATH) -> pd.DataFrame:
    """Load and normalize the cleaned breach dataset."""

    data_path = Path(path)
    if not data_path.exists():
        raise FileNotFoundError(
            "Processed dataset not found. Expected file at "
            f"{data_path.as_posix()}."
        )

    df = pd.read_csv(data_path)
    unnamed_columns = [column for column in df.columns if str(column).startswith("Unnamed:")]
    if unnamed_columns:
        df = df.drop(columns=unnamed_columns)

    for column in DATE_COLUMNS:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    for column in BOOLEAN_COLUMNS:
        if column in df.columns:
            df[column] = _coerce_boolean(df[column])

    if "PwnCount" in df.columns:
        df["PwnCount"] = pd.to_numeric(df["PwnCount"], errors="coerce").fillna(0).astype("int64")

    return df

