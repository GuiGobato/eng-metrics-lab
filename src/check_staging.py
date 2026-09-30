print("\n== Sanidade dos dados sintéticos ==")
abertos = con.sql("SELECT COUNT(*) FROM staging.stg_jira_issues WHERE done_at IS NULL").fetchone()[0]
print(f"cards em aberto: {abertos} (esperado: > 0)")
incs = con.sql("SELECT COUNT(*) FROM staging.stg_incidents").fetchone()[0]
print(f"incidentes: {incs} (esperado: >= 4)")