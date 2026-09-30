import json
import random
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pandas as pd

random.seed(42)  # resultados reproduzíveis

RAW_DIR = Path("data/raw")
FMT = "%Y-%m-%dT%H:%M:%SZ"

TEAMS = {
    # nome: (multiplicador de velocidade, multiplicador do tempo em review)
    "Plataforma": (1.0, 1.0),
    "Pagamentos": (1.2, 1.1),
    "Mobile": (1.1, 3.0),   # gargalo plantado: review lento
    "Dados": (0.9, 1.2),
}

STATUS_FLOW = ["Backlog", "Refinement", "In Progress", "In Review", "QA", "Done"]

# duração base (em horas) de cada status, sorteada entre min e max
BASE_HOURS = {
    "Backlog": (24, 240),
    "Refinement": (8, 72),
    "In Progress": (16, 96),
    "In Review": (4, 40),
    "QA": (4, 32),
}

ISSUE_TYPES = ["Story"] * 6 + ["Bug"] * 3 + ["Task"] * 2


def parse(s):
    return datetime.strptime(s, FMT).replace(tzinfo=timezone.utc)


def business_delay(hours):
    """Converte horas 'de relógio' sorteadas em um atraso levemente irregular."""
    return timedelta(hours=hours * random.uniform(0.8, 1.4))


def main():
    prs = json.loads((RAW_DIR / "github_pull_requests.json").read_text(encoding="utf-8"))
    releases = json.loads((RAW_DIR / "github_releases.json").read_text(encoding="utf-8"))

    start = parse(min(pr["created_at"] for pr in prs))
    end = parse(max(pr["merged_at"] for pr in prs))

    issues, transitions = [], []
    n_issues = 900

    for i in range(1, n_issues + 1):
        key = f"ENG-{i:04d}"
        team = random.choice(list(TEAMS))
        speed, review_mult = TEAMS[team]
        issue_type = random.choice(ISSUE_TYPES)

        created = start + timedelta(seconds=random.uniform(0, (end - start).total_seconds()))
        current = created
        history = [("Backlog", current)]
        done_at = None

        for status in STATUS_FLOW[1:]:
            previous = STATUS_FLOW[STATUS_FLOW.index(status) - 1]
            lo, hi = BASE_HOURS[previous]
            hours = random.uniform(lo, hi) * speed
            if previous == "In Review":
                hours *= review_mult
            current = current + business_delay(hours)
            if current > end:
                break
            history.append((status, current))

        if history[-1][0] == "Done":
            done_at = history[-1][1]

        issues.append({
            "issue_key": key,
            "team": team,
            "issue_type": issue_type,
            "created_at": created.strftime(FMT),
            "current_status": history[-1][0],
            "done_at": done_at.strftime(FMT) if done_at else None,
        })

        for status, ts in history:
            transitions.append({
                "issue_key": key,
                "to_status": status,
                "transitioned_at": ts.strftime(FMT),
            })

    # incidentes ligados a releases reais
    incidents = []
    for rel in releases:
        if random.random() < 0.30:
            opened = parse(rel["published_at"]) + timedelta(hours=random.uniform(0.5, 12))
            resolve_hours = random.choice([0.5, 1, 2, 4, 8, 24]) * random.uniform(0.7, 1.3)
            resolved = opened + timedelta(hours=resolve_hours)
            incidents.append({
                "incident_id": f"INC-{len(incidents) + 1:03d}",
                "release_tag": rel["tag_name"],
                "severity": random.choice(["SEV1", "SEV2", "SEV3"]),
                "opened_at": opened.strftime(FMT),
                "resolved_at": resolved.strftime(FMT),
            })

    pd.DataFrame(issues).to_csv(RAW_DIR / "jira_issues.csv", index=False)
    pd.DataFrame(transitions).to_csv(RAW_DIR / "jira_transitions.csv", index=False)
    pd.DataFrame(incidents).to_csv(RAW_DIR / "incidents.csv", index=False)

    print(f"Período: {start:%Y-%m-%d} a {end:%Y-%m-%d}")
    print(f"jira_issues: {len(issues)} | jira_transitions: {len(transitions)} | incidents: {len(incidents)}")


if __name__ == "__main__":
    main()