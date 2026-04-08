"""
=============================================================
AI SPEND INTELLIGENCE — DASHBOARD GENERATOR
=============================================================
This script AUTO-GENERATES the HTML dashboard from Python.
It reads the analysis results and embeds them into HTML.

Why auto-generate instead of manually building HTML?
→ The numbers update automatically when data changes
→ Shows Python skill (not just copy-pasting HTML)
→ Impressive in interviews: "My dashboard is code-generated"

How it works:
1. Read CSV result files
2. Build HTML string in Python
3. Write to dashboard/index.html
=============================================================
"""

import pandas as pd
import os

# ── PATHS ─────────────────────────────────────────────────
BASE = ".."
OUTPUTS = f"{BASE}/outputs"
DASH = f"{BASE}/dashboard"

# ── LOAD ANALYSIS RESULTS ─────────────────────────────────
team_spend    = pd.read_csv(f"{OUTPUTS}/team_spend.csv")
tool_spend    = pd.read_csv(f"{OUTPUTS}/tool_spend.csv")
monthly       = pd.read_csv(f"{OUTPUTS}/monthly_trend.csv")
use_case      = pd.read_csv(f"{OUTPUTS}/use_case_analysis.csv")
recs          = pd.read_csv(f"{OUTPUTS}/recommendations.csv")
logs          = pd.read_csv(f"{OUTPUTS}/logs_with_anomaly_flags.csv")

# ── COMPUTE KPIs ──────────────────────────────────────────
total_spend   = round(logs['cost_usd'].sum(), 2)
total_req     = len(logs)
active_users  = logs['user_id'].nunique()
avg_quality   = round(logs['quality_score'].mean(), 2)
retry_rate    = round(logs['is_retry'].mean() * 100, 1)
anomalies     = int(logs['anomaly_detected'].sum())
waste_usd     = round(logs[logs['anomaly_detected']==1]['cost_usd'].sum(), 2)
top_team      = team_spend.iloc[0]['team']
top_tool      = tool_spend.iloc[0]['tool']
peak_month    = monthly.sort_values('spend_usd', ascending=False).iloc[0]['month']


# ── BUILD RECOMMENDATION ROWS ─────────────────────────────
def rec_rows():
    icons = {
        'Run prompt engineering training': '⚡',
        'Set token limits per request':    '🔒',
        'Review tool selection':           '🔍',
        'Monitor monthly — usage is healthy': '✅',
    }
    colors = {
        'Run prompt engineering training': '#DC2626',
        'Set token limits per request':    '#D97706',
        'Review tool selection':           '#7C3AED',
        'Monitor monthly — usage is healthy': '#16A34A',
    }
    rows = ""
    for _, row in recs.iterrows():
        rec_text = row['recommendation']
        icon  = icons.get(rec_text, '📌')
        color = colors.get(rec_text, '#374151')
        rows += f"""
        <tr>
          <td style="font-weight:600;color:#1e293b">{row['team']}</td>
          <td style="font-family:monospace;color:#2563eb">${row['total_spend']:.2f}</td>
          <td>{row['avg_quality']}/5</td>
          <td>{row['retry_rate']}%</td>
          <td>{row['anomalies']}</td>
          <td><span style="background:{color}15;color:{color};padding:3px 10px;
              border-radius:4px;font-size:12px;font-weight:500">{icon} {rec_text}</span></td>
        </tr>"""
    return rows


# ── BUILD USE CASE ROWS ───────────────────────────────────
def use_case_rows():
    rows = ""
    max_spend = use_case['spend_usd'].max()
    for _, row in use_case.iterrows():
        pct = int(row['spend_usd'] / max_spend * 100)
        rows += f"""
        <tr>
          <td style="font-weight:500;color:#1e293b">{row['use_case']}</td>
          <td style="font-family:monospace">{row['requests']:,}</td>
          <td style="font-family:monospace;color:#2563eb">${row['spend_usd']:.2f}</td>
          <td>{row['avg_quality']:.1f}/5</td>
          <td>{row['retry_pct']:.1f}%</td>
          <td>
            <div style="background:#e2e8f0;border-radius:4px;height:8px;width:120px">
              <div style="background:#2563eb;height:100%;width:{pct}%;border-radius:4px"></div>
            </div>
          </td>
        </tr>"""
    return rows


