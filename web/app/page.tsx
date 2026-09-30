"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import KpiCard from "../components/KpiCard";
import {
  api,
  type StatusTime,
  type Summary,
  type TeamRow,
  type WeeklyDeploys,
  type WeeklyThroughput,
} from "../lib/api";

const REVIEW_STATUSES = ["In Progress", "In Review", "QA"];

function ChartBox({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 text-sm font-medium text-slate-600">{title}</h3>
      <div className="h-64">{children}</div>
    </div>
  );
}

export default function Home() {
  const [view, setView] = useState<"exec" | "team">("exec");
  const [team, setTeam] = useState<string>("");
  const [error, setError] = useState<string | null>(null);

  const [summary, setSummary] = useState<Summary | null>(null);
  const [deploys, setDeploys] = useState<WeeklyDeploys[]>([]);
  const [throughputAll, setThroughputAll] = useState<WeeklyThroughput[]>([]);
  const [teams, setTeams] = useState<TeamRow[]>([]);
  const [statusTimes, setStatusTimes] = useState<StatusTime[]>([]);
  const [throughputTeam, setThroughputTeam] = useState<WeeklyThroughput[]>([]);

  useEffect(() => {
    Promise.all([
      api.summary(),
      api.deploysWeekly(),
      api.throughputWeekly(),
      api.teams(),
      api.timeInStatus(),
    ])
      .then(([s, d, t, tm, st]) => {
        setSummary(s);
        setDeploys(d);
        setThroughputAll(t);
        setTeams(tm);
        setStatusTimes(st);
        setTeam(tm[0]?.team ?? "");
      })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!team) return;
    api.throughputWeekly(team).then(setThroughputTeam).catch((e) => setError(e.message));
  }, [team]);

  // Uma linha por time, com uma coluna por etapa (formato que o Recharts espera)
  const stackedByTeam = useMemo(() => {
    return teams.map((t) => {
      const row: Record<string, string | number> = { team: t.team };
      REVIEW_STATUSES.forEach((s) => {
        row[s] =
          statusTimes.find((x) => x.team === t.team && x.status === s)?.avg_hours ?? 0;
      });
      return row;
    });
  }, [teams, statusTimes]);

  const selected = teams.find((t) => t.team === team);

  if (error) {
    return (
      <main className="p-8 text-red-600">
        Não foi possível carregar os dados: {error}. A API está rodando em
        localhost:8000?
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-slate-50 p-6 text-slate-900">
      <div className="mx-auto max-w-6xl">
        <header className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold">Eng Metrics Lab</h1>
            <p className="text-sm text-slate-500">
              Saúde do sistema de engenharia (por time, nunca por pessoa)
            </p>
          </div>
          <div className="flex gap-2">
            {(["exec", "team"] as const).map((v) => (
              <button
                key={v}
                onClick={() => setView(v)}
                className={`rounded-lg px-4 py-2 text-sm font-medium ${
                  view === v
                    ? "bg-slate-900 text-white"
                    : "bg-white text-slate-700 border border-slate-200"
                }`}
              >
                {v === "exec" ? "Visão Executiva" : "Visão por Time"}
              </button>
            ))}
          </div>
        </header>

        {view === "exec" && summary && (
          <section className="space-y-4">
            <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
              <KpiCard
                label="Deployment Frequency"
                value={`${summary.deploys_per_week}/sem`}
                hint={`${summary.deploys} deploys em 180 dias`}
              />
              <KpiCard
                label="Lead Time (mediana)"
                value={`${summary.lead_time_median_days} dias`}
                hint="Abertura do PR até o release"
              />
              <KpiCard
                label="Change Failure Rate"
                value={`${summary.change_failure_rate_pct}%`}
                hint={`${summary.incidents} incidentes`}
              />
              <KpiCard
                label="MTTR (mediana)"
                value={`${summary.mttr_median_hours} h`}
                hint={`Média: ${summary.mttr_avg_hours} h (amostra pequena)`}
              />
            </div>

            <div className="grid gap-4 md:grid-cols-2">
              <ChartBox title="Deploys por semana">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={deploys}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="week_start" fontSize={11} />
                    <YAxis allowDecimals={false} fontSize={11} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="deploys" name="Deploys" fill="#0f172a" />
                    <Bar dataKey="with_incident" name="Com incidente" fill="#dc2626" />
                  </BarChart>
                </ResponsiveContainer>
              </ChartBox>

              <ChartBox title="Throughput semanal (cards concluídos)">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={throughputAll}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="week_start" fontSize={11} />
                    <YAxis fontSize={11} />
                    <Tooltip />
                    <Line type="monotone" dataKey="throughput" stroke="#2563eb" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </ChartBox>
            </div>
          </section>
        )}

        {view === "team" && (
          <section className="space-y-4">
            <div className="flex items-center gap-2">
              <label className="text-sm text-slate-600">Time:</label>
              <select
                value={team}
                onChange={(e) => setTeam(e.target.value)}
                className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
              >
                {teams.map((t) => (
                  <option key={t.team} value={t.team}>
                    {t.team}
                  </option>
                ))}
              </select>
            </div>

            {selected && (
              <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
                <KpiCard label="Cards concluídos" value={String(selected.done)} />
                <KpiCard
                  label="Cycle Time (mediana)"
                  value={`${selected.cycle_time_median_days} dias`}
                  hint="Da entrada em In Progress até Done"
                />
                <KpiCard label="WIP atual" value={String(selected.wip)} />
                <KpiCard
                  label="Tempo médio em Review"
                  value={`${selected.review_avg_hours} h`}
                />
              </div>
            )}

            <div className="grid gap-4 md:grid-cols-2">
              <ChartBox title="Tempo médio por etapa (horas), comparando os times">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={stackedByTeam}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="team" fontSize={11} />
                    <YAxis fontSize={11} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="In Progress" stackId="a" fill="#94a3b8" />
                    <Bar dataKey="In Review" stackId="a" fill="#dc2626" />
                    <Bar dataKey="QA" stackId="a" fill="#2563eb" />
                  </BarChart>
                </ResponsiveContainer>
              </ChartBox>

              <ChartBox title={`Throughput semanal: ${team}`}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={throughputTeam}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="week_start" fontSize={11} />
                    <YAxis fontSize={11} />
                    <Tooltip />
                    <Line type="monotone" dataKey="throughput" stroke="#2563eb" dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              </ChartBox>
            </div>
          </section>
        )}
      </div>
    </main>
  );
}