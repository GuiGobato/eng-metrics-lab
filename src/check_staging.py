import duckdb

con = duckdb.connect("data/warehouse.duckdb", read_only=True)

print("== Contagens ==")
for t in ["stg_github_pull_requests", "stg_github_releases",
          "stg_jira_issues", "stg_jira_transitions", "stg_incidents"]:
    n = con.sql(f"SELECT COUNT(*) FROM staging.{t}").fetchone()[0]
    print(f"{t}: {n}")

print("\n== Testes (esperado: 0 em todos) ==")
testes = {
    "PRs com merge antes da abertura": """
        SELECT COUNT(*) FROM staging.stg_github_pull_requests WHERE merged_at < opened_at""",
    "issue_key duplicada": """
        SELECT COUNT(*) FROM (SELECT issue_key FROM staging.stg_jira_issues
                              GROUP BY 1 HAVING COUNT(*) > 1)""",
    "incidentes sem release correspondente": """
        SELECT COUNT(*) FROM staging.stg_incidents i
        LEFT JOIN staging.stg_github_releases r USING (release_tag)
        WHERE r.release_tag IS NULL""",
    "incidentes resolvidos antes de abrir": """
        SELECT COUNT(*) FROM staging.stg_incidents WHERE resolved_at < opened_at""",
}
for nome, sql in testes.items():
    print(f"{nome}: {con.sql(sql).fetchone()[0]}")

print("\n== Sanidade dos dados sintéticos ==")
abertos = con.sql("SELECT COUNT(*) FROM staging.stg_jira_issues WHERE done_at IS NULL").fetchone()[0]
print(f"cards em aberto: {abertos} (esperado: > 0)")
incs = con.sql("SELECT COUNT(*) FROM staging.stg_incidents").fetchone()[0]
print(f"incidentes: {incs} (esperado: >= 4)")

print("\n== Cards por status ==")
print(con.sql("""
    SELECT current_status, COUNT(*) AS cards
    FROM staging.stg_jira_issues GROUP BY 1 ORDER BY 2 DESC
"""))

print("== Período dos PRs ==")
print(con.sql("""
    SELECT MIN(merged_at) AS primeiro, MAX(merged_at) AS ultimo
    FROM staging.stg_github_pull_requests
"""))