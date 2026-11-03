import { useEffect, useState } from "react";
import { CheckSquare, FileCheck2, Rows3, Timer } from "lucide-react";
import type { Stats } from "../lib/api";

function formatDuration(ms: number) {
  const s = Math.max(0, Math.floor(ms / 1000));
  const h = Math.floor(s / 3600), m = Math.floor((s % 3600) / 60), sec = s % 60;
  return [h, m, sec].map((n) => String(n).padStart(2, "0")).join(":");
}

export function StatsCards({ stats, active }: { stats?: Stats; active: boolean }) {
  const [now, setNow] = useState(Date.now());
  useEffect(() => {
    if (!active) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [active]);

  const inicio = stats?.iniciado_em ? new Date(stats.iniciado_em).getTime() : null;
  const fim = stats?.finalizado_em ? new Date(stats.finalizado_em).getTime() : now;
  const items = [
    { label: "Fichas salvas", value: stats?.fichas_processadas ?? 0, icon: FileCheck2 },
    { label: "Linhas zeradas", value: stats?.linhas_zeradas ?? 0, icon: Rows3 },
    { label: "Checkboxes", value: stats?.checkboxes_marcadas ?? 0, icon: CheckSquare },
    { label: "Tempo decorrido", value: inicio ? formatDuration(fim - inicio) : "00:00:00", icon: Timer },
  ];

  return (
    <div className="grid grid-cols-2 gap-3 xl:grid-cols-4">
      {items.map(({ label, value, icon: Icon }) => (
        <div key={label} className="card p-4">
          <div className="flex items-center justify-between text-xs font-medium text-slate-500 dark:text-slate-400">
            {label}
            <Icon className="h-4 w-4 text-brand-500" />
          </div>
          <div className="mt-2 text-2xl font-semibold tabular-nums tracking-tight">{value}</div>
        </div>
      ))}
    </div>
  );
}
