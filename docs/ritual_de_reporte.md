# Ritual de reporte

Objetivo: transformar métricas em **conversa e ação**, não em relatório
arquivado. Toda métrica apresentada termina em uma pergunta: "o que vamos
fazer a respeito?"

## Cadência

| Ritual | Frequência | Público | Duração | Foco |
|---|---|---|---|---|
| Revisão operacional | Semanal | Time e tech lead | 15 min | Fluxo: WIP, gargalos, cards parados |
| Revisão de liderança | Mensal | Líderes técnicos e Eng Manager | 30 min | DORA, tendências, ações em andamento |
| Reporte executivo | Trimestral | Diretoria e board | 1 página | Tendência, riscos e decisões pedidas |
| Revisão da metodologia | Trimestral | Analytics + líderes | 30 min | O que vale e o que não vale medir |

## Reporte operacional (semanal, por time)

Perguntas guia:
1. O WIP está crescendo? Há cards parados numa etapa há muito tempo?
2. Qual etapa do fluxo está mais lenta que a média dos outros times?
3. A ação combinada na semana passada surtiu efeito?

Formato:
- Cycle Time (mediana) e Throughput da última semana **completa**
- Tempo médio por etapa
- WIP atual
- **Uma** ação combinada, com responsável **de time** (não de pessoa) e data

## Reporte executivo (trimestral, 1 página)

Estrutura fixa:
1. **Resumo em uma frase.** Ex.: "Entregamos com estabilidade, mas o fluxo
   do Mobile limita a velocidade."
2. **DORA:** os 4 números com tendência (subiu, caiu ou estável).
3. **Fluxo:** Cycle Time e Throughput consolidados.
4. **Risco ou gargalo principal**, com evidência.
5. **Decisão ou apoio pedido à liderança.**
6. **Ressalvas de qualidade dos dados** (ex.: amostra pequena de incidentes).

Regras:
- Sem ranking de pessoas. Comparar times só para achar **onde ajudar**, não
  para cobrar.
- Sempre mediana em tempos, com a amostra declarada.
- Se a métrica mudou de definição, avisar antes de mostrar o número.

## Regras do ritual

1. **Ação antes de gráfico.** Cada reunião termina com no máximo uma a três
   ações registradas.
2. **Sem surpresa.** O líder técnico vê os números antes da reunião.
3. **Métrica que ninguém usa é removida** na revisão trimestral.
4. **Semana parcial não entra.** Só semanas completas nos gráficos.
5. **Nunca por pessoa.** Se alguém pedir, a resposta é a seção "O que NÃO
   medimos" da metodologia.

## Registro de ações

| Data | Time | Observação | Ação | Métrica de acompanhamento | Resultado |
|---|---|---|---|---|---|
| (exemplo) | Mobile | Review 3x mais lento | Acordo de primeira revisão em 24h | Tempo em In Review | a medir |