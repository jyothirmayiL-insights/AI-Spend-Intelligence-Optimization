-- ================================================================
-- AI SPEND INTELLIGENCE & OPTIMIZATION
-- SQL Layer — Schema + 15 Business Queries
-- Database: SQLite (ai_spend.db)
-- Author: Jyothirmayi Lakumarapu
-- ================================================================
-- HOW TO READ THIS FILE:
--   Each query has:
--   → BUSINESS QUESTION it answers
--   → WHAT SQL CONCEPT it uses
--   → The actual SQL
-- ================================================================


-- ================================================================
-- PART A — DATABASE SCHEMA
-- (Create all 4 tables with proper data types and relationships)
-- ================================================================

-- Drop tables if they exist (for clean re-runs)
DROP TABLE IF EXISTS ai_usage_logs;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS teams;
DROP TABLE IF EXISTS tools;
DROP TABLE IF EXISTS budgets;

-- Table 1: Teams (reference table)
CREATE TABLE teams (
    team_id             TEXT PRIMARY KEY,
    team_name           TEXT NOT NULL,
    monthly_budget_usd  REAL,
    head_count          INTEGER
);

-- Table 2: Tools (reference table)
CREATE TABLE tools (
    tool_id             TEXT PRIMARY KEY,
    tool_name           TEXT NOT NULL,
    cost_per_1k_input   REAL,
    cost_per_1k_output  REAL,
    pricing_model       TEXT
);

-- Table 3: Users (employee directory)
CREATE TABLE users (
    user_id     TEXT PRIMARY KEY,
    user_name   TEXT,
    team        TEXT,
    team_id     TEXT,
    role        TEXT,
    join_date   TEXT,
    FOREIGN KEY (team_id) REFERENCES teams(team_id)
);

-- Table 4: Budgets (monthly budget per team)
CREATE TABLE budgets (
    team        TEXT,
    month       TEXT,
    budget_usd  REAL,
    PRIMARY KEY (team, month)
);

-- Table 5: AI Usage Logs (main fact table — 5000 rows)
-- Every row = one AI query made by one user
CREATE TABLE ai_usage_logs (
    log_id          TEXT PRIMARY KEY,
    date            TEXT,           -- YYYY-MM-DD
    month           TEXT,           -- YYYY-MM
    day_of_week     TEXT,
    hour            INTEGER,        -- 0 to 23
    user_id         TEXT,
    team            TEXT,
    tool            TEXT,
    use_case        TEXT,
    input_tokens    INTEGER,
    output_tokens   INTEGER,
    total_tokens    INTEGER,        -- input + output (what you pay for)
    cost_usd        REAL,           -- actual cost of this request
    quality_score   INTEGER,        -- 1-5 (was the AI response good?)
    session_minutes REAL,
    is_retry        INTEGER,        -- 1 = user had to re-ask (wasted money)
    is_anomaly      INTEGER,        -- 1 = unusually expensive request
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);


-- ================================================================
-- PART B — BUSINESS QUERIES (15 Total)
-- ================================================================


-- ────────────────────────────────────────────────────────────────
-- QUERY 1: EXECUTIVE SUMMARY — OVERALL KPIs
-- ────────────────────────────────────────────────────────────────
-- Business Question: Give me one summary of all AI spend this year.
-- SQL Concept: Basic aggregations (SUM, AVG, COUNT, ROUND)
-- Used in: KPI cards at the top of the dashboard
-- ────────────────────────────────────────────────────────────────
SELECT
    COUNT(*)                                        AS total_requests,
    COUNT(DISTINCT user_id)                         AS active_users,
    COUNT(DISTINCT team)                            AS teams_using_ai,
    COUNT(DISTINCT tool)                            AS tools_in_use,
    ROUND(SUM(cost_usd), 2)                         AS total_spend_usd,
    ROUND(AVG(cost_usd), 4)                         AS avg_cost_per_request,
    ROUND(SUM(total_tokens) / 1000000.0, 2)         AS total_tokens_millions,
    ROUND(AVG(quality_score), 2)                    AS avg_quality_score,
    SUM(is_anomaly)                                 AS anomalous_requests,
    ROUND(100.0 * SUM(is_retry) / COUNT(*), 1)      AS retry_rate_pct
