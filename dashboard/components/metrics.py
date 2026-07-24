"""Metric card rendering helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

import pandas as pd
import streamlit as st

from dashboard.utils.helpers import compact_number, format_date


@dataclass(slots=True)
class MetricCard:
    """Data for a single metric card."""

    label: str
    value: object
    subtitle: str | None = None
    accent: str = "#00E5FF"


def _render_card(card: MetricCard) -> None:
    value_text = format_date(card.value) if isinstance(card.value, (pd.Timestamp,)) else compact_number(card.value)
    if isinstance(card.value, str) and not card.value.isdigit():
        value_text = card.value

    subtitle_html = f"<div class='metric-subtitle'>{card.subtitle}</div>" if card.subtitle else ""
    st.markdown(
        f"""
        <div class="metric-card" style="--accent:{card.accent}">
            <div class="metric-accent"></div>
            <div class="metric-label">{card.label}</div>
            <div class="metric-value">{value_text}</div>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric_cards(cards: Sequence[MetricCard]) -> None:
    """Render metrics in a responsive row."""

    if not cards:
        return

    columns = st.columns(len(cards))
    for column, card in zip(columns, cards, strict=False):
        with column:
            _render_card(card)
