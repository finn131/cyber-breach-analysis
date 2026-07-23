"""Visualization helpers for the breach dataset."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter, MaxNLocator
import seaborn as sns
import pandas as pd

from scripts.analysis import category_distribution, domain_frequency, top_services, year_distribution


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_IMAGE_DIR = PROJECT_ROOT / "images"

sns.set_theme(style="whitegrid", context="talk")


def _prepare_output_path(output_path: str | Path | None, filename: str) -> Path:
    """Resolve an output path and ensure its parent directory exists."""

    if output_path is None:
        output_path = DEFAULT_IMAGE_DIR / filename

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def plot_top_services(
    df: pd.DataFrame,
    n: int = 10,
    output_path: str | Path | None = None,
) -> Path:
    """Plot the top breached services by impacted accounts."""

    data = top_services(df, n=n, sort_by="pwncount")
    path = _prepare_output_path(output_path, "top_services.png")

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(
        data=data,
        x="pwncount",
        y="Name",
        ax=ax,
        color="#4C78A8",
    )
    ax.set_title("Top Breached Services by Impacted Accounts")
    ax.set_xlabel("Pwned accounts")
    ax.set_ylabel("Service")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))
    for container in ax.containers:
        ax.bar_label(container, labels=[f"{int(v):,}" for v in container.datavalues], padding=4)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_categories(
    df: pd.DataFrame,
    n: int = 15,
    output_path: str | Path | None = None,
) -> Path:
    """Plot the most common breach data classes."""

    data = category_distribution(df, n=n)
    path = _prepare_output_path(output_path, "category_distribution.png")

    fig, ax = plt.subplots(figsize=(12, 8))
    sns.barplot(data=data, x="count", y="category", ax=ax, color="#4472C4")
    ax.set_title("Most Common Data Classes")
    ax.set_xlabel("Occurrences")
    ax.set_ylabel("Data class")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_year_distribution(
    df: pd.DataFrame,
    output_path: str | Path | None = None,
) -> Path:
    """Plot the number of breaches reported per year."""

    data = year_distribution(df)
    path = _prepare_output_path(output_path, "breach_year_distribution.png")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=data, x="year", y="count", marker="o", ax=ax, color="#C55A11")
    ax.set_title("Breaches by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Breach count")
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_top_domains(
    df: pd.DataFrame,
    n: int = 10,
    output_path: str | Path | None = None,
) -> Path:
    """Plot the most common domains in the breach dataset."""

    data = domain_frequency(df, n=n)
    path = _prepare_output_path(output_path, "top_domains.png")

    fig, ax = plt.subplots(figsize=(12, 7))
    sns.barplot(data=data, x="count", y="domain", ax=ax, color="#7A5195")
    ax.set_title("Most Repeated Domains")
    ax.set_xlabel("Occurrences")
    ax.set_ylabel("Domain")
    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f"{x:,.0f}"))
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches="tight")
    plt.close(fig)
    return path


def save_figures(df: pd.DataFrame, output_dir: str | Path = DEFAULT_IMAGE_DIR) -> list[Path]:
    """Create and save the standard project figures."""

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    figures = [
        plot_top_services(df, output_path=output_dir / "top_services.png"),
        plot_categories(df, output_path=output_dir / "category_distribution.png"),
        plot_year_distribution(df, output_path=output_dir / "breach_year_distribution.png"),
        plot_top_domains(df, output_path=output_dir / "top_domains.png"),
    ]
    return figures


def main() -> None:
    """Generate the standard set of project figures."""

    from scripts.analysis import load_clean_data

    df = load_clean_data()
    generated = save_figures(df)
    print("Saved figures:")
    for path in generated:
        print(path)


if __name__ == "__main__":
    main()
