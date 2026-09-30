# Metodologia das métricas

Este documento define **o que medimos, como medimos e o que não medimos**.
O objetivo é medir a saúde do **sistema** de engenharia. Nunca pessoas.

## Princípios

1. **Sistema, não indivíduos.** Nenhuma métrica, tabela ou endpoint contém
   autor, assignee ou qualquer dado individual. O campo de usuário do GitHub
   é descartado na carga (`src/build_warehouse.py`).
2. **Métrica gera ação.** Cada indicador existe para sustentar uma decisão
   (ex.: onde investir para reduzir o tempo em review).
3. **Mediana antes de média** em tempos, porque poucos casos extremos
   distorcem a média.
4. **Amostra pequena é declarada.** Métricas com poucos eventos trazem aviso.

## Fontes de dados

| Fonte | Origem | Observação |
|---|---|---|
| Pull requests e releases | GitHub API, repositório `astral-sh/ruff` | **Dados reais**, últimos 180 dias |
| Cards e transições do Jira | Gerador sintético (`generate_synthetic.py`) | **Simulado** |
| Incidentes | Gerador sintético, ligado a releases reais | **Simulado** |

## Definições

### Deployment Frequency
- **Definição:** releases publicados (não pré-release) por semana.
- **Fonte:** `marts.fct_deployments`.
- **Limitação:** o Ruff publica cerca de 1 release a cada 8 dias, então a
  frequência é menor que a de um time com deploy contínuo.

### Lead Time for Changes
- **Definição:** tempo entre a abertura do PR e o primeiro release publicado
  após o merge. Reportado pela **mediana**.
- **Fonte:** `marts.fct_lead_time`.
- **Limitações:**
  - É uma aproximação: o PR pode não estar de fato naquele release.
  - Usa a abertura do PR, não o primeiro commit (exigiria uma chamada de API
    por PR).
  - PRs mergeados depois do último release ficam sem lead time.

### Change Failure Rate
- **Definição:** releases com ao menos um incidente / total de releases.
- **Fonte:** `marts.fct_deployments`.
- **Limitação:** com poucos releases, cada incidente move muito o percentual.

### MTTR
- **Definição:** tempo entre a abertura e a resolução do incidente.
  Reportado pela **mediana**, com a média como referência.
- **Fonte:** `marts.fct_incidents`.
- **Limitação:** com 6 incidentes, é indicativo, não conclusivo. Olhar
  tendência trimestral, não mensal.

### Cycle Time
- **Definição:** tempo entre a entrada em `In Progress` e `Done`, apenas
  para cards concluídos. Reportado pela **mediana**.
- **Fonte:** `marts.fct_issue_flow`.
- **Limitação:** ignora cards ainda abertos, o que pode fazer o número
  parecer melhor do que a realidade. Por isso o WIP é exibido junto.

### Throughput
- **Definição:** cards concluídos por semana.
- **Uso:** tendência, nunca meta individual.

### WIP
- **Definição:** cards atualmente em `In Progress`, `In Review` ou `QA`.

### Tempo por etapa
- **Definição:** tempo médio em cada status do fluxo. É a métrica que
  revela gargalos.

## O que NÃO medimos

| Não medimos | Por quê |
|---|---|
| Commits, linhas de código ou PRs por pessoa | Mede volume, não valor, e incentiva comportamentos ruins |
| Ranking de desenvolvedores | Contraria o princípio de medir o sistema |
| Velocity como meta | Vira jogo de estimativas |
| Horas trabalhadas | Não indica entrega nem qualidade |

## Testes de qualidade dos dados

- Consistência: PR com merge antes da abertura, `issue_key` duplicada,
  incidente sem release, incidente resolvido antes de abrir.
- Plausibilidade: existem cards em aberto e um mínimo de incidentes.
- Executados por `src/check_staging.py`.

## Leitura de exemplo

O time Mobile tem Cycle Time mediano de 7,3 dias contra 4,1 a 5,3 dos demais.
O tempo médio em `In Review` é de 81 h contra 25 a 31 h. **Hipótese:** o
gargalo está no processo de revisão. **Ação sugerida:** definir um acordo de
tempo para primeira revisão e acompanhar o efeito no Cycle Time.