"""
=============================================================
AI SPEND INTELLIGENCE — PYTHON ANALYSIS SCRIPT
=============================================================
What this script does (in simple steps):
  Step 1: Load data from CSV files
  Step 2: Build SQLite database
  Step 3: Run all SQL queries
  Step 4: Clean and validate data (pandas)
  Step 5: Basic calculations (NumPy)
  Step 6: Generate 6 charts (Matplotlib)
  Step 7: Save results to CSV files

Libraries used:
  pandas   → data loading, cleaning, transformations
  numpy    → basic math calculations
  sqlite3  → run SQL queries from Python
  matplotlib → create charts

Note: Kept simple on purpose — every line is easy to explain
=============================================================
"""

import sqlite3
import os
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')           # Non-interactive mode (saves to file)
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import warnings
warnings.filterwarnings('ignore')

# ── PATHS ─────────────────────────────────────────────────
BASE = ".."
DATA = f"{BASE}/data"
CHARTS = f"{BASE}/charts"
OUTPUTS = f"{BASE}/outputs"
DB_PATH = f"{DATA}/ai_spend.db"

# ── CHART STYLE ────────────────────────────────────────────
COLORS = ['#2563EB', '#DC2626', '#16A34A', '#D97706',
          '#7C3AED', '#0891B2', '#BE185D', '#374151']

plt.rcParams.update({
    'figure.dpi':        150,
    'font.family':       'DejaVu Sans',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.titlesize':    13,
    'axes.titleweight':  'bold',
    'axes.labelsize':    11,
    'figure.facecolor':  'white',
})

print("=" * 55)
print("  AI SPEND INTELLIGENCE — PYTHON ANALYSIS")
print("=" * 55)


# ═══════════════════════════════════════════════════════════
# STEP 1 — LOAD DATA FROM CSV FILES
# ═══════════════════════════════════════════════════════════
print("\n[1/7] Loading data from CSV files...")

logs_df    = pd.read_csv(f"{DATA}/ai_usage_logs.csv")
users_df   = pd.read_csv(f"{DATA}/users.csv")
teams_df   = pd.read_csv(f"{DATA}/teams.csv")
tools_df   = pd.read_csv(f"{DATA}/tools.csv")
budgets_df = pd.read_csv(f"{DATA}/budgets.csv")

print(f"  ✅ ai_usage_logs : {len(logs_df):,} records")
print(f"  ✅ users         : {len(users_df)} employees")
print(f"  ✅ teams         : {len(teams_df)} departments")
print(f"  ✅ tools         : {len(tools_df)} AI tools")
print(f"  ✅ budgets       : {len(budgets_df)} rows")


# ═══════════════════════════════════════════════════════════
# STEP 2 — DATA CLEANING (Pandas)
# ═══════════════════════════════════════════════════════════
print("\n[2/7] Cleaning and validating data...")

# Check for missing values
missing = logs_df.isnull().sum().sum()
print(f"  Missing values found : {missing}")

# Convert date column to proper datetime type
logs_df['date'] = pd.to_datetime(logs_df['date'])

# Make sure numeric columns have correct types
logs_df['cost_usd']      = logs_df['cost_usd'].astype(float)
logs_df['total_tokens']  = logs_df['total_tokens'].astype(int)
logs_df['quality_score'] = logs_df['quality_score'].astype(int)
logs_df['is_retry']      = logs_df['is_retry'].astype(int)
logs_df['is_anomaly']    = logs_df['is_anomaly'].astype(int)

# Flag negative costs as data quality issue (there should be none)
neg_cost = (logs_df['cost_usd'] < 0).sum()
print(f"  Negative cost records: {neg_cost}")

# Remove duplicates (if any)
before = len(logs_df)
logs_df = logs_df.drop_duplicates(subset='log_id')
after = len(logs_df)
print(f"  Duplicates removed   : {before - after}")

print(f"  ✅ Data is clean. {len(logs_df):,} records ready.")


# ═══════════════════════════════════════════════════════════
# STEP 3 — BUILD SQLITE DATABASE
# ═══════════════════════════════════════════════════════════
print("\n[3/7] Building SQLite database...")

conn = sqlite3.connect(DB_PATH)

