"""
=============================================================
AI SPEND INTELLIGENCE — DATASET GENERATOR
=============================================================
What this script does:
  Creates realistic synthetic data that simulates how a
  mid-size company (200 employees) uses AI tools.
  
  Think of it like: every time someone at the company sends
  a prompt to ChatGPT or Copilot, it gets logged here.

Output files:
  1. ai_usage_logs.csv   → main table (5,000 rows)
  2. users.csv           → employee directory (80 rows)
  3. teams.csv           → department info (8 rows)
  4. tools.csv           → AI tools and pricing (6 rows)
  5. budgets.csv         → monthly budget per team (96 rows)

Also saves everything to:
  6. ai_spend_data.xlsx  → Excel file (all sheets)
=============================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import os

# Fix random seed so results are same every run
np.random.seed(42)
random.seed(42)

# ── PATHS ─────────────────────────────────────────────────
OUT = "../data"

# ═══════════════════════════════════════════════════════════
# REFERENCE DATA — The building blocks
# ═══════════════════════════════════════════════════════════

TEAMS = [
    "Engineering",
    "Data & Analytics",
    "Marketing",
    "Finance",
    "HR",
    "Product",
    "Customer Support",
    "Legal"
]

# AI tools with real-world approximate pricing per 1000 tokens
TOOLS_DATA = {
    "ChatGPT-4":        {"cost_per_1k_input": 0.030, "cost_per_1k_output": 0.060},
    "ChatGPT-3.5":      {"cost_per_1k_input": 0.002, "cost_per_1k_output": 0.002},
    "Claude-3-Sonnet":  {"cost_per_1k_input": 0.003, "cost_per_1k_output": 0.015},
    "GitHub-Copilot":   {"cost_per_1k_input": 0.000, "cost_per_1k_output": 0.000},  # flat subscription
    "Gemini-Pro":       {"cost_per_1k_input": 0.001, "cost_per_1k_output": 0.001},
    "Perplexity":       {"cost_per_1k_input": 0.001, "cost_per_1k_output": 0.001},
}

USE_CASES = [
    "Code Generation",
    "Data Analysis",
    "Content Writing",
    "Email Drafting",
    "Report Summarization",
    "Bug Fixing",
    "Research",
    "Customer Query",
    "Documentation",
    "Image Generation"
]

# Which tools each team uses most
# (weights for random selection — higher = more likely)
TEAM_TOOL_MAP = {
    "Engineering":      ["ChatGPT-4", "GitHub-Copilot", "ChatGPT-3.5"],
    "Data & Analytics": ["ChatGPT-4", "Claude-3-Sonnet", "Gemini-Pro"],
    "Marketing":        ["ChatGPT-3.5", "ChatGPT-4", "Perplexity"],
    "Finance":          ["ChatGPT-3.5", "Claude-3-Sonnet", "Perplexity"],
    "HR":               ["ChatGPT-3.5", "Perplexity", "ChatGPT-4"],
    "Product":          ["ChatGPT-4", "Claude-3-Sonnet", "Gemini-Pro"],
    "Customer Support": ["ChatGPT-3.5", "Gemini-Pro", "Perplexity"],
    "Legal":            ["Claude-3-Sonnet", "ChatGPT-4", "Perplexity"],
}

# Which use cases each team does most
TEAM_USECASE_MAP = {
    "Engineering":      ["Code Generation", "Bug Fixing", "Documentation"],
    "Data & Analytics": ["Data Analysis", "Report Summarization", "Research"],
    "Marketing":        ["Content Writing", "Email Drafting", "Research"],
    "Finance":          ["Report Summarization", "Data Analysis", "Email Drafting"],
    "HR":               ["Email Drafting", "Documentation", "Research"],
    "Product":          ["Research", "Documentation", "Content Writing"],
    "Customer Support": ["Customer Query", "Email Drafting", "Documentation"],
    "Legal":            ["Report Summarization", "Research", "Documentation"],
}

# Monthly budget per team (USD)
TEAM_BUDGETS = {
    "Engineering":      800,
    "Data & Analytics": 600,
    "Marketing":        500,
    "Finance":          400,
    "HR":               300,
    "Product":          500,
    "Customer Support": 350,
    "Legal":            250,
}


# ═══════════════════════════════════════════════════════════
# STEP 1 — Create reference tables
# ═══════════════════════════════════════════════════════════

def make_teams():
    """Create teams reference table."""
    rows = []
    for i, team in enumerate(TEAMS, start=1):
        rows.append({
            "team_id":      f"T{i:02d}",
            "team_name":    team,
            "monthly_budget_usd": TEAM_BUDGETS[team],
            "head_count":   random.randint(10, 40),
        })
    return pd.DataFrame(rows)


def make_tools():
    """Create AI tools reference table."""
    rows = []
    for i, (tool, pricing) in enumerate(TOOLS_DATA.items(), start=1):
        rows.append({
            "tool_id":              f"TL{i:02d}",
            "tool_name":            tool,
            "cost_per_1k_input":    pricing["cost_per_1k_input"],
            "cost_per_1k_output":   pricing["cost_per_1k_output"],
            "pricing_model": "subscription" if tool == "GitHub-Copilot" else "token-based",
        })
    return pd.DataFrame(rows)


def make_users(teams_df, n=80):
    """Create user/employee table."""
    rows = []
    uid = 1001

    for _, team_row in teams_df.iterrows():
        team = team_row["team_name"]
        # Spread users across teams proportionally
        n_users = max(5, int(n * team_row["head_count"] / teams_df["head_count"].sum()))

        for _ in range(n_users):
            rows.append({
                "user_id":   f"U{uid}",
                "user_name": f"Employee_{uid}",
                "team":      team,
                "team_id":   team_row["team_id"],
                "role":      random.choice(["Junior Analyst", "Senior Analyst", "Manager", "Lead"]),
                "join_date": (
                    datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1460))
                ).strftime("%Y-%m-%d"),
            })
            uid += 1

    df = pd.DataFrame(rows)
    return df.head(n)  # cap at exactly n users


def make_budgets():
    """Monthly budget table for all 12 months."""
    rows = []
    for team in TEAMS:
        for month_num in range(1, 13):
            month_str = f"2024-{month_num:02d}"
            rows.append({
                "team":          team,
                "month":         month_str,
                "budget_usd":    TEAM_BUDGETS[team],
            })
    return pd.DataFrame(rows)


# ═══════════════════════════════════════════════════════════
# STEP 2 — Create the main usage log table
# ═══════════════════════════════════════════════════════════

def calculate_cost(tool, input_tokens, output_tokens):
    """
    Calculate cost of a single AI request.
    
    Simple formula:
    cost = (input_tokens / 1000 * price_per_1k_input)
         + (output_tokens / 1000 * price_per_1k_output)
    
    GitHub Copilot is subscription-based → flat $0.20/day allocation
    """
    pricing = TOOLS_DATA[tool]

    if tool == "GitHub-Copilot":
        # Flat daily subscription cost per user
        return round(random.uniform(0.15, 0.25), 4)

    cost = (
        (input_tokens / 1000) * pricing["cost_per_1k_input"]
        + (output_tokens / 1000) * pricing["cost_per_1k_output"]
    )
    return round(cost, 4)


def make_usage_logs(users_df, n=5000):
    """
    Generate 5000 AI usage log records.
    
    Each row represents one AI query:
    - WHO  made it (user, team)
    - WHAT tool they used
    - WHAT they used it for (use case)
    - HOW MUCH it consumed (tokens)
    - HOW MUCH it cost (USD)
    - WAS it efficient (quality, retry)
    """
    records = []
    start_date = datetime(2024, 1, 1)
    end_date   = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days

    for i in range(n):
        # Pick a random user
        user = users_df.sample(1).iloc[0]
        team = user["team"]

        # Pick tool from that team's preferred tools
        preferred_tools = TEAM_TOOL_MAP[team]
        # First tool in list has higher chance (50%), rest split remaining
        tool_weights = [0.50, 0.30, 0.20]
        tool = random.choices(preferred_tools, weights=tool_weights[:len(preferred_tools)], k=1)[0]

        # Pick use case from that team's common use cases
        preferred_cases = TEAM_USECASE_MAP[team]
        use_case = random.choice(preferred_cases)

        # Random date within 2024
        rand_days = random.randint(0, date_range)
        query_date = start_date + timedelta(days=rand_days)

        # Token counts — vary by use case
        # Longer use cases = more tokens
        token_range = {
            "Code Generation":      (500, 2500),
            "Data Analysis":        (400, 2000),
            "Content Writing":      (400, 1800),
            "Email Drafting":       (100, 600),
            "Report Summarization": (800, 3500),
            "Bug Fixing":           (400, 2200),
            "Research":             (600, 3000),
            "Customer Query":       (100, 500),
            "Documentation":        (300, 1500),
            "Image Generation":     (50,  200),
        }

        lo, hi = token_range.get(use_case, (200, 1000))
        input_tokens  = int(np.random.uniform(lo * 0.5, hi * 0.5))
        output_tokens = int(np.random.uniform(lo * 0.2, hi * 0.4))
        total_tokens  = input_tokens + output_tokens

        # Cost calculation
        cost = calculate_cost(tool, input_tokens, output_tokens)

        # Quality score (1 to 5) — most responses are good (3-5)
        quality = random.choices([1, 2, 3, 4, 5], weights=[4, 8, 20, 40, 28])[0]

        # Retry flag — if quality was poor, user likely tried again
        is_retry = 1 if (quality <= 2 and random.random() < 0.65) else 0

        # Session duration in minutes
        session_minutes = round(random.uniform(0.5, 30), 1)

        # Is anomaly — inject ~5% anomalous expensive records
        # This simulates users accidentally sending huge files/documents to AI
        is_anomaly = 0
        if random.random() < 0.05:
            total_tokens  = total_tokens * random.randint(5, 12)
            input_tokens  = int(total_tokens * 0.65)
            output_tokens = total_tokens - input_tokens
            cost          = round(cost * random.uniform(6, 15), 4)
            is_anomaly    = 1

        records.append({
            "log_id":         f"LOG{i+100001}",
            "date":           query_date.strftime("%Y-%m-%d"),
            "month":          query_date.strftime("%Y-%m"),
            "day_of_week":    query_date.strftime("%A"),
            "hour":           random.randint(8, 19),
            "user_id":        user["user_id"],
            "team":           team,
            "tool":           tool,
            "use_case":       use_case,
            "input_tokens":   input_tokens,
            "output_tokens":  output_tokens,
            "total_tokens":   total_tokens,
            "cost_usd":       cost,
            "quality_score":  quality,
            "session_minutes":session_minutes,
            "is_retry":       is_retry,
            "is_anomaly":     is_anomaly,
        })

    return pd.DataFrame(records)


# ═══════════════════════════════════════════════════════════
# STEP 3 — Run everything and save files
# ═══════════════════════════════════════════════════════════

if __name__ == "__main__":
    print("=" * 55)
    print("  AI SPEND INTELLIGENCE — DATASET GENERATOR")
    print("=" * 55)

    print("\n[1/6] Creating teams table...")
    teams_df = make_teams()
    teams_df.to_csv(f"{OUT}/teams.csv", index=False)
    print(f"  ✅ teams.csv — {len(teams_df)} teams")

    print("\n[2/6] Creating tools table...")
    tools_df = make_tools()
    tools_df.to_csv(f"{OUT}/tools.csv", index=False)
    print(f"  ✅ tools.csv — {len(tools_df)} tools")

    print("\n[3/6] Creating users table...")
    users_df = make_users(teams_df, n=80)
    users_df.to_csv(f"{OUT}/users.csv", index=False)
    print(f"  ✅ users.csv — {len(users_df)} employees")

    print("\n[4/6] Creating budgets table...")
    budgets_df = make_budgets()
    budgets_df.to_csv(f"{OUT}/budgets.csv", index=False)
    print(f"  ✅ budgets.csv — {len(budgets_df)} rows")

    print("\n[5/6] Generating usage logs (5000 records)...")
    logs_df = make_usage_logs(users_df, n=5000)
    logs_df.to_csv(f"{OUT}/ai_usage_logs.csv", index=False)
    print(f"  ✅ ai_usage_logs.csv — {len(logs_df)} records")

    print("\n[6/6] Saving Excel file (all tables in one file)...")
    with pd.ExcelWriter(f"{OUT}/ai_spend_data.xlsx", engine="openpyxl") as writer:
        logs_df.to_excel(writer,    sheet_name="AI_Usage_Logs",  index=False)
        users_df.to_excel(writer,   sheet_name="Users",          index=False)
        teams_df.to_excel(writer,   sheet_name="Teams",          index=False)
        tools_df.to_excel(writer,   sheet_name="Tools",          index=False)
        budgets_df.to_excel(writer, sheet_name="Budgets",        index=False)
    print(f"  ✅ ai_spend_data.xlsx — 5 sheets")

    # Summary
    print("\n" + "=" * 55)
    print("  DATASET SUMMARY")
    print("=" * 55)
    print(f"  Total records    : {len(logs_df):,}")
    print(f"  Total spend      : ${logs_df['cost_usd'].sum():.2f}")
    print(f"  Date range       : Jan 2024 – Dec 2024")
    print(f"  Teams            : {logs_df['team'].nunique()}")
    print(f"  Tools            : {logs_df['tool'].nunique()}")
    print(f"  Use cases        : {logs_df['use_case'].nunique()}")
    print(f"  Anomalies        : {logs_df['is_anomaly'].sum()}")
    print(f"  Avg quality      : {logs_df['quality_score'].mean():.2f}/5")
    print(f"  Retry rate       : {logs_df['is_retry'].mean()*100:.1f}%")
    print("\n  ✅ All files saved to data/ folder")
    print("=" * 55)