FROM ai_usage_logs;


-- ────────────────────────────────────────────────────────────────
-- QUERY 2: SPEND BY TEAM — WHICH DEPARTMENT COSTS THE MOST?
-- ────────────────────────────────────────────────────────────────
-- Business Question: Which teams are spending the most on AI tools?
-- SQL Concept: GROUP BY, ORDER BY, multiple aggregations
-- Used in: Bar chart — Spend by Team
-- ────────────────────────────────────────────────────────────────
SELECT
    team,
    COUNT(*)                                            AS total_requests,
    COUNT(DISTINCT user_id)                             AS users,
    ROUND(SUM(cost_usd), 2)                             AS total_spend_usd,
    ROUND(AVG(cost_usd), 4)                             AS avg_cost_per_request,
    ROUND(SUM(cost_usd) / COUNT(DISTINCT user_id), 2)   AS spend_per_user,
    ROUND(SUM(total_tokens) / 1000000.0, 3)             AS tokens_millions,
    ROUND(AVG(quality_score), 2)                        AS avg_quality,
    ROUND(100.0 * SUM(is_retry) / COUNT(*), 1)          AS retry_rate_pct
FROM ai_usage_logs
GROUP BY team
ORDER BY total_spend_usd DESC;


-- ────────────────────────────────────────────────────────────────
-- QUERY 3: SPEND BY TOOL — WHICH AI TOOL IS MOST EXPENSIVE?
-- ────────────────────────────────────────────────────────────────
-- Business Question: Which AI tool costs us the most money?
-- SQL Concept: GROUP BY with multiple metrics
-- Used in: Donut chart — Spend by Tool
-- ────────────────────────────────────────────────────────────────
SELECT
    tool,
    COUNT(*)                                        AS total_requests,
    COUNT(DISTINCT user_id)                         AS unique_users,
    ROUND(SUM(cost_usd), 2)                         AS total_spend_usd,
    ROUND(AVG(cost_usd), 5)                         AS avg_cost_per_request,
    ROUND(SUM(total_tokens) / 1000000.0, 3)         AS tokens_millions,
    ROUND(AVG(total_tokens), 0)                     AS avg_tokens_per_request,
    ROUND(AVG(quality_score), 2)                    AS avg_quality_score,
    ROUND(100.0 * SUM(is_anomaly) / COUNT(*), 1)    AS anomaly_rate_pct
FROM ai_usage_logs
GROUP BY tool
ORDER BY total_spend_usd DESC;


-- ────────────────────────────────────────────────────────────────
-- QUERY 4: MONTHLY SPEND TREND — HOW IS SPENDING CHANGING?
-- ────────────────────────────────────────────────────────────────
-- Business Question: Is AI spend going up or down each month?
-- SQL Concept: GROUP BY month (time-series analysis)
-- Used in: Line chart — Monthly trend
-- ────────────────────────────────────────────────────────────────
SELECT
    month,
    COUNT(*)                                AS total_requests,
    COUNT(DISTINCT user_id)                 AS active_users,
    ROUND(SUM(cost_usd), 2)                 AS total_spend_usd,
    ROUND(AVG(cost_usd), 4)                 AS avg_cost_per_request,
    ROUND(SUM(total_tokens) / 1000000.0, 3) AS tokens_millions,
    ROUND(AVG(quality_score), 2)            AS avg_quality,
    SUM(is_anomaly)                         AS anomalies_detected
FROM ai_usage_logs
GROUP BY month
ORDER BY month;


-- ────────────────────────────────────────────────────────────────
-- QUERY 5: USE CASE ANALYSIS — WHAT ARE TEAMS USING AI FOR?
-- ────────────────────────────────────────────────────────────────
-- Business Question: Which use cases cost the most and deliver best quality?
-- SQL Concept: GROUP BY with derived column (roi_score = quality / cost)
-- Used in: Use case efficiency table
-- ────────────────────────────────────────────────────────────────
SELECT
    use_case,
    COUNT(*)                                            AS total_requests,
    ROUND(SUM(cost_usd), 2)                             AS total_spend_usd,
    ROUND(AVG(cost_usd), 5)                             AS avg_cost_per_request,
    ROUND(AVG(total_tokens), 0)                         AS avg_tokens_per_request,
    ROUND(AVG(quality_score), 2)                        AS avg_quality_score,
    ROUND(AVG(quality_score) / (AVG(cost_usd) + 0.001), 1) AS roi_score,
    ROUND(100.0 * SUM(is_retry) / COUNT(*), 1)          AS retry_rate_pct