# Write all tables to the database
logs_df.to_sql('ai_usage_logs', conn, if_exists='replace', index=False)
users_df.to_sql('users',        conn, if_exists='replace', index=False)
teams_df.to_sql('teams',        conn, if_exists='replace', index=False)
tools_df.to_sql('tools',        conn, if_exists='replace', index=False)
budgets_df.to_sql('budgets',    conn, if_exists='replace', index=False)
conn.commit()

print(f"  ✅ Database created: ai_spend.db")
print(f"  ✅ 5 tables loaded into SQLite")


# ═══════════════════════════════════════════════════════════
# STEP 4 — RUN SQL QUERIES (sqlite3 + pandas)
# ═══════════════════════════════════════════════════════════
print("\n[4/7] Running SQL queries...")

def run_sql(sql):
    """Helper function: run SQL, return result as DataFrame."""
    return pd.read_sql_query(sql, conn)

# KPI Summary (Query 1)
kpi = run_sql("""
    SELECT
        COUNT(*)                                    AS total_requests,
        COUNT(DISTINCT user_id)                     AS active_users,
        ROUND(SUM(cost_usd), 2)                     AS total_spend_usd,
        ROUND(AVG(cost_usd), 4)                     AS avg_cost_per_request,
        ROUND(SUM(total_tokens) / 1000000.0, 2)     AS total_tokens_millions,
        ROUND(AVG(quality_score), 2)                AS avg_quality_score,
        SUM(is_anomaly)                             AS anomalous_requests,
        ROUND(100.0 * SUM(is_retry) / COUNT(*), 1) AS retry_rate_pct
    FROM ai_usage_logs
""").iloc[0]

# Spend by Team (Query 2)
team_spend = run_sql("""
    SELECT team,
           COUNT(*) AS requests,
           ROUND(SUM(cost_usd), 2) AS spend_usd,
           ROUND(AVG(quality_score), 2) AS avg_quality,
           ROUND(100.0 * SUM(is_retry) / COUNT(*), 1) AS retry_pct,
           ROUND(SUM(cost_usd) / COUNT(DISTINCT user_id), 2) AS spend_per_user
    FROM ai_usage_logs
    GROUP BY team
    ORDER BY spend_usd DESC
""")

# Spend by Tool (Query 3)
tool_spend = run_sql("""
    SELECT tool,
           COUNT(*) AS requests,
           ROUND(SUM(cost_usd), 2) AS spend_usd,
           ROUND(AVG(quality_score), 2) AS avg_quality
    FROM ai_usage_logs
    GROUP BY tool
    ORDER BY spend_usd DESC
""")

# Monthly Trend (Query 4)
monthly = run_sql("""
    SELECT month,
           COUNT(*) AS requests,
           COUNT(DISTINCT user_id) AS active_users,
           ROUND(SUM(cost_usd), 2) AS spend_usd,
           SUM(is_anomaly) AS anomalies
    FROM ai_usage_logs
    GROUP BY month
    ORDER BY month
""")

# Use Case Analysis (Query 5)
use_case = run_sql("""
    SELECT use_case,
           COUNT(*) AS requests,
           ROUND(SUM(cost_usd), 2) AS spend_usd,
           ROUND(AVG(quality_score), 2) AS avg_quality,
           ROUND(100.0 * SUM(is_retry) / COUNT(*), 1) AS retry_pct
    FROM ai_usage_logs
    GROUP BY use_case
    ORDER BY spend_usd DESC
""")

# Hourly Pattern (Query 10)
hourly = run_sql("""
    SELECT hour,
           COUNT(*) AS requests,
           ROUND(SUM(cost_usd), 2) AS spend_usd
    FROM ai_usage_logs
    GROUP BY hour
    ORDER BY hour
""")

# Budget vs Actual (from Query 8)
budget_vs_actual = run_sql("""
    WITH actual AS (
        SELECT team, month, ROUND(SUM(cost_usd), 2) AS actual_spend
        FROM ai_usage_logs
        GROUP BY team, month
    )
    SELECT b.team, b.month, b.budget_usd,
           COALESCE(a.actual_spend, 0) AS actual_spend,
           ROUND(100.0 * COALESCE(a.actual_spend, 0) / b.budget_usd, 1) AS pct_used
    FROM budgets b
    LEFT JOIN actual a ON b.team = a.team AND b.month = a.month
    ORDER BY b.month, actual_spend DESC
""")

