import duckdb
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

DB_PATH = "data/warehouse.duckdb"
WEEKS_IN_WINDOW = 26  # 180 dias

app = FastAPI(title="Eng Metrics Lab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

con = duckdb.connect(DB_PATH, read_only=True)


def query(sql, params=None):
    """Executa SQL e devolve lista de dicionários."""
    cur = con.cursor()
    result = cur.execute(sql, params or [])
    cols = [d[0] for d in result.description]
    return [dict(zip(cols, row)) for row in result.fetchall()]


@app.get("/api/summary")
def summary():
    deploys = query("""
        SELECT COUNT(*) AS deploys,
               ROUND(100.0 * SUM(CAST(caused_incident AS INT)) / COUNT(*), 1) AS change_failure_rate_pct
        FROM marts.fct_deployments
    """)[0]
    lead = query("""
        SELECT ROUND(MEDIAN(lead_time_hours) / 24, 1) AS lead_time_median_days
        FROM marts.fct_lead_time
    """)[0]
    mttr = query("""
        SELECT ROUND(AVG(hours_to_restore), 1) AS mttr_avg_hours,
               ROUND(MEDIAN(hours_to_restore), 1) AS mttr_median_hours,
               COUNT(*) AS incidents
        FROM marts.fct_incidents
    """)[0]
    return {
        **deploys,
        "deploys_per_week": round(deploys["deploys"] / WEEKS_IN_WINDOW, 2),
        **lead,
        **mttr,
    }


@app.get("/api/deployments/weekly")
def deployments_weekly():
    return query("""
        SELECT week_start, COUNT(*) AS deploys,
               SUM(CAST(caused_incident AS INT)) AS with_incident
        FROM marts.fct_deployments
        GROUP BY 1 ORDER BY 1
    """)


@app.get("/api/throughput/weekly")
def throughput_weekly(team: str | None = Query(default=None)):
    return query("""
        SELECT done_week AS week_start, COUNT(*) AS throughput
        FROM marts.fct_issue_flow
        WHERE done_at IS NOT NULL
          AND (CAST(? AS VARCHAR) IS NULL OR team = ?)
        GROUP BY 1 ORDER BY 1
    """, [team, team])


@app.get("/api/teams")
def teams():
    return query("""
        WITH flow AS (
            SELECT team,
                   COUNT(*) FILTER (WHERE done_at IS NOT NULL) AS done,
                   ROUND(MEDIAN(cycle_time_days), 1) AS cycle_time_median_days,
                   COUNT(*) FILTER (
                       WHERE current_status IN ('In Progress', 'In Review', 'QA')
                   ) AS wip
            FROM marts.fct_issue_flow
            GROUP BY 1
        ),
        review AS (
            SELECT team, ROUND(AVG(hours_in_status), 1) AS review_avg_hours
            FROM marts.fct_time_in_status
            WHERE status = 'In Review'
            GROUP BY 1
        )
        SELECT * FROM flow JOIN review USING (team) ORDER BY team
    """)


@app.get("/api/time-in-status")
def time_in_status():
    return query("""
        SELECT team, status, ROUND(AVG(hours_in_status), 1) AS avg_hours
        FROM marts.fct_time_in_status
        GROUP BY 1, 2
        ORDER BY team, MIN(CASE status
            WHEN 'Backlog' THEN 1 WHEN 'Refinement' THEN 2 WHEN 'In Progress' THEN 3
            WHEN 'In Review' THEN 4 WHEN 'QA' THEN 5 ELSE 6 END)
    """)