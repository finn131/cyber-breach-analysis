# Cyber Breach Analysis Project Instructions

## Project Overview

This project aims to perform Exploratory Data Analysis (EDA) on cybersecurity breach datasets using Python and Pandas.

Dataset location:

```text
data/raw/breached_services_info.csv
```

The objective is to understand trends, patterns, and insights related to cyber breach incidents.

---

# Tech Stack

* Python 3.12+
* Pandas
* NumPy
* Matplotlib
* Seaborn
* Jupyter Notebook

---

# Project Tasks

## Notebook 01 - Data Understanding

File:

```text
notebooks/01_data_understanding.ipynb
```

Tasks:

1. Load dataset from:

```python
data/raw/breached_services_info.csv
```

2. Display:

* `head()`
* `tail()`
* `sample()`
* `shape`
* `columns`
* `dtypes`
* `info()`
* `describe()`

3. Investigate:

* Missing values
* Duplicate rows
* Unique values per column

4. Write a short summary of findings.

---

## Notebook 02 - Data Cleaning

File:

```text
notebooks/02_data_cleaning.ipynb
```

Tasks:

1. Handle missing values.

2. Remove duplicate records.

3. Convert columns to appropriate data types.

4. Standardize text values:

* lowercase
* trim whitespace

5. Save cleaned dataset to:

```text
data/processed/cleaned_breach_data.csv
```

---

## Notebook 03 - Exploratory Analysis

File:

```text
notebooks/03_exploratory_analysis.ipynb
```

Perform analysis such as:

### General Statistics

* Number of records
* Number of unique services
* Most common categories

### Analysis Questions

1. Which services appear most frequently?

2. Which categories dominate the dataset?

3. What are the top breached platforms?

4. Are there any patterns in service naming?

5. Distribution of records by category.

6. Additional insights discovered during exploration.

Use:

* groupby
* value_counts
* agg
* pivot_table

---

## Notebook 04 - Visualization

File:

```text
notebooks/04_visualization.ipynb
```

Create visualizations:

1. Top 10 breached services.
2. Category distribution.
3. Frequency distributions.
4. Additional useful charts.

Save figures into:

```text
images/
```

Example:

```python
plt.savefig(
    "images/top_services.png",
    dpi=300,
    bbox_inches="tight"
)
```

---

# Scripts

## cleaning.py

Create reusable functions:

* load_data()
* clean_data()
* save_data()

---

## analysis.py

Create functions:

* top_services()
* category_distribution()
* summary_statistics()

---

## visualization.py

Create functions:

* plot_top_services()
* plot_categories()
* save_figures()

---

# Reports

## reports/findings.md

Generate a report containing:

* Key insights
* Important statistics
* Interesting findings
* Recommendations

---

## reports/executive_summary.md

Create a concise summary explaining:

1. Project objectives.
2. Dataset overview.
3. Main findings.
4. Future improvements.

---

# README Improvements

Update README.md with:

* Project description
* Dataset information
* Folder structure
* Installation guide
* Usage instructions
* Visualizations
* Key findings
* Future work

---

# Coding Requirements

* Write clean and readable code.
* Add comments where necessary.
* Use type hints when possible.
* Follow PEP8 conventions.
* Prefer reusable functions over repetitive code.

---

# Final Goal

Produce a portfolio-quality cybersecurity data analysis project demonstrating:

* Python
* Pandas
* Data Cleaning
* Exploratory Data Analysis
* Data Visualization
* Cybersecurity Domain Knowledge