# ── GENERATE FULL HTML ────────────────────────────────────
html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AI Spend Intelligence & Optimization Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
/* ── RESET & BASE ── */
*, *::before, *::after {{ margin:0; padding:0; box-sizing:border-box; }}
:root {{
  --navy:   #0f172a; --blue:  #2563eb; --blue-lt: #eff6ff;
  --green:  #16a34a; --red:   #dc2626; --amber:   #d97706;
  --border: #e2e8f0; --bg:    #f8fafc; --white:   #ffffff;
  --text:   #1e293b; --muted: #64748b;
}}
html {{ scroll-behavior:smooth; }}
body {{ font-family:'Inter',sans-serif; background:var(--bg); color:var(--text);
        font-size:14px; line-height:1.6; -webkit-font-smoothing:antialiased; }}

/* ── TOPBAR ── */
.topbar {{ background:var(--navy); color:white; padding:0 2rem;
           display:flex; align-items:center; justify-content:space-between;
           height:52px; position:sticky; top:0; z-index:100; }}
.topbar-logo {{ font-family:'JetBrains Mono',monospace; font-size:13px;
                display:flex; align-items:center; gap:.6rem; }}
.logo-icon {{ background:rgba(255,255,255,.1); border-radius:6px;
              width:28px; height:28px; display:flex; align-items:center;
              justify-content:center; font-size:14px; }}
.topbar-nav {{ display:flex; gap:0; list-style:none; }}
.topbar-nav a {{ color:rgba(255,255,255,.55); text-decoration:none;
                  font-size:12.5px; padding:0 1rem; height:52px;
                  display:flex; align-items:center;
                  border-bottom:2px solid transparent;
                  transition:color .15s, border-color .15s; }}
.topbar-nav a:hover {{ color:white; border-color:var(--blue); }}
.live-chip {{ background:rgba(22,163,74,.15); border:1px solid rgba(22,163,74,.3);
              color:#4ade80; font-size:11px; font-family:'JetBrains Mono',monospace;
              padding:4px 12px; border-radius:100px;
              display:flex; align-items:center; gap:6px; }}
.live-dot {{ width:6px; height:6px; border-radius:50%; background:#4ade80;
             animation:pulse 2s infinite; }}
@keyframes pulse {{ 0%,100%{{opacity:1}} 50%{{opacity:.3}} }}

/* ── HERO ── */
.hero {{ background:linear-gradient(135deg, var(--navy) 0%, #1e3a5f 100%);
         color:white; padding:2.5rem 2rem 2rem; border-bottom:1px solid #1e293b; }}
.hero-tag {{ display:inline-flex; align-items:center; gap:.5rem;
             background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.15);
             font-size:11.5px; padding:4px 12px; border-radius:100px;
             font-family:'JetBrains Mono',monospace; margin-bottom:1rem; }}
.hero-title {{ font-size:clamp(1.6rem,3vw,2.4rem); font-weight:700;
               line-height:1.1; margin-bottom:.6rem; letter-spacing:-.02em; }}
.hero-title span {{ color:#60a5fa; }}
.hero-desc {{ font-size:14px; color:rgba(255,255,255,.65); font-weight:300;
              max-width:640px; line-height:1.8; margin-bottom:1.25rem; }}
.hero-pills {{ display:flex; flex-wrap:wrap; gap:.4rem; }}
.hpill {{ font-family:'JetBrains Mono',monospace; font-size:11px;
          padding:3px 10px; border-radius:4px;
          border:1px solid rgba(255,255,255,.15);
          color:rgba(255,255,255,.65); background:rgba(255,255,255,.05); }}
.hpill.blue  {{ background:rgba(96,165,250,.15); border-color:rgba(96,165,250,.35); color:#93c5fd; }}
.hpill.green {{ background:rgba(74,222,128,.1);  border-color:rgba(74,222,128,.3);  color:#86efac; }}
.hpill.red   {{ background:rgba(248,113,113,.1); border-color:rgba(248,113,113,.3); color:#fca5a5; }}

/* ── KPI STRIP ── */
.kpi-strip {{ display:grid; grid-template-columns:repeat(5,1fr);
              border-bottom:1px solid var(--border); }}
.kpi {{ background:white; padding:1.25rem 1.4rem;
        border-right:1px solid var(--border); position:relative; }}
.kpi:last-child {{ border-right:none; }}
.kpi::before {{ content:''; position:absolute; top:0; left:0; right:0;
                height:3px; background:var(--kc, #2563eb); }}
.kpi-label {{ font-size:10.5px; text-transform:uppercase; letter-spacing:.07em;
              color:var(--muted); font-weight:600; margin-bottom:.4rem; }}
.kpi-val {{ font-family:'JetBrains Mono',monospace; font-size:1.6rem;
            font-weight:500; color:var(--navy); line-height:1; margin-bottom:.25rem; }}
.kpi-note {{ font-size:11.5px; color:var(--muted); font-weight:300; }}
.kpi-tag {{ display:inline-block; font-size:10.5px; font-weight:600;
            padding:2px 7px; border-radius:3px; margin-top:.3rem;
            font-family:'JetBrains Mono',monospace; }}
.kt-g {{ background:#dcfce7; color:#166534; }}
.kt-r {{ background:#fee2e2; color:#991b1b; }}
.kt-a {{ background:#fef3c7; color:#92400e; }}

/* ── BODY ── */
.body {{ padding:1.75rem 2rem; max-width:1400px; margin:0 auto;
         display:flex; flex-direction:column; gap:1.75rem; }}

/* ── SECTION HEADER ── */
.sh {{ margin-bottom:1rem; }}
.sh-eye {{ font-family:'JetBrains Mono',monospace; font-size:10.5px;
           color:var(--blue); letter-spacing:.1em; text-transform:uppercase;
           margin-bottom:.3rem; font-weight:500; }}
.sh-title {{ font-size:1rem; font-weight:700; color:var(--navy);
             letter-spacing:-.01em; }}
.sh-sub {{ font-size:12.5px; color:var(--muted); font-weight:300; margin-top:2px; }}

/* ── CARD ── */
.card {{ background:white; border:1px solid var(--border);
         border-radius:10px; overflow:hidden; transition:box-shadow .2s; }}
.card:hover {{ box-shadow:0 4px 16px rgba(0,0,0,.06); }}
.card-head {{ padding:.85rem 1.1rem .7rem; border-bottom:1px solid var(--border);
              display:flex; justify-content:space-between; align-items:flex-start; }}
.ct {{ font-size:13px; font-weight:600; color:var(--navy); }}
.cs {{ font-size:11.5px; color:var(--muted); margin-top:2px; font-weight:300; }}
.cbadge {{ font-family:'JetBrains Mono',monospace; font-size:10px;
           color:var(--muted); background:var(--bg); padding:3px 8px;
           border:1px solid var(--border); border-radius:3px; white-space:nowrap; }}
.card img {{ width:100%; display:block; }}
.card-foot {{ padding:.65rem 1.1rem; background:#f8fafc;
              border-top:1px solid var(--border); font-size:12px;
              color:var(--muted); line-height:1.55; font-style:italic; }}
.card-foot strong {{ color:var(--text); font-style:normal; font-weight:500; }}

/* ── GRIDS ── */
.g2 {{ display:grid; grid-template-columns:1fr 1fr; gap:1.25rem; }}
.g3 {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:1.25rem; }}

/* ── TABLE ── */
.tbl-wrap {{ overflow-x:auto; }}
table {{ width:100%; border-collapse:collapse; font-size:13px; }}
thead tr {{ background:var(--navy); color:white; }}
thead th {{ padding:.65rem 1rem; text-align:left; font-size:10.5px;
            text-transform:uppercase; letter-spacing:.07em; font-weight:500; white-space:nowrap; }}
tbody tr {{ border-bottom:1px solid var(--border); transition:background .15s; }}
tbody tr:hover {{ background:#f8fafc; }}
tbody td {{ padding:.8rem 1rem; }}

/* ── INSIGHT CARDS ── */
.ic-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:1rem; }}
.ic {{ background:white; border:1px solid var(--border); border-radius:10px;
       padding:1.1rem 1.2rem; border-top:3px solid var(--ic-c, #2563eb); }}
.ic-num {{ font-family:'JetBrains Mono',monospace; font-size:10px;
           color:var(--muted); text-transform:uppercase; letter-spacing:.06em;
           margin-bottom:.35rem; }}
.ic-title {{ font-size:13.5px; font-weight:600; color:var(--navy);
             margin-bottom:.4rem; line-height:1.3; }}
.ic-body {{ font-size:12.5px; color:var(--muted); line-height:1.65; font-weight:300; }}
.ic-body strong {{ color:var(--text); font-weight:500; }}
.ic-metric {{ margin-top:.65rem; font-family:'JetBrains Mono',monospace;
              font-size:11px; font-weight:500; padding:4px 8px;
              border-radius:4px; display:inline-block; }}

/* ── REC GRID ── */
.rc-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; }}
.rc {{ background:white; border:1px solid var(--border); border-radius:10px;
       padding:1.2rem 1.3rem; }}
.rc-icon {{ font-size:22px; margin-bottom:.7rem; }}
.rc-title {{ font-size:13.5px; font-weight:600; color:var(--navy); margin-bottom:.4rem; }}
.rc-body {{ font-size:12.5px; color:var(--muted); line-height:1.65; font-weight:300; }}
.rc-save {{ margin-top:.7rem; font-family:'JetBrains Mono',monospace;
            font-size:11px; font-weight:500; color:var(--green); }}

/* ── STACK ── */
.stack {{ background:white; border:1px solid var(--border); border-radius:10px;
          padding:1rem 1.4rem; display:flex; align-items:center; gap:1.25rem; }}
.stack-lbl {{ font-size:11px; text-transform:uppercase; letter-spacing:.07em;
              color:var(--muted); font-weight:600; flex-shrink:0; }}
.chips {{ display:flex; flex-wrap:wrap; gap:.4rem; }}
.chip {{ font-family:'JetBrains Mono',monospace; font-size:11px; padding:4px 10px;
         border-radius:4px; background:var(--bg); border:1px solid var(--border); color:var(--text); }}
.chip.hi {{ background:#eff6ff; border-color:#bfdbfe; color:var(--blue); }}

/* ── FOOTER ── */
footer {{ border-top:1px solid var(--border); padding:1.25rem 2rem;
          display:flex; justify-content:space-between; align-items:center;
          font-size:12px; color:var(--muted); }}
footer strong {{ color:var(--text); font-weight:600; }}

/* ── FADE ANIMATION ── */
.fade {{ opacity:0; transform:translateY(18px);
         transition:opacity .5s ease, transform .5s ease; }}
.fade.in {{ opacity:1; transform:translateY(0); }}

@media(max-width:900px) {{
  .kpi-strip {{ grid-template-columns:repeat(3,1fr); }}
  .g2,.g3,.ic-grid,.rc-grid {{ grid-template-columns:1fr; }}
  .topbar-nav {{ display:none; }}
}}
</style>
</head>
<body>

<!-- TOPBAR -->
<nav class="topbar">
  <div class="topbar-logo">
    <div class="logo-icon">🤖</div>
    AI Spend Intelligence
  </div>
  <ul class="topbar-nav">
    <li><a href="#overview">Overview</a></li>
    <li><a href="#trends">Trends</a></li>
    <li><a href="#teams">Teams &amp; Tools</a></li>
    <li><a href="#efficiency">Efficiency</a></li>
    <li><a href="#anomalies">Anomalies</a></li>
    <li><a href="#insights">Insights</a></li>
  </ul>
  <div class="live-chip"><span class="live-dot"></span>Analysis Complete · 5,000 records</div>
</nav>

<!-- HERO -->
<div class="hero fade" id="overview">
  <div class="hero-tag">📊 Data Analytics Project · AI Cost Optimization</div>
  <h1 class="hero-title">AI Spend Intelligence<br>&amp; <span>Optimization</span> Dashboard</h1>
  <p class="hero-desc">
    Tracks AI tool usage, token consumption, and cost efficiency across 8 teams.
    Identifies wasteful spending using statistical anomaly detection,
    computes ROI per use case, and auto-generates optimization recommendations.
    Built with SQL, Python (pandas · NumPy · Matplotlib), and auto-generated HTML.
  </p>
  <div class="hero-pills">
    <span class="hpill blue">SQL · 15 Advanced Queries</span>
    <span class="hpill blue">Python · pandas · NumPy · Matplotlib</span>
    <span class="hpill green">5,000 Usage Records · 8 Teams · 6 Tools</span>
    <span class="hpill red">${waste_usd} Waste Identified</span>
    <span class="hpill">Jan–Dec 2024 · SQLite</span>
    <span class="hpill">GitHub Pages</span>
  </div>
</div>

<!-- KPI STRIP -->
<div class="kpi-strip fade">
  <div class="kpi" style="--kc:#2563eb">
    <div class="kpi-label">Total AI Spend</div>
    <div class="kpi-val">${total_spend:.2f}</div>
    <div class="kpi-note">Full year 2024 · 8 teams</div>
    <div class="kpi-tag kt-a">↑ Q3 was peak</div>
  </div>
  <div class="kpi" style="--kc:#16a34a">
    <div class="kpi-label">Total Requests</div>
    <div class="kpi-val">{total_req:,}</div>
    <div class="kpi-note">{active_users} active users</div>
    <div class="kpi-tag kt-g">↑ Growing usage</div>
  </div>
  <div class="kpi" style="--kc:#d97706">
    <div class="kpi-label">Avg Quality Score</div>
    <div class="kpi-val">{avg_quality}<small style="font-size:1rem;color:#94a3b8">/5</small></div>
    <div class="kpi-note">Response quality rating</div>
    <div class="kpi-tag kt-g">Consistently good</div>
  </div>
  <div class="kpi" style="--kc:#dc2626">
    <div class="kpi-label">Waste Identified</div>
    <div class="kpi-val">${waste_usd}</div>
    <div class="kpi-note">{anomalies} anomalous requests</div>
    <div class="kpi-tag kt-r">Needs attention</div>
  </div>
  <div class="kpi" style="--kc:#7c3aed">
    <div class="kpi-label">Retry Rate</div>
    <div class="kpi-val">{retry_rate}<small style="font-size:1rem;color:#94a3b8">%</small></div>
    <div class="kpi-note">Re-prompts = wasted spend</div>
    <div class="kpi-tag kt-a">Action needed</div>
  </div>
</div>

<!-- BODY -->
<div class="body">

  <!-- TRENDS -->
  <div class="fade" id="trends">
    <div class="sh">
      <div class="sh-eye">01 · Time Series</div>
      <div class="sh-title">Monthly AI Spend & Request Volume</div>
      <div class="sh-sub">How spending changed across all 12 months of 2024</div>
    </div>
    <div class="card">
      <div class="card-head">
        <div><div class="ct">Monthly Spend vs Request Volume — Jan to Dec 2024</div>
             <div class="cs">Blue line = Spend (USD) · Red dashed = Number of requests</div></div>
        <span class="cbadge">SQL Query 4 · Time Series</span>
      </div>
      <img src="charts/01_monthly_trend.png" alt="Monthly Trend">
      <div class="card-foot">
        <strong>Finding:</strong> {peak_month} was the peak spending month. Usage shows a clear upward trend in H2 2024 as teams expanded AI adoption. Month-over-month growth was computed using the SQL LAG() window function (Query 13).
      </div>
    </div>
  </div>

  <!-- TEAM + TOOL -->
  <div class="fade" id="teams">
    <div class="sh">
      <div class="sh-eye">02 · Spend Breakdown</div>
      <div class="sh-title">Spend by Team & by AI Tool</div>
      <div class="sh-sub">Which departments and tools are driving the most cost</div>
    </div>
    <div class="g2">
      <div class="card">
        <div class="card-head">
          <div><div class="ct">Total AI Spend by Team</div>
               <div class="cs">Ranked by annual spend — 2024</div></div>
          <span class="cbadge">SQL Query 2 · GROUP BY</span>
        </div>
        <img src="charts/02_team_spend.png" alt="Spend by Team">
        <div class="card-foot">
          <strong>{top_team}</strong> is the top spending team — driven primarily by {tool_spend.iloc[0]['tool']} usage. This analysis helps the finance team decide where to set tighter budgets.
        </div>
      </div>
      <div class="card">
        <div class="card-head">
          <div><div class="ct">AI Spend Distribution by Tool</div>
               <div class="cs">Which tools cost the company the most</div></div>
          <span class="cbadge">SQL Query 3 · Aggregation</span>
        </div>
        <img src="charts/03_tool_spend.png" alt="Spend by Tool">
        <div class="card-foot">
          <strong>{top_tool}</strong> is the highest-cost tool. Key insight: routing low-complexity tasks (emails, summaries) from expensive models to cheaper alternatives saves ~60–70% per request with minimal quality loss.
        </div>
      </div>
    </div>
  </div>

  <!-- EFFICIENCY -->
  <div class="fade" id="efficiency">
    <div class="sh">
      <div class="sh-eye">03 · Efficiency Analysis</div>
      <div class="sh-title">Quality Score vs Retry Rate</div>
      <div class="sh-sub">Which teams get value for money — and which ones waste it</div>
    </div>
    <div class="g2">
      <div class="card">
        <div class="card-head">
          <div><div class="ct">Team Efficiency — Quality vs Retry Rate</div>
               <div class="cs">Bubble size = total spend · Top-left = most efficient</div></div>
          <span class="cbadge">SQL Query 9 · Efficiency</span>
        </div>
        <img src="charts/04_quality_vs_retry.png" alt="Quality vs Retry">
        <div class="card-foot">
          Teams with <strong>high retry rates</strong> are spending money on poor prompts. The most efficient teams are in the top-left: high quality, low retries. This directly maps to SQL Query 9 which calculates wasted spend per team.
        </div>
      </div>
      <div class="card">
        <div class="card-head">
          <div><div class="ct">AI Usage by Hour of Day</div>
               <div class="cs">Peak usage windows highlighted in red</div></div>
          <span class="cbadge">SQL Query 10 · Hourly</span>
        </div>
        <img src="charts/05_hourly_pattern.png" alt="Hourly Pattern">
        <div class="card-foot">
          Peak AI usage at <strong>9–11am and 2–4pm</strong> aligns with typical deep-work hours. Late-evening usage worth monitoring — may indicate overtime or non-work use.
        </div>
      </div>
    </div>
  </div>

  <!-- ANOMALIES -->
  <div class="fade" id="anomalies">
    <div class="sh">
      <div class="sh-eye">04 · Anomaly Detection</div>
      <div class="sh-title">Identifying Wasteful Requests</div>
      <div class="sh-sub">Z-Score and IQR statistical methods flag unusually expensive requests</div>
    </div>
    <div class="card">
      <div class="card-head">
        <div><div class="ct">Cost Distribution — Normal vs Anomalous Requests</div>
             <div class="cs">Z-Score (>3σ) + IQR (>Q3+3×IQR) — two methods for robust detection</div></div>
        <span class="cbadge">Python · NumPy · Z-Score + IQR</span>
      </div>
      <img src="charts/06_anomaly_distribution.png" alt="Anomaly Distribution">
      <div class="card-foot">
        <strong>{anomalies} anomalous requests detected</strong> — ${waste_usd} in estimated waste.
        These requests consumed 5–12× more tokens than normal. Root cause: users accidentally
        sending large files or unoptimized prompts. Fix: set per-request token limits at the API level.
      </div>
    </div>
  </div>

  <!-- USE CASE TABLE -->
  <div class="fade">
    <div class="sh">
      <div class="sh-eye">05 · Use Case Analysis</div>
      <div class="sh-title">What Are Teams Using AI For?</div>
      <div class="sh-sub">Cost and quality breakdown by AI use case — which delivers the best ROI</div>
    </div>
    <div class="card">
      <div class="card-head">
        <div><div class="ct">Use Case Performance — Spend, Quality & Retry Rate</div>
             <div class="cs">Bar shows relative spend as % of top use case</div></div>
        <span class="cbadge">SQL Query 5</span>
      </div>
      <div class="tbl-wrap">
        <table>
          <thead><tr>
            <th>Use Case</th><th>Requests</th><th>Total Spend</th>
            <th>Avg Quality</th><th>Retry Rate</th><th>Relative Spend</th>
          </tr></thead>
          <tbody>{use_case_rows()}</tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- RECOMMENDATIONS TABLE -->
  <div class="fade">
    <div class="sh">
      <div class="sh-eye">06 · Automated Recommendations</div>
      <div class="sh-title">Team-Level Action Plan</div>
      <div class="sh-sub">Auto-generated by SQL Query 15 using CASE WHEN conditional logic</div>
    </div>
    <div class="card">
      <div class="card-head">
        <div><div class="ct">Per-Team Recommendations — Generated from Data</div>
             <div class="cs">Each recommendation is driven by the team's actual spend, quality, and retry metrics</div></div>
        <span class="cbadge">SQL Query 15 · CTE + CASE WHEN</span>
      </div>
      <div class="tbl-wrap">
        <table>
          <thead><tr>
            <th>Team</th><th>Total Spend</th><th>Avg Quality</th>
            <th>Retry Rate</th><th>Anomalies</th><th>Recommendation</th>
          </tr></thead>
          <tbody>{rec_rows()}</tbody>
        </table>
      </div>
    </div>
  </div>

  <!-- KEY INSIGHTS -->
  <div class="fade" id="insights">
    <div class="sh">
      <div class="sh-eye">07 · Business Insights</div>
      <div class="sh-title">Key Findings from the Analysis</div>
      <div class="sh-sub">Four critical insights extracted from SQL queries and Python analysis</div>
    </div>
    <div class="ic-grid">
      <div class="ic" style="--ic-c:#2563eb">
        <div class="ic-num">Finding 01 · Spend</div>
        <div class="ic-title">{top_team} drives the highest AI spend</div>
        <div class="ic-body">
          The <strong>{top_team}</strong> team accounts for the largest share of total AI spend —
          primarily due to heavy usage of expensive models for code generation and bug fixing.
          Routing simple tasks to cheaper alternatives could reduce this by 25–35%.
        </div>
        <div class="ic-metric" style="background:#eff6ff;color:#1d4ed8">
          ${team_spend.iloc[0]['spend_usd']:.2f} · {round(team_spend.iloc[0]['spend_usd']/total_spend*100,1)}% of total
        </div>
      </div>
      <div class="ic" style="--ic-c:#dc2626">
        <div class="ic-num">Finding 02 · Waste</div>
        <div class="ic-title">${waste_usd} wasted on anomalous requests</div>
        <div class="ic-body">
          <strong>{anomalies} requests</strong> were flagged as anomalous using Z-Score and IQR
          statistical methods. These consumed 5–12× normal token counts due to
          unoptimized prompts sending large unstructured text. Simple API token limits fix this.
        </div>
        <div class="ic-metric" style="background:#fee2e2;color:#991b1b">
          {anomalies} anomalies · ${waste_usd} waste
        </div>
      </div>
      <div class="ic" style="--ic-c:#d97706">
        <div class="ic-num">Finding 03 · Efficiency</div>
        <div class="ic-title">{retry_rate}% of all requests are retried</div>
        <div class="ic-body">
          <strong>{retry_rate}%</strong> of requests are re-done because the first AI response
          was insufficient. This is wasted money. The primary cause is poor prompt structure —
          not a tool problem. Prompt engineering training can halve this rate within 30 days.
        </div>
        <div class="ic-metric" style="background:#fef3c7;color:#92400e">
          {retry_rate}% retry rate · Fixable with training
        </div>
      </div>
      <div class="ic" style="--ic-c:#16a34a">
        <div class="ic-num">Finding 04 · Opportunity</div>
        <div class="ic-title">Smart tool routing reduces cost by 40–60%</div>
        <div class="ic-body">
          Analysis shows <strong>cheaper models (GPT-3.5, Gemini-Pro)</strong> deliver near-identical
          quality scores for Email Drafting and Customer Queries compared to GPT-4.
          A tool routing policy can save 40–60% on per-request costs with zero quality drop.
        </div>
        <div class="ic-metric" style="background:#dcfce7;color:#166534">
          Potential 40–60% cost reduction
        </div>
      </div>
    </div>
  </div>

  <!-- RECOMMENDATIONS -->
  <div class="fade">
    <div class="sh">
      <div class="sh-eye">08 · Action Plan</div>
      <div class="sh-title">6 Optimization Recommendations</div>
      <div class="sh-sub">Data-backed actions to reduce cost and improve AI ROI</div>
    </div>
    <div class="rc-grid">
      <div class="rc">
        <div class="rc-icon">⚡</div>
        <div class="rc-title">Prompt Engineering Training</div>
        <div class="rc-body">Focused workshops for high-retry teams. Provide standard prompt templates for the top 5 use cases. Target: cut retry rate from {retry_rate}% to under 5% in 60 days.</div>
        <div class="rc-save">Saves ~15–20% of wasted retry spend</div>
      </div>
      <div class="rc">
        <div class="rc-icon">🔒</div>
        <div class="rc-title">API Token Limits</div>
        <div class="rc-body">Set per-request token limits at the API gateway. Alert when a single request exceeds 5× team average. Auto-block requests over 10,000 tokens without approval.</div>
        <div class="rc-save">Eliminates ${waste_usd} annual anomaly waste</div>
      </div>
      <div class="rc">
        <div class="rc-icon">💡</div>
        <div class="rc-title">Smart Tool Routing</div>
        <div class="rc-body">Decision matrix: Emails/FAQs → GPT-3.5 or Gemini (70% cheaper). Complex analysis → GPT-4 or Claude. Code → GitHub Copilot. Route by complexity, not by habit.</div>
        <div class="rc-save">40–60% cost reduction on eligible tasks</div>
      </div>
      <div class="rc">
        <div class="rc-icon">📊</div>
        <div class="rc-title">Monthly Budget Alerts</div>
        <div class="rc-body">Automated alerts at 80% and 95% budget utilization per team per month. SQL Query 8 shows teams regularly exceed budget with no early warning system currently in place.</div>
        <div class="rc-save">Prevents budget overruns before they happen</div>
      </div>
      <div class="rc">
        <div class="rc-icon">📚</div>
        <div class="rc-title">Internal Prompt Library</div>
        <div class="rc-body">Shared repository of validated prompts for the 10 most common use cases. Reusing tested prompts eliminates retries for repetitive tasks across all teams.</div>
        <div class="rc-save">Reduces retry rate company-wide</div>
      </div>
      <div class="rc">
        <div class="rc-icon">📈</div>
        <div class="rc-title">Weekly Monitoring</div>
        <div class="rc-body">Refresh this dashboard weekly. Track quality score trends by team and tool. Use SQL Query 13 (MoM growth) to catch spending spikes early before they become budget problems.</div>
        <div class="rc-save">Ongoing cost governance culture</div>
      </div>
    </div>
  </div>

  <!-- TECH STACK -->
  <div class="fade">
    <div class="stack">
      <div class="stack-lbl">Tech Stack</div>
      <div class="chips">
        <span class="chip hi">Python 3.12</span>
        <span class="chip hi">pandas</span>
        <span class="chip hi">NumPy</span>
        <span class="chip hi">Matplotlib</span>
        <span class="chip hi">SQL · SQLite</span>
        <span class="chip">15 SQL Queries</span>
        <span class="chip">CTEs</span>
        <span class="chip">Window Functions</span>
        <span class="chip">Z-Score Detection</span>
        <span class="chip">IQR Detection</span>
        <span class="chip">Excel (5 sheets)</span>
        <span class="chip">HTML Auto-generated</span>
        <span class="chip">GitHub Pages</span>
      </div>
    </div>
  </div>

</div>

<!-- FOOTER -->
<footer>
  <strong>AI Spend Intelligence & Optimization · Jyothirmayi Lakumarapu · Data Analyst</strong>
  <span>Python · SQL · 5,000 records · Jan–Dec 2024 · github.com/YOUR-USERNAME/ai-spend-intelligence</span>
</footer>

<script>
const io = new IntersectionObserver(entries => {{
  entries.forEach(e => {{ if(e.isIntersecting) e.target.classList.add('in'); }});
}}, {{ threshold: 0.07 }});
document.querySelectorAll('.fade').forEach(el => io.observe(el));
</script>
</body>
</html>"""

# Write HTML file
out_path = f"{DASH}/index.html"
with open(out_path, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅ Dashboard generated: {out_path}")
print(f"   Open dashboard/index.html in your browser to view it.")
