# 📊 task-dashboard.md
# Cyber Breach Analysis Dashboard

## Goal

Create a professional interactive dashboard using **Streamlit**, **Pandas**, and **Plotly** based on the processed dataset inside:

```
data/processed/cleaned_breach_data.csv
```

The dashboard should look modern, clean, responsive, and suitable for a Data Analyst portfolio.

---

# Tech Stack

- Python 3.12+
- Streamlit
- Pandas
- Plotly Express
- Plotly Graph Objects

---

# Project Structure

Create the following structure:

```
dashboard/
│
├── app.py
│
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Trends.py
│   ├── 3_Service_Analysis.py
│   ├── 4_Data_Explorer.py
│   └── 5_Insights.py
│
├── components/
│   ├── loader.py
│   ├── sidebar.py
│   ├── metrics.py
│   └── charts.py
│
├── assets/
│   └── style.css
│
└── utils/
    └── helpers.py
```

---

# General Requirements

- Use Streamlit multipage app.
- Cache data loading using @st.cache_data.
- Organize reusable functions into components.
- Add type hints where appropriate.
- Follow PEP8.
- Keep code modular.
- Add comments only where necessary.
- Handle missing values gracefully.
- Use responsive Plotly charts.

---

# Dashboard Theme

Dark Theme

Background

```
#0D1117
```

Cards

```
#161B22
```

Primary Accent

```
#00E5FF
```

Success

```
#00C853
```

Danger

```
#FF5252
```

---

# Sidebar

Sidebar should include:

- Search Service
- Year Filter
- Domain Filter
- Verified Filter (if available)
- Minimum Records Exposed
- Maximum Records Exposed

All pages must react to sidebar filters.

---

# Page 1
## Overview

Display KPI cards:

- Total Breaches
- Total Services
- Total Domains
- Total Records Exposed
- Earliest Breach
- Latest Breach

Charts:

- Breaches per Year
- Records Exposed per Year
- Top 10 Largest Breaches
- Top Domains

Add a recent data table below.

---

# Page 2
## Trends

Include:

- Line chart
- Area chart
- Rolling Average
- Year-over-Year Growth

Charts should support hover information.

---

# Page 3
## Service Analysis

Create:

Top 20 Services

Horizontal Bar Chart

Service Detail Card

Display:

- Service Name
- Domain
- Breach Date
- Records Exposed
- Description
- Compromised Data

Allow selecting service from dropdown.

---

# Page 4
## Data Explorer

Interactive table

Features:

- Search
- Sort
- Filter
- Download CSV

Show complete processed dataset.

---

# Page 5
## Insights

Generate summary statistics.

Show:

- Biggest breach
- Average records exposed
- Median records
- Most common domain
- Total unique services

Include markdown insight cards explaining findings.

---

# Charts

Use Plotly only.

Include:

- Line Chart
- Bar Chart
- Pie Chart
- Histogram
- Treemap
- Box Plot

Charts must have consistent styling.

---

# Metrics

Format large numbers:

Example

```
1000 -> 1K
1200000 -> 1.2M
```

---

# Performance

- Use caching.
- Avoid recomputing data.
- Optimize dataframe operations.

---

# Error Handling

Display friendly messages when:

- Dataset not found.
- Empty dataframe.
- Invalid filters.

Do not crash the application.

---

# Landing Page

Create an attractive homepage with:

Title

Cyber Breach Analysis Dashboard

Subtitle

Interactive Data Analysis using Streamlit, Pandas and Plotly

Display:

- Project description
- Dataset summary
- Navigation instructions

---

# Extras

If possible implement:

- Download filtered dataset
- Fullscreen charts
- Dark mode styling
- Metric animations
- Loading spinner
- Footer with GitHub link

---

# Dependencies

Update requirements.txt if necessary.

Include:

streamlit
pandas
plotly
numpy

---

# Deliverables

Produce:

- Complete dashboard
- Modular code
- Clean architecture
- Professional UI
- Ready to run with:

```
streamlit run dashboard/app.py
```

No placeholder charts.

All visualizations must use the actual processed dataset.