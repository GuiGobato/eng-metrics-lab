from datetime import date
from pathlib import Path

import duckdb

con = duckdb.connect("data/warehouse.duckdb", read_only=True)
OUT = Path("docs/reports")
OUT.mkdir(parents=True, exist_ok=True)


def one(sql):
    return con.sql(sql).fetchone()


deploys, cfr = one("""
    SELECT COUNT(*),
           ROUND(100.0 * SUM(CAST(caused_incident AS INT)) / COUNT(*), 1)
    FROM marts.fct_deployments
""")
lead = one("SELECT ROUND(MEDIAN(lead_time_hours) / 24, 1) FROM marts.fct_lead_time")[0]
mttr_med, mttr_avg, incidents = one("""
    SELECT ROUND(MEDIAN(hours_to_restore), 1),
           ROUND(AVG(hours_to_restore), 1),
           COUNT(*)
    FROM marts.fct_incidents
""")

weeks = con.sql("""
    SELECT done_week, COUNT(*) AS n
    FROM marts.fct_issue_flow
    WHERE done_at IS NOT NULL
      AND done_week < DATE_TRUNC('week', CURRENT_DATE)
    GROUP BY 1 ORDER BY 1 DESC LIMIT 2
""").fetchall()
last_week = weeks[0] if weeks else (None, 0)
prev_week = weeks[1] if len(weeks) > 1 else (None, 0)

teams = con.sql("""
    WITH flow AS (
        SELECT team,
               ROUND(MEDIAN(cycle_time_days), 1) AS cycle_time,
               COUNT(*) FILTER (
                   WHERE current_status IN ('In Progress', 'In Review', 'QA')
               ) AS wip
        FROM marts.fct_issue_flow GROUP BY 1
    ),
    review AS (
        SELECT team, ROUND(AVG(hours_in_status), 1) AS review_hours
        FROM marts.fct_time_in_status
        WHERE status = 'In Review' GROUP BY 1
    )
    SELECT team, cycle_time, wip, review_hours
    FROM flow JOIN review USING (team)
    ORDER BY review_hours DESC
""").fetchall()

# Ponto de atenção: time com review mais lento vs. média dos demais
worst = teams[0]
others = [t[3] for t in teams[1:]]
ratio = worst[3] / (sum(others) / len(others)) if others else 1

rows = "\n".join(
    f"| {t[0]} | {t[1]} | {t[2]} | {t[3]} |" for t in teams
)

report = f"""# Relatório de engenharia - {date.today():%d/%m/%Y}

> Dados de PRs e releases: reais (GitHub). Cards e incidentes: simulados.

## Resumo
- Semana completa mais recente: {last_week[1]} cards concluídos
  (anterior: {prev_week[1]}).
- Ponto de atenção: **{worst[0]}** tem tempo em review {ratio:.1f}x maior
  que a média dos demais times.

## DORA (últimos 180 dias)
| Métrica | Valor |
|---|---|
| Deploys | {deploys} |
| Lead Time (mediana) | {lead} dias |
| Change Failure Rate | {cfr}% |
| MTTR (mediana) | {mttr_med} h (média {mttr_avg} h) |

Ressalva: {incidents} incidentes. Amostra pequena, use como indicativo.

## Fluxo por time
| Time | Cycle Time (dias, mediana) | WIP | Tempo em Review (h, média) |
|---|---|---|---|
{rows}

## Ação sugerida
Discutir com o líder de **{worst[0]}** um acordo de tempo para primeira
revisão e acompanhar o efeito no Cycle Time nas próximas semanas.
"""

path = OUT / f"relatorio_{date.today():%Y-%m-%d}.md"
path.write_text(report, encoding="utf-8")
print(f"Relatório gerado: {path}")