FROM ai_usage_logs
GROUP BY use_case
ORDER BY total_spend_usd DESC;


-- ────────────────────────────────────────────────────────────────
-- QUERY 6: TOP 15 HIGHEST SPENDING USERS
-- ────────────────────────────────────────────────────────────────
-- Business Question: Which individual employees are using AI the most?
-- SQL Concept: GROUP BY user with JOIN to get team info
-- Used in: Top users table
-- ────────────────────────────────────────────────────────────────
SELECT
    l.user_id,
    l.team,
    COUNT(*)                                AS total_requests,
    ROUND(SUM(l.cost_usd), 2)               AS total_spend_usd,
    ROUND(AVG(l.cost_usd), 4)               AS avg_cost_per_request,
    ROUND(SUM(l.total_tokens) / 1000.0, 1)  AS total_tokens_k,
    ROUND(AVG(l.quality_score), 2)          AS avg_quality,
    SUM(l.is_retry)                         AS total_retries,
    SUM(l.is_anomaly)                       AS anomalies
FROM ai_usage_logs l
GROUP BY l.user_id
ORDER BY total_spend_usd DESC
LIMIT 15;


-- ────────────────────────────────────────────────────────────────
-- QUERY 7: ANOMALY DETECTION — WHICH REQUESTS ARE SUSPICIOUSLY EXPENSIVE?
-- ────────────────────────────────────────────────────────────────
-- Business Question: Which requests cost far more than normal? (Waste detection)
-- SQL Concept: CTE (Common Table Expression) — calculate avg per team first,
--              then compare each record against that average
-- This is an ADVANCED query — interviewers love CTEs!
-- ────────────────────────────────────────────────────────────────
WITH team_averages AS (
    -- Step 1: Calculate average cost per team (for normal requests only)
    SELECT
        team,
        ROUND(AVG(cost_usd), 5)         AS avg_cost,
        ROUND(AVG(cost_usd) * 5, 5)     AS anomaly_threshold
    FROM ai_usage_logs
    WHERE is_anomaly = 0
    GROUP BY team
)
-- Step 2: Find all requests that exceed 5x the team average
SELECT
    l.log_id,
    l.date,
    l.user_id,
    l.team,
    l.tool,
    l.use_case,
    l.cost_usd                          AS actual_cost,
    ROUND(t.avg_cost, 5)                AS team_avg_cost,
    ROUND(l.cost_usd / (t.avg_cost + 0.0001), 1) AS times_above_avg,
    l.total_tokens,
    l.quality_score
FROM ai_usage_logs l
JOIN team_averages t ON l.team = t.team
WHERE l.cost_usd > t.anomaly_threshold
ORDER BY l.cost_usd DESC
LIMIT 25;


-- ────────────────────────────────────────────────────────────────
-- QUERY 8: BUDGET vs ACTUAL — IS EACH TEAM WITHIN BUDGET?
-- ────────────────────────────────────────────────────────────────
-- Business Question: Are teams staying within their monthly AI budgets?
-- SQL Concept: CTE + LEFT JOIN + CASE WHEN (conditional logic)
-- Used in: Budget tracking table with traffic light status
-- ────────────────────────────────────────────────────────────────
WITH monthly_actual AS (
    SELECT
        team,
        month,
        ROUND(SUM(cost_usd), 2) AS actual_spend
    FROM ai_usage_logs
    GROUP BY team, month
)
SELECT
    b.team,
    b.month,
    b.budget_usd,
    COALESCE(a.actual_spend, 0)         AS actual_spend_usd,
    ROUND(b.budget_usd - COALESCE(a.actual_spend, 0), 2) AS remaining_usd,
    ROUND(
        100.0 * COALESCE(a.actual_spend, 0) / b.budget_usd, 1
    )                                   AS budget_used_pct,
    CASE
        WHEN COALESCE(a.actual_spend, 0) > b.budget_usd         THEN 'Over Budget'
        WHEN COALESCE(a.actual_spend, 0) > b.budget_usd * 0.85  THEN 'Near Limit'
        ELSE 'On Track'
    END                                 AS budget_status
