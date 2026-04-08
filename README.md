# 🤖 AI Spend Intelligence & Optimization Dashboard

> **SQL · Python · pandas · NumPy · Matplotlib · SQLite · HTML Auto-Generated Dashboard**  
> End-to-end analytics solution tracking AI tool costs, token usage, and efficiency across 8 teams.

---

## 🎯 Problem Statement

Organizations using AI tools (ChatGPT, Copilot, Claude etc.) lack visibility into:
- Which teams and users consume the most AI resources
- Which requests are wasteful or anomalously expensive
- Whether AI spend is delivering real business ROI
- How to optimize tool selection to reduce costs

**This project builds a full analytics pipeline that answers all these questions.**

---

## 📊 Live Dashboard

**[View Live Dashboard →](https://YOUR-USERNAME.github.io/ai-spend-intelligence)**

---

## 🔑 Key Findings

| Metric | Value |
|--------|-------|
| Total AI Spend (2024) | $220.20 |
| Total Requests | 5,000 |
| Active Users | 75 |
| Anomalies Detected | 388 requests |
| Estimated Waste | $142.32 |
| Overall Retry Rate | 8.0% |
| Potential Monthly Saving | ~$21–25 |

---

## 🛠️ Tech Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Data | Python (custom generator) | Realistic synthetic dataset |
| Storage | SQLite + Excel (.xlsx) | Database + spreadsheet |
| Analysis | SQL — 15 queries | Business insights |
| Processing | Python — pandas, NumPy | Cleaning + anomaly detection |
| Charts | Python — Matplotlib | 6 visualizations |
| Dashboard | Python → HTML | Auto-generated report |

---

## 📁 Project Structure

```
ai-spend-intelligence/
│
├── data/
│   ├── ai_usage_logs.csv      ← main table (5,000 rows)
│   ├── users.csv              ← employee directory
│   ├── teams.csv              ← team reference
│   ├── tools.csv              ← AI tools and pricing
│   ├── budgets.csv            ← monthly budgets
│   ├── ai_spend_data.xlsx     ← all tables in one Excel file
│   └── ai_spend.db            ← SQLite database
│
├── sql/
│   └── queries.sql            ← all 15 SQL queries with comments
│
├── python/
│   ├── 01_generate_data.py    ← creates the dataset
│   ├── 02_analysis.py         ← SQL + Python analysis + charts
│   └── 03_generate_dashboard.py ← auto-generates HTML dashboard
│
├── charts/                    ← 6 PNG charts from Matplotlib
│
├── outputs/                   ← CSV result files from SQL queries
│
├── dashboard/
│   └── index.html             ← auto-generated HTML dashboard
│
├── insights/
│   └── business_insights.md  ← key findings + recommendations
│
└── README.md
```

---

## 🚀 How to Run

```bash
# 1. Clone
git clone https://github.com/YOUR-USERNAME/ai-spend-intelligence.git
cd ai-spend-intelligence

# 2. Install libraries
pip install pandas numpy matplotlib openpyxl

# 3. Generate the dataset
python python/01_generate_data.py

# 4. Run analysis (builds DB, runs SQL, creates charts)
python python/02_analysis.py

# 5. Generate the dashboard
python python/03_generate_dashboard.py

# 6. Open dashboard
open dashboard/index.html
```

---

## 📋 SQL Queries (15 Total)

| # | Business Question | SQL Concept |
|---|-------------------|-------------|
| Q1 | Executive KPI summary | SUM, AVG, COUNT |
| Q2 | Which team spends the most? | GROUP BY, ORDER BY |
| Q3 | Which tool costs the most? | Multi-metric aggregation |
| Q4 | How is spend trending monthly? | Time-series grouping |
| Q5 | Which use case has best ROI? | Derived column (quality÷cost) |
| Q6 | Top 15 highest spending users | Ranked aggregation + LIMIT |
| Q7 | Which requests are anomalously expensive? | **CTE + JOIN** |
| Q8 | Are teams within budget? | **CTE + LEFT JOIN + CASE WHEN** |
| Q9 | Which teams waste money on retries? | Conditional aggregation |
| Q10 | What time of day is AI used most? | GROUP BY numeric column |
| Q11 | Which team uses which tool? | Multi-column GROUP BY |
| Q12 | Rank teams by spend | **RANK() OVER window function** |
| Q13 | Month-over-month growth | **LAG() window function** |
| Q14 | Top tool per team | **RANK() OVER PARTITION BY** |
| Q15 | Auto-generate recommendations | **CTE + complex CASE WHEN** |

---

## 🧠 Skills Demonstrated

- ✅ End-to-end data pipeline: generate → clean → SQL → Python → dashboard
- ✅ SQL database design (5-table relational schema with foreign keys)
- ✅ 15 SQL queries — CTEs, window functions (LAG, RANK, PARTITION BY)
- ✅ Python data cleaning with pandas
- ✅ Statistical anomaly detection with NumPy (Z-Score + IQR)
- ✅ 6 data visualizations with Matplotlib
- ✅ Auto-generated HTML dashboard (Python writes the HTML)
- ✅ Excel workbook with 5 sheets
- ✅ Business insight generation from data

---

*Synthetic dataset simulating realistic AI tool usage in a 200-person technology company.*  
*Pricing based on approximate real-world API rates as of 2024.*
