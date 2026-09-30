const API = "http://localhost:8000";

export type Summary = {
  deploys: number;
  deploys_per_week: number;
  change_failure_rate_pct: number;
  lead_time_median_days: number;
  mttr_avg_hours: number;
  mttr_median_hours: number;
  incidents: number;
};

export type WeeklyDeploys = { week_start: string; deploys: number; with_incident: number };
export type WeeklyThroughput = { week_start: string; throughput: number };
export type TeamRow = {
  team: string;
  done: number;
  cycle_time_median_days: number;
  wip: number;
  review_avg_hours: number;
};
export type StatusTime = { team: string; status: string; avg_hours: number };

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${API}${path}`);
  if (!res.ok) throw new Error(`Erro ${res.status} em ${path}`);
  return res.json();
}

export const api = {
  summary: () => get<Summary>("/api/summary"),
  deploysWeekly: () => get<WeeklyDeploys[]>("/api/deployments/weekly"),
  throughputWeekly: (team?: string) =>
    get<WeeklyThroughput[]>(
      `/api/throughput/weekly${team ? `?team=${encodeURIComponent(team)}` : ""}`
    ),
  teams: () => get<TeamRow[]>("/api/teams"),
  timeInStatus: () => get<StatusTime[]>("/api/time-in-status"),
};