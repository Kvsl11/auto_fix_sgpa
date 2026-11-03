import type { JobStatus } from "../lib/api";

const MAP: Record<JobStatus | "idle", { label: string; cls: string; pulse?: boolean }> = {
  idle: { label: "Aguardando", cls: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300" },
  starting: { label: "Iniciando", cls: "bg-sky-100 text-sky-700 dark:bg-sky-500/15 dark:text-sky-300", pulse: true },
  running: { label: "Executando", cls: "bg-brand-100 text-brand-700 dark:bg-brand-500/15 dark:text-brand-300", pulse: true },
  paused: { label: "Pausado", cls: "bg-amber-100 text-amber-700 dark:bg-amber-500/15 dark:text-amber-300" },
  waiting: { label: "Aguardando nova entrada", cls: "bg-violet-100 text-violet-700 dark:bg-violet-500/15 dark:text-violet-300" },
  stopping: { label: "Encerrando", cls: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300", pulse: true },
  finished: { label: "Finalizado", cls: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300" },
  error: { label: "Erro", cls: "bg-red-100 text-red-700 dark:bg-red-500/15 dark:text-red-300" },
};

export function StatusBadge({ status }: { status: JobStatus | "idle" }) {
  const s = MAP[status];
  return (
    <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-semibold ${s.cls}`}>
      <span className="relative flex h-2 w-2">
        {s.pulse && <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-current opacity-60" />}
        <span className="relative inline-flex h-2 w-2 rounded-full bg-current" />
      </span>
      {s.label}
    </span>
  );
}