FROM budgets b
LEFT JOIN monthly_actual a
    ON b.team = a.team AND b.month = a.month
ORDER BY b.month, actual_spend_usd DESC;


-- ────────────────────────────────────────────────────────────────
-- QUERY 9: RETRY RATE ANALYSIS — WHO IS WASTING MONEY ON BAD PROMPTS?
-- ────────────────────────────────────────────────────────────────
-- Business Question: Which teams are re-prompting the most?
--   (High retry = poor prompt quality = wasted spend)
-- SQL Concept: Conditional aggregation with CASE WHEN inside SUM
-- ────────────────────────────────────────────────────────────────
SELECT
    team,
    COUNT(*)                                            AS total_requests,
    SUM(is_retry)                                       AS retried_requests,
    ROUND(100.0 * SUM(is_retry) / COUNT(*), 1)          AS retry_rate_pct,
    ROUND(
        SUM(CASE WHEN is_retry = 1 THEN cost_usd ELSE 0 END), 2
    )                                                   AS wasted_spend_usd,
    ROUND(AVG(quality_score), 2)                        AS avg_quality_score,
    ROUND(SUM(cost_usd), 2)                             AS total_spend_usd
FROM ai_usage_logs
GROUP BY team
ORDER BY retry_rate_pct DESC;


-- ────────────────────────────────────────────────────────────────
-- QUERY 10: HOURLY USAGE PATTERN — WHEN IS AI USED MOST?
-- ────────────────────────────────────────────────────────────────
-- Business Question: What time of day do teams use AI tools most?
-- SQL Concept: GROUP BY on a numeric column (hour of day)
-- Used in: Bar chart showing peak usage hours
-- ────────────────────────────────────────────────────────────────
SELECT
    hour,
    COUNT(*)                        AS total_requests,
    COUNT(DISTINCT user_id)         AS unique_users,
    ROUND(SUM(cost_usd), 2)         AS total_spend_usd,
    ROUND(AVG(quality_score), 2)    AS avg_quality_score
FROM ai_usage_logs
GROUP BY hour
ORDER BY hour;


-- ────────────────────────────────────────────────────────────────
-- QUERY 11: TEAM × TOOL USAGE — WHICH TEAM USES WHICH TOOL?
-- ────────────────────────────────────────────────────────────────
-- Business Question: For each team, which tools do they use and how much?
-- SQL Concept: Multi-column GROUP BY
-- Used in: Heatmap data (team vs tool matrix)
-- ────────────────────────────────────────────────────────────────
SELECT
    team,
    tool,
    COUNT(*)                        AS requests,
    ROUND(SUM(cost_usd), 2)         AS spend_usd,
    ROUND(AVG(quality_score), 2)    AS avg_quality
FROM ai_usage_logs
GROUP BY team, tool
ORDER BY team, spend_usd DESC;


-- ────────────────────────────────────────────────────────────────
-- QUERY 12: RANK TEAMS BY SPEND (WINDOW FUNCTION)
-- ────────────────────────────────────────────────────────────────
-- Business Question: What is the rank of each team by spending?
-- SQL Concept: Window function — RANK() OVER (ORDER BY ...)
-- Advanced SQL — key interview skill!
-- ────────────────────────────────────────────────────────────────
SELECT
    team,
    ROUND(SUM(cost_usd), 2)                                 AS total_spend_usd,
    COUNT(*)                                                AS total_requests,
    RANK() OVER (ORDER BY SUM(cost_usd) DESC)               AS spend_rank,
    ROUND(100.0 * SUM(cost_usd) / SUM(SUM(cost_usd)) OVER (), 1) AS pct_of_total
FROM ai_usage_logs
GROUP BY team
ORDER BY spend_rank;


