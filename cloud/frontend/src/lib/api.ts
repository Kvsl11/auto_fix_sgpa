// Cliente da API. VITE_API_URL permite hospedar o front (ex.: Vercel)
// separado do backend (ex.: Render/Railway/Fly). Vazio = mesma origem.
export const API_URL = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") ?? "";

export type Modo = "zeradas" | "parciais";
export type JobStatus = "starting" | "running" | "paused" | "waiting" | "stopping" | "finished" | "error";
export type LogLevel = "success" | "error" | "warning" | "info" | "default";

export interface LogEntry { ts: string; level: LogLevel; message: string }
export interface Stats {
  fichas_processadas: number;
  linhas_zeradas: number;
  checkboxes_marcadas: number;
  iniciado_em: string | null;
  finalizado_em: string | null;
}
export interface Job {
  id: string;
  created_at: string;
  usuario: string;
  modo: Modo;
  status: JobStatus;
  ativo: boolean;
  stats: Stats;
  logs?: LogEntry[];
}
export interface SystemInfo {
  auth_required: boolean;
  version: string;
  bloqueado: boolean;
  mensagem: string;
  max_concurrent: number;
  ativos: number;
}
export interface JobInput {
  usuario: string;
  senha: string;
  modo: Modo;
  fazenda?: string;
  zona?: string;
  talhao?: string;
}

const TOKEN_KEY = "auto-ficha-token";
export const token = {
  get: () => { try { return localStorage.getItem(TOKEN_KEY) ?? ""; } catch { return ""; } },
  set: (t: string) => { try { localStorage.setItem(TOKEN_KEY, t); } catch {} },
  clear: () => { try { localStorage.removeItem(TOKEN_KEY); } catch {} },
};

export class ApiError extends Error {
  constructor(public status: number, message: string) { super(message); }
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...(token.get() ? { Authorization: `Bearer ${token.get()}` } : {}),
      ...init.headers,
    },
  });
  if (!res.ok) {
    let detail = res.statusText;
    try {
      const body = await res.json();
      detail = typeof body.detail === "string" ? body.detail : JSON.stringify(body.detail);
    } catch {}
    throw new ApiError(res.status, detail);
  }
  return res.json() as Promise<T>;
}

export const api = {
  system: () => request<SystemInfo>("/api/system"),
  login: (password: string) =>
    request<{ token: string }>("/api/auth/login", { method: "POST", body: JSON.stringify({ password }) }),
  listJobs: () => request<Job[]>("/api/jobs"),
  getJob: (id: string) => request<Job>(`/api/jobs/${id}`),
  createJob: (body: JobInput) => request<Job>("/api/jobs", { method: "POST", body: JSON.stringify(body) }),
  pause: (id: string) => request(`/api/jobs/${id}/pause`, { method: "POST" }),
  resume: (id: string) => request(`/api/jobs/${id}/continue`, { method: "POST" }),
  stop: (id: string) => request(`/api/jobs/${id}/stop`, { method: "POST" }),
  click: (id: string, x: number, y: number) =>
    request(`/api/jobs/${id}/click`, { method: "POST", body: JSON.stringify({ x, y }) }),
  type: (id: string, text: string) =>
    request(`/api/jobs/${id}/type`, { method: "POST", body: JSON.stringify({ text }) }),
  screenshotUrl: (id: string) =>
    `${API_URL}/api/jobs/${id}/screenshot?token=${encodeURIComponent(token.get())}&t=${Date.now()}`,
  wsUrl: (id: string) => {
    const base = API_URL || window.location.origin;
    return `${base.replace(/^http/, "ws")}/api/jobs/${id}/ws?token=${encodeURIComponent(token.get())}`;
  },
};