# Recommendations (Query 15)
recommendations = run_sql("""
    WITH stats AS (
        SELECT team,
               ROUND(SUM(cost_usd), 2) AS total_spend,
               ROUND(AVG(quality_score), 2) AS avg_quality,
               ROUND(100.0 * SUM(is_retry) / COUNT(*), 1) AS retry_rate,
               SUM(is_anomaly) AS anomalies,
               ROUND(SUM(cost_usd) / COUNT(DISTINCT user_id), 2) AS cost_per_user
        FROM ai_usage_logs GROUP BY team
    )
    SELECT team, total_spend, avg_quality, retry_rate, anomalies, cost_per_user,
           CASE
               WHEN retry_rate > 12 THEN 'Run prompt engineering training'
               WHEN anomalies > 30  THEN 'Set token limits per request'
               WHEN avg_quality < 3.2 THEN 'Review tool selection'
               ELSE 'Monitor monthly — usage is healthy'
           END AS recommendation
    FROM stats ORDER BY total_spend DESC
""")

print(f"  ✅ All SQL queries executed")


# ═══════════════════════════════════════════════════════════
# STEP 5 — NUMPY CALCULATIONS
# ═══════════════════════════════════════════════════════════
print("\n[5/7] Running NumPy calculations...")

costs = logs_df['cost_usd'].values

# Basic statistics
cost_mean   = np.mean(costs)
cost_median = np.median(costs)
cost_std    = np.std(costs)

# Anomaly detection using Z-Score
# Z-Score tells how many standard deviations a value is from the mean
# Rule: if Z-score > 3, the request is unusually expensive
z_scores         = np.abs((costs - cost_mean) / (cost_std + 1e-9))
anomaly_flag_z   = (z_scores > 3).astype(int)

# IQR method (Interquartile Range)
# IQR = Q3 - Q1 (middle 50% of data)
# Anything above Q3 + 3*IQR is an outlier
q1, q3  = np.percentile(costs, 25), np.percentile(costs, 75)
iqr     = q3 - q1
iqr_hi  = q3 + 3 * iqr
anomaly_flag_iqr = (costs > iqr_hi).astype(int)

# Combine both methods
logs_df['anomaly_detected'] = np.maximum(anomaly_flag_z, anomaly_flag_iqr)
detected_count   = logs_df['anomaly_detected'].sum()
detected_waste   = logs_df[logs_df['anomaly_detected'] == 1]['cost_usd'].sum()

print(f"  Cost mean      : ${cost_mean:.4f}")
print(f"  Cost median    : ${cost_median:.4f}")
print(f"  Cost std dev   : ${cost_std:.4f}")
print(f"  Z-Score threshold (3σ) : ${cost_mean + 3*cost_std:.4f}")
print(f"  IQR threshold  : ${iqr_hi:.4f}")
print(f"  Anomalies found: {detected_count} requests")
print(f"  Estimated waste: ${detected_waste:.2f}")


# ═══════════════════════════════════════════════════════════
# STEP 6 — GENERATE CHARTS (Matplotlib)
# ═══════════════════════════════════════════════════════════
print("\n[6/7] Generating charts...")


# ── Chart 1: Monthly Spend Trend ──────────────────────────
fig, ax1 = plt.subplots(figsize=(13, 5))
ax2 = ax1.twinx()   # Second Y-axis for requests

months_lbl = [m[-2:] + "/" + m[2:4] for m in monthly['month']]

ax1.fill_between(range(len(monthly)), monthly['spend_usd'],
                 alpha=0.15, color=COLORS[0])
ax1.plot(range(len(monthly)), monthly['spend_usd'],
         'o-', color=COLORS[0], linewidth=2.5, markersize=7,
         label='Monthly Spend ($)')
ax2.plot(range(len(monthly)), monthly['requests'],
         's--', color=COLORS[1], linewidth=1.8, markersize=6,
         label='Requests')

ax1.set_xticks(range(len(monthly)))
ax1.set_xticklabels(months_lbl, rotation=45, ha='right')
ax1.set_ylabel('Total Spend (USD)', color=COLORS[0])
ax2.set_ylabel('Number of Requests', color=COLORS[1])
ax1.set_title('Monthly AI Spend & Request Volume — Jan to Dec 2024')