-- ────────────────────────────────────────────────────────────────
-- QUERY 13: MONTH-OVER-MONTH GROWTH (LAG WINDOW FUNCTION)
-- ────────────────────────────────────────────────────────────────
-- Business Question: Is spending growing or shrinking month by month?
-- SQL Concept: LAG() window function — looks at previous row value
-- Very impressive in interviews!
-- ────────────────────────────────────────────────────────────────
WITH monthly_spend AS (
    SELECT
        month,
        ROUND(SUM(cost_usd), 2) AS spend_usd,
        COUNT(*)                AS requests
    FROM ai_usage_logs
    GROUP BY month
)
SELECT
    month,
    spend_usd,
    requests,
    LAG(spend_usd) OVER (ORDER BY month)    AS prev_month_spend,
    ROUND(
        100.0 * (spend_usd - LAG(spend_usd) OVER (ORDER BY month))
        / (LAG(spend_usd) OVER (ORDER BY month) + 0.01),
        1
    )                                       AS mom_growth_pct
FROM monthly_spend
ORDER BY month;


-- ────────────────────────────────────────────────────────────────
-- QUERY 14: TOP TOOL PER TEAM (PARTITION BY WINDOW FUNCTION)
-- ────────────────────────────────────────────────────────────────
-- Business Question: For EACH team, what is their #1 most-used tool?
-- SQL Concept: RANK() OVER PARTITION BY — ranks within each group
-- Partition = like GROUP BY but for window functions
-- ────────────────────────────────────────────────────────────────
WITH tool_per_team AS (
    SELECT
        team,
        tool,
        COUNT(*)                AS requests,
        ROUND(SUM(cost_usd), 2) AS spend_usd,
        RANK() OVER (
            PARTITION BY team
            ORDER BY SUM(cost_usd) DESC
        )                       AS rank_within_team
    FROM ai_usage_logs
    GROUP BY team, tool
)
SELECT
    team,
    tool                AS top_tool,
    requests,
    spend_usd,
    rank_within_team
FROM tool_per_team
WHERE rank_within_team = 1
ORDER BY spend_usd DESC;


-- ────────────────────────────────────────────────────────────────
-- QUERY 15: COST OPTIMIZATION RECOMMENDATIONS
-- ────────────────────────────────────────────────────────────────
-- Business Question: Which teams need action and what should they do?
-- SQL Concept: CTE + CASE WHEN for automated recommendation logic
-- This is the "AI insight layer" — auto-generates advice from data
-- ────────────────────────────────────────────────────────────────
WITH team_stats AS (
    SELECT
        team,
        ROUND(SUM(cost_usd), 2)                             AS total_spend,
        ROUND(AVG(quality_score), 2)                        AS avg_quality,
        ROUND(100.0 * SUM(is_retry) / COUNT(*), 1)          AS retry_rate,
        SUM(is_anomaly)                                     AS anomalies,
        ROUND(SUM(cost_usd) / COUNT(DISTINCT user_id), 2)   AS cost_per_user,
        ROUND(
            SUM(CASE WHEN is_retry = 1 THEN cost_usd ELSE 0 END), 2
        )                                                   AS wasted_on_retries
    FROM ai_usage_logs
    GROUP BY team
)
SELECT
    team,
    total_spend,
    avg_quality,
    retry_rate,
    anomalies,
    cost_per_user,
    wasted_on_retries,
    CASE
        WHEN retry_rate > 15
            THEN 'HIGH PRIORITY: Retry rate above 15% — run prompt engineering training'
        WHEN anomalies > 20
            THEN 'HIGH PRIORITY: Too many anomalies — set token limits per request'
        WHEN avg_quality < 3.0
            THEN 'MEDIUM: Low quality scores — review tool selection for this team'
        WHEN cost_per_user > 5
            THEN 'MEDIUM: High per-user cost — introduce usage policies'
        ELSE 'LOW: Usage looks healthy — continue monitoring'
    END AS recommendation,
    CASE
        WHEN retry_rate > 15   THEN 'High'
        WHEN anomalies > 20    THEN 'High'
        WHEN avg_quality < 3.0 THEN 'Medium'
        WHEN cost_per_user > 5 THEN 'Medium'
        ELSE 'Low'
    END AS priority
FROM team_stats
ORDER BY total_spend DESC;
