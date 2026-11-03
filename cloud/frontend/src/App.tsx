import { useCallback, useEffect, useState } from "react";
import { AlertTriangle, History, LogOut, Moon, Pause, Play, Square, Sun, Zap } from "lucide-react";
import { api, ApiError, Job, JobInput, SystemInfo, token } from "./lib/api";
import { useJobStream } from "./lib/useJobStream";
import { RunForm } from "./components/RunForm";
import { StatsCards } from "./components/StatsCards";
import { BrowserPreview } from "./components/BrowserPreview";
import { LogConsole } from "./components/LogConsole";
import { StatusBadge } from "./components/StatusBadge";
import { LoginScreen } from "./components/LoginScreen";

const JOB_KEY = "auto-ficha-job";

function useTheme() {
  const [dark, setDark] = useState(() => document.documentElement.classList.contains("dark"));
  useEffect(() => {
    document.documentElement.classList.toggle("dark", dark);
    try { localStorage.setItem("theme", dark ? "dark" : "light"); } catch {}
  }, [dark]);
  return [dark, setDark] as const;
}

export default function App() {
  const [dark, setDark] = useTheme();
  const [system, setSystem] = useState<SystemInfo | null>(null);
  const [needLogin, setNeedLogin] = useState(false);
  const [jobId, setJobId] = useState<string | null>(() => { try { return localStorage.getItem(JOB_KEY); } catch { return null; } });
  const [history, setHistory] = useState<Job[]>([]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const { job, logs, connected } = useJobStream(needLogin ? null : jobId);

  const handleErr = useCallback((e: unknown) => {
    if (e instanceof ApiError && e.status === 401) { token.clear(); setNeedLogin(true); return; }
    if (e instanceof ApiError && e.status === 404) { setJobId(null); return; }
    setError(e instanceof Error ? e.message : String(e));
  }, []);

  const refresh = useCallback(async () => {
    try {
      const s = await api.system();
      setSystem(s);
      if (s.auth_required && !token.get()) { setNeedLogin(true); return; }
      setHistory(await api.listJobs());
    } catch (e) { handleErr(e); }
  }, [handleErr]);

  useEffect(() => { refresh(); const t = setInterval(refresh, 10000); return () => clearInterval(t); }, [refresh]);
  useEffect(() => { try { jobId ? localStorage.setItem(JOB_KEY, jobId) : localStorage.removeItem(JOB_KEY); } catch {} }, [jobId]);
  useEffect(() => {
    if (jobId && history.length && !history.some((h) => h.id === jobId)) setJobId(null);
    // Abriu o painel em outro dispositivo? Segue a execução ativa mais recente.
    if (!jobId) { const ativa = history.find((h) => h.ativo); if (ativa) setJobId(ativa.id); }
  }, [history, jobId]);

  const ativo = Boolean(job?.ativo);
  const status = job?.status ?? "idle";

  const start = async (input: JobInput) => {
    setSubmitting(true); setError("");
    try { const j = await api.createJob(input); setJobId(j.id); refresh(); }
    catch (e) { handleErr(e); }
    finally { setSubmitting(false); }
  };
  const act = (fn: (id: string) => Promise<unknown>) => () => { if (jobId) fn(jobId).catch(handleErr); };

  // Atalho herdado do app desktop: Esc = Pausar
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => { if (e.key === "Escape" && jobId && status === "running") api.pause(jobId).catch(handleErr); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [jobId, status, handleErr]);

  if (needLogin) return <LoginScreen onLogged={() => { setNeedLogin(false); refresh(); }} />;

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur dark:border-slate-800 dark:bg-slate-950/80">
        <div className="mx-auto flex h-16 max-w-7xl items-center gap-3 px-6">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-brand-500 text-white shadow-md shadow-brand-500/30">
            <Zap className="h-5 w-5" />
          </div>
          <div className="leading-tight">
            <div className="font-semibold">Auto Ficha OPE</div>
            <div className="text-xs text-slate-500 dark:text-slate-400">Versão {system?.version ?? "—"} · Cloud</div>
          </div>
          <div className="ml-auto flex items-center gap-2">
            <span className="text-xs text-slate-500">
              {system ? `${system.ativos}/${system.max_concurrent} execuções ativas` : ""}
            </span>
            <button className="btn-secondary h-9 w-9 p-0" onClick={() => setDark(!dark)} aria-label="Alternar tema">
              {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            {system?.auth_required && (
              <button className="btn-secondary h-9 w-9 p-0" aria-label="Sair" onClick={() => { token.clear(); setNeedLogin(true); }}>
                <LogOut className="h-4 w-4" />
              </button>
            )}
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl space-y-6 px-6 py-6">
        {system?.bloqueado && (
          <div className="flex items-start gap-3 rounded-2xl border border-red-200 bg-red-50 p-4 text-sm text-red-800 dark:border-red-500/30 dark:bg-red-500/10 dark:text-red-300">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0" />
            <div><strong>Sistema bloqueado.</strong> {system.mensagem}</div>
          </div>
        )}
        {error && (
          <div className="flex items-center justify-between rounded-2xl border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300">
            {error}
            <button className="text-xs font-semibold underline" onClick={() => setError("")}>Fechar</button>
          </div>
        )}

        <div className="grid gap-6 md:grid-cols-[18rem_1fr] xl:grid-cols-[22rem_1fr]">
          <aside className="space-y-6">
            <RunForm disabled={ativo || Boolean(system?.bloqueado)} submitting={submitting} onSubmit={start} />

            {history.length > 0 && (
              <div className="card p-5">
                <h2 className="mb-3 flex items-center gap-2 text-sm font-semibold">
                  <History className="h-4 w-4 text-brand-500" /> Execuções recentes
                </h2>
                <ul className="space-y-1.5">
                  {history.slice(0, 8).map((h) => (
                    <li key={h.id}>
                      <button onClick={() => setJobId(h.id)}
                        className={`flex w-full items-center justify-between gap-2 rounded-xl px-3 py-2 text-left text-sm transition hover:bg-slate-100 dark:hover:bg-slate-800 ${h.id === jobId ? "bg-slate-100 dark:bg-slate-800" : ""}`}>
                        <span className="min-w-0">
                          <span className="block truncate font-medium">{h.usuario}</span>
                          <span className="block text-xs text-slate-500">{new Date(h.created_at).toLocaleString("pt-BR")} · {h.stats.fichas_processadas} fichas</span>
                        </span>
                        <StatusBadge status={h.status} />
                      </button>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </aside>

          <section className="min-w-0 space-y-6">
            <div className="card flex flex-wrap items-center gap-3 p-4">
              <div className="mr-auto flex items-center gap-3">
                <StatusBadge status={status} />
                {status === "waiting" && (
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    Sem fichas para inserir. Ajuste os filtros no navegador (modo interativo) e clique em Continuar.
                  </span>
                )}
              </div>
              <button className="btn-primary" disabled={!ativo || !["paused", "waiting"].includes(status)} onClick={act(api.resume)}>
                <Play className="h-4 w-4" /> Continuar
              </button>
              <button className="btn-secondary" disabled={status !== "running"} onClick={act(api.pause)} title="Atalho: Esc">
                <Pause className="h-4 w-4" /> Pausar
              </button>
              <button className="btn-danger" disabled={!ativo} onClick={act(api.stop)}>
                <Square className="h-4 w-4" /> Encerrar
              </button>
            </div>

            <StatsCards stats={job?.stats} active={ativo} />

            <div className="grid gap-6 2xl:grid-cols-2">
              <BrowserPreview jobId={jobId} active={ativo} />
              <LogConsole logs={logs} connected={connected} />
            </div>
          </section>
        </div>
      </main>
    </div>
  );
}
