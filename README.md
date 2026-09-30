# Eng Metrics Lab

Projeto de portfólio de **Engineering Analytics**: transforma dados de GitHub
e Jira em métricas DORA e de fluxo, expostas por uma API e um dashboard.
Mede a saúde do sistema de engenharia, nunca pessoas.

## O que é real e o que é simulado

- **Real:** pull requests e releases do repositório `astral-sh/ruff` (GitHub API).
- **Simulado:** cards do Jira, histórico de status e incidentes. Foram gerados
  com uma semente fixa e ligados aos releases reais. O gargalo de review do
  time Mobile foi plantado de propósito para demonstrar a análise.

## Arquitetura

    GitHub API ─┐
                ├─► Python (ingestão) ─► DuckDB (raw → staging → marts)
    Jira/Incid. ┘   (dados sintéticos)          │
                                                ▼
                                        FastAPI (Python)
                                                │
                                                ▼
                                    Next.js + React + Recharts

## Métricas

Deployment Frequency, Lead Time for Changes, Change Failure Rate, MTTR,
Cycle Time, Throughput, WIP e tempo por etapa. Definições e limitações em
[docs/metodologia.md](docs/metodologia.md).

## Como rodar

Pré-requisitos: Python 3.11+, Node.js 20+, um token do GitHub (somente leitura
em repositórios públicos).

    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt

Crie um arquivo `.env` na raiz:

    GITHUB_TOKEN=seu_token
    GITHUB_REPO=astral-sh/ruff
    LOOKBACK_DAYS=180

Pipeline de dados:

    python src\ingestion\github_ingest.py
    python src\ingestion\generate_synthetic.py
    python src\build_warehouse.py
    python src\check_staging.py
    python src\check_marts.py

API (na raiz do projeto):

    uvicorn src.api.main:app --reload

Dashboard (em outro terminal):

    cd web
    npm install
    npm run dev

Abra http://localhost:3000.

## Decisões de design

- Camadas raw → staging → marts, com SQL versionado em `sql/`.
- As métricas moram no SQL e na API. O front só exibe.
- Pipeline idempotente: rodar de novo reconstrói tudo sem duplicar.
- Testes de qualidade e de plausibilidade dos dados.
- O campo de usuário do GitHub é descartado na carga.

## Limitações

Lead time aproximado, amostra pequena de incidentes, dados de Jira simulados.
Detalhes em `docs/metodologia.md`.

## Próximos passos

Ritual de reporte, dados de custo de cloud (FinOps) e sinais de
confiabilidade no estilo Datadog.