# Add value labels on top of each bar
for i, v in enumerate(monthly['spend_usd']):
    ax1.text(i, v + 0.2, f'${v:.1f}', ha='center', fontsize=8, color=COLORS[0])

lines1, lbl1 = ax1.get_legend_handles_labels()
lines2, lbl2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, lbl1 + lbl2, loc='upper left')
plt.tight_layout()
plt.savefig(f'{CHARTS}/01_monthly_trend.png', bbox_inches='tight')
plt.close()
print("  ✅ 01_monthly_trend.png")


# ── Chart 2: Spend by Team (Horizontal Bar) ───────────────
fig, ax = plt.subplots(figsize=(11, 6))
bars = ax.barh(
    team_spend['team'][::-1],
    team_spend['spend_usd'][::-1],
    color=COLORS[:len(team_spend)][::-1],
    edgecolor='white', height=0.6
)
ax.set_xlabel('Total AI Spend (USD)')
ax.set_title('Total AI Spend by Team — Full Year 2024')
for bar, val in zip(bars, team_spend['spend_usd'][::-1]):
    ax.text(val + 0.2, bar.get_y() + bar.get_height() / 2,
            f'${val:.2f}', va='center', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig(f'{CHARTS}/02_team_spend.png', bbox_inches='tight')
plt.close()
print("  ✅ 02_team_spend.png")


# ── Chart 3: Spend by Tool (Pie Chart) ────────────────────
fig, ax = plt.subplots(figsize=(9, 7))
wedges, texts, autotexts = ax.pie(
    tool_spend['spend_usd'],
    labels=tool_spend['tool'],
    autopct='%1.1f%%',
    colors=COLORS[:len(tool_spend)],
    startangle=140,
    wedgeprops={'edgecolor': 'white', 'linewidth': 2},
)
ax.set_title('AI Spend Share by Tool')
plt.tight_layout()
plt.savefig(f'{CHARTS}/03_tool_spend.png', bbox_inches='tight')
plt.close()
print("  ✅ 03_tool_spend.png")


# ── Chart 4: Quality Score vs Retry Rate by Team ──────────
fig, ax = plt.subplots(figsize=(11, 7))
for i, row in team_spend.iterrows():
    ax.scatter(
        row['retry_pct'], row['avg_quality'],
        s=row['spend_usd'] * 40 + 100,
        color=COLORS[i % len(COLORS)],
        alpha=0.75, edgecolors='white', linewidth=1.5
    )
    ax.annotate(
        row['team'],
        (row['retry_pct'], row['avg_quality']),
        textcoords='offset points', xytext=(8, 4), fontsize=9
    )

# Draw average lines
ax.axhline(y=team_spend['avg_quality'].mean(), color='gray',
           linestyle='--', linewidth=1, alpha=0.6, label='Avg Quality')
ax.axvline(x=team_spend['retry_pct'].mean(), color=COLORS[1],
           linestyle='--', linewidth=1, alpha=0.6, label='Avg Retry Rate')
ax.set_xlabel('Retry Rate (%) — Higher means more wasted spend')
ax.set_ylabel('Avg Quality Score (1–5)')
ax.set_title('Team Efficiency: Quality Score vs Retry Rate\n(Bubble size = Total Spend)')
ax.legend()
plt.tight_layout()
plt.savefig(f'{CHARTS}/04_quality_vs_retry.png', bbox_inches='tight')
plt.close()
print("  ✅ 04_quality_vs_retry.png")


# ── Chart 5: Hourly Usage Pattern ─────────────────────────
fig, ax = plt.subplots(figsize=(13, 5))
peak_hours = [9, 10, 11, 14, 15, 16]
bar_colors = [COLORS[1] if h in peak_hours else COLORS[0]
              for h in hourly['hour']]
ax.bar(hourly['hour'], hourly['requests'],
       color=bar_colors, edgecolor='white', width=0.7)
ax.set_xlabel('Hour of Day (24-hour format)')
ax.set_ylabel('Number of AI Requests')
ax.set_title('AI Usage by Hour of Day — Peak Hours Highlighted in Red')
ax.set_xticks(hourly['hour'])

# Custom legend
normal_patch = mpatches.Patch(color=COLORS[0], label='Normal hours')
peak_patch   = mpatches.Patch(color=COLORS[1], label='Peak hours (9–11am, 2–4pm)')
ax.legend(handles=[normal_patch, peak_patch])
plt.tight_layout()
plt.savefig(f'{CHARTS}/05_hourly_pattern.png', bbox_inches='tight')
plt.close()
print("  ✅ 05_hourly_pattern.png")


# ── Chart 6: Anomaly Cost Distribution ────────────────────
fig, ax = plt.subplots(figsize=(11, 5))
normal_costs  = logs_df[logs_df['anomaly_detected'] == 0]['cost_usd']
anomaly_costs = logs_df[logs_df['anomaly_detected'] == 1]['cost_usd']

ax.hist(normal_costs,  bins=50, alpha=0.65, color=COLORS[0],
        label=f'Normal Requests ({len(normal_costs):,})',  density=True)
ax.hist(anomaly_costs, bins=20, alpha=0.75, color=COLORS[1],
        label=f'Anomalous Requests ({len(anomaly_costs):,})', density=True)

ax.set_xlabel('Cost per Request (USD)')
ax.set_ylabel('Density')
ax.set_title('Cost Distribution — Normal vs Anomalous Requests')
ax.legend()
ax.set_xlim(left=0)
plt.tight_layout()
plt.savefig(f'{CHARTS}/06_anomaly_distribution.png', bbox_inches='tight')
plt.close()
print("  ✅ 06_anomaly_distribution.png")


# ═══════════════════════════════════════════════════════════
# STEP 7 — SAVE OUTPUT FILES
# ═══════════════════════════════════════════════════════════
print("\n[7/7] Saving output files...")

team_spend.to_csv(f"{OUTPUTS}/team_spend.csv",         index=False)
tool_spend.to_csv(f"{OUTPUTS}/tool_spend.csv",         index=False)
monthly.to_csv(f"{OUTPUTS}/monthly_trend.csv",         index=False)
use_case.to_csv(f"{OUTPUTS}/use_case_analysis.csv",    index=False)
recommendations.to_csv(f"{OUTPUTS}/recommendations.csv", index=False)
logs_df.to_csv(f"{OUTPUTS}/logs_with_anomaly_flags.csv", index=False)

print("  ✅ All output files saved to outputs/")


# ── Print Final Summary ────────────────────────────────────
top_team    = team_spend.iloc[0]
top_tool    = tool_spend.iloc[0]
worst_retry = team_spend.sort_values('retry_pct', ascending=False).iloc[0]
peak_month  = monthly.sort_values('spend_usd', ascending=False).iloc[0]

print("\n" + "=" * 55)
print("  ANALYSIS COMPLETE — KEY FINDINGS")
print("=" * 55)
print(f"  Total Spend       : ${kpi['total_spend_usd']:,.2f}")
print(f"  Total Requests    : {kpi['total_requests']:,.0f}")
print(f"  Active Users      : {kpi['active_users']:.0f}")
print(f"  Avg Quality       : {kpi['avg_quality_score']:.2f}/5")
print(f"  Retry Rate        : {kpi['retry_rate_pct']:.1f}%")
print(f"  Anomalies Found   : {detected_count} (${detected_waste:.2f} waste)")
print(f"  Top Spending Team : {top_team['team']} (${top_team['spend_usd']:.2f})")
print(f"  Top Tool          : {top_tool['tool']} (${top_tool['spend_usd']:.2f})")
print(f"  Peak Month        : {peak_month['month']} (${peak_month['spend_usd']:.2f})")
print(f"  Highest Retry     : {worst_retry['team']} ({worst_retry['retry_pct']:.1f}%)")
print("=" * 55)

# Save global variables for dashboard use
GLOBAL_KPI = {
    "total_spend":   kpi['total_spend_usd'],
    "total_requests": int(kpi['total_requests']),
    "active_users":  int(kpi['active_users']),
    "avg_quality":   kpi['avg_quality_score'],
    "retry_rate":    kpi['retry_rate_pct'],
    "anomalies":     detected_count,
    "waste":         round(detected_waste, 2),
    "top_team":      top_team['team'],
    "top_tool":      top_tool['tool'],
    "peak_month":    peak_month['month'],
}

conn.close()
print("\n  ✅ Python analysis complete. Ready for dashboard.")
