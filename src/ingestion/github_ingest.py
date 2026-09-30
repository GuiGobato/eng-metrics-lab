import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("GITHUB_TOKEN")
REPO = os.getenv("GITHUB_REPO", "astral-sh/ruff")
LOOKBACK_DAYS = int(os.getenv("LOOKBACK_DAYS", "180"))
BASE_URL = f"https://api.github.com/repos/{REPO}"
RAW_DIR = Path("data/raw")

HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
}

CUTOFF = (datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).strftime(
    "%Y-%m-%dT%H:%M:%SZ"
)


def fetch_since(endpoint, date_field, params=None, max_pages=60):
    """Pagina um endpoint ordenado do mais novo pro mais antigo
    e para ao passar da data de corte."""
    params = dict(params or {})
    params["per_page"] = 100
    results = []

    for page in range(1, max_pages + 1):
        params["page"] = page
        response = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS, params=params)
        response.raise_for_status()
        data = response.json()

        if not data:
            break

        reached_cutoff = False
        for item in data:
            item_date = item.get(date_field) or item.get("created_at")
            if item_date and item_date < CUTOFF:
                reached_cutoff = True
                continue
            results.append(item)

        print(f"  {endpoint}: página {page} ({len(results)} acumulados)")
        if reached_cutoff:
            break
        time.sleep(0.2)

    return results


def save_raw(name, data):
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / f"{name}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Salvo: {path} ({len(data)} registros)")


def main():
    if not TOKEN:
        raise SystemExit("GITHUB_TOKEN não encontrado no .env")

    print(f"Repositório: {REPO} | janela: últimos {LOOKBACK_DAYS} dias (desde {CUTOFF})")

    print("Buscando releases...")
    releases = fetch_since("releases", "published_at")
    save_raw("github_releases", releases)

    print("Buscando pull requests...")
    prs = fetch_since(
        "pulls", "created_at",
        {"state": "closed", "sort": "created", "direction": "desc"},
    )
    merged = [pr for pr in prs if pr.get("merged_at")]
    save_raw("github_pull_requests", merged)


if __name__ == "__main__":
    main()