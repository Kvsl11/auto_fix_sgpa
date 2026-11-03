import { useEffect, useMemo, useRef, useState } from "react";
import { Download, Search, Terminal } from "lucide-react";
import type { LogEntry, LogLevel } from "../lib/api";

const COLORS: Record<LogLevel, string> = {
  success: "text-emerald-600 dark:text-emerald-400",
  error: "text-red-600 dark:text-red-400",
  warning: "text-amber-600 dark:text-amber-400",
  info: "text-sky-700 dark:text-sky-300",
  default: "text-slate-700 dark:text-slate-300",
};

const FILTERS: { key: LogLevel | "all"; label: string }[] = [
  { key: "all", label: "Todos" },
  { key: "success", label: "Sucesso" },
  { key: "warning", label: "Avisos" },
  { key: "error", label: "Erros" },
];

export function LogConsole({ logs, connected }: { logs: LogEntry[]; connected: boolean }) {
  const [filter, setFilter] = useState<LogLevel | "all">("all");
  const [query, setQuery] = useState("");
  const [follow, setFollow] = useState(true);
  const box = useRef<HTMLDivElement>(null);

  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return logs.filter((l) => (filter === "all" || l.level === filter) && (!q || l.message.toLowerCase().includes(q)));
  }, [logs, filter, query]);

  useEffect(() => {
    if (follow && box.current) box.current.scrollTop = box.current.scrollHeight;
  }, [visible, follow]);

  const exportar = () => {
    const blob = new Blob([logs.map((l) => `[${l.ts}] ${l.message}`).join("\n")], { type: "text/plain" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `auto-ficha-log-${new Date().toISOString().slice(0, 19)}.txt`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  return (
    <div className="card flex min-h-[22rem] flex-col overflow-hidden">
      <div className="flex flex-wrap items-center gap-2 border-b border-slate-200 px-4 py-3 dark:border-slate-800">
        <div className="mr-auto flex items-center gap-2 text-sm font-semibold">
          <Terminal className="h-4 w-4 text-brand-500" /> Log de execução
          <span title={connected ? "Conectado em tempo real" : "Desconectado"}
            className={`h-2 w-2 rounded-full ${connected ? "bg-emerald-500" : "bg-slate-300 dark:bg-slate-600"}`} />
        </div>
        <div className="flex rounded-lg bg-slate-100 p-0.5 text-xs dark:bg-slate-800">
          {FILTERS.map((f) => (
            <button key={f.key} onClick={() => setFilter(f.key)}
              className={`rounded-md px-2.5 py-1 font-medium transition ${filter === f.key ? "bg-white shadow-sm dark:bg-slate-900" : "text-slate-500"}`}>
              {f.label}
            </button>
          ))}
        </div>
        <div className="relative">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
          <input value={query} onChange={(e) => setQuery(e.target.value)} placeholder="Buscar"
            className="input w-36 py-1.5 pl-8 text-xs" />
        </div>
        <button onClick={exportar} disabled={!logs.length} className="btn-secondary px-2.5 py-1.5 text-xs" title="Baixar log">
          <Download className="h-3.5 w-3.5" />
        </button>
      </div>

      <div ref={box} onScroll={(e) => {
          const el = e.currentTarget;
          setFollow(el.scrollHeight - el.scrollTop - el.clientHeight < 40);
        }}
        className="scrollbar-thin flex-1 overflow-auto bg-slate-50/60 p-4 font-mono text-[12.5px] leading-relaxed dark:bg-slate-950/60"
        style={{ maxHeight: "32rem" }}>
        {visible.length === 0 ? (
          <div className="flex h-full items-center justify-center text-slate-400">Nenhuma mensagem ainda.</div>
        ) : (
          visible.map((l, i) => (
            <div key={i} className="flex gap-3">
              <span className="shrink-0 select-none text-slate-400">{l.ts.slice(11)}</span>
              <span className={`break-words ${COLORS[l.level]}`}>{l.message}</span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
