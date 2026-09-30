import json
from pathlib import Path

for nome in ["github_releases", "github_pull_requests"]:
    dados = json.loads(Path(f"data/raw/{nome}.json").read_text(encoding="utf-8"))
    campo = "published_at" if "releases" in nome else "merged_at"
    datas = sorted(d[campo] for d in dados if d.get(campo))
    print(f"{nome}: {len(dados)} registros")
    print(f"  mais antigo: {datas[0]}")
    print(f"  mais recente: {datas[-1]}")