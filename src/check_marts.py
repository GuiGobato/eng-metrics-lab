import duckdb

con = duckdb.connect("data/warehouse.duckdb", read_only=True)

print("== DORA ==")
print(con.sql("""
    SELECT
        COUNT(*) AS deploys,
        ROUND(COUNT(*) / 26.0, 2) AS deploys_por_semana,
        ROUND(100.0 * SUM(CAST(caused_incident AS INT)) / COUNT(*), 1) AS change_failure_rate_pct
    FROM marts.fct_deployments
"""))
print(con.sql("""
    SELECT
        ROUND(MEDIAN(lead_time_hours) / 24, 1) AS lead_time_mediana_dias,
        COUNT(*) FILTER (WHERE release_tag IS NULL) AS prs_sem_release
    FROM marts.fct_lead_time
"""))
print(con.sql("""
    SELECT ROUND(AVG(hours_to_restore), 1) AS mttr_horas, COUNT(*) AS incidentes
    FROM marts.fct_incidents
"""))

print("== Fluxo por time (cards concluídos) ==")
print(con.sql("""
    SELECT team,
           COUNT(*) AS concluidos,
           ROUND(MEDIAN(cycle_time_days), 1) AS cycle_time_mediana_dias
    FROM marts.fct_issue_flow
    WHERE done_at IS NOT NULL
    GROUP BY 1 ORDER BY 3 DESC
"""))

print("== Tempo médio por etapa e time (horas) ==")
print(con.sql("""
    SELECT team,
           ROUND(AVG(hours_in_status) FILTER (WHERE status = 'In Progress'), 1) AS in_progress,
           ROUND(AVG(hours_in_status) FILTER (WHERE status = 'In Review'), 1) AS in_review,
           ROUND(AVG(hours_in_status) FILTER (WHERE status = 'QA'), 1) AS qa
    FROM marts.fct_time_in_status
    GROUP BY 1 ORDER BY in_review DESC
"""))