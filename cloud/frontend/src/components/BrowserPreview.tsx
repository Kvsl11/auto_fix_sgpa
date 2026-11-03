import { FormEvent, MouseEvent, useEffect, useState } from "react";
import { Keyboard, Monitor, MousePointerClick, Send } from "lucide-react";
import { api } from "../lib/api";

/**
 * Pré-visualização ao vivo do navegador que roda na nuvem.
 * Com "Modo interativo" ligado, cliques e textos são repassados ao navegador
 * remoto — útil na etapa "Aguardando nova entrada", em que o operador ajusta
 * filtros no SGPA antes de clicar em "Continuar".
 */
export function BrowserPreview({ jobId, active }: { jobId: string | null; active: boolean }) {
  const [src, setSrc] = useState<string | null>(null);
  const [interativo, setInterativo] = useState(false);
  const [texto, setTexto] = useState("");

  useEffect(() => {
    if (!jobId || !active) return;
    let stop = false;
    let timer: number;
    // Pré-carrega a próxima imagem antes de trocar (evita "piscar").
    const tick = () => {
      const url = api.screenshotUrl(jobId);
      const img = new Image();
      img.onload = () => { if (!stop) setSrc(url); schedule(); };
      img.onerror = schedule;
      img.src = url;
    };
    const schedule = () => { if (!stop) timer = window.setTimeout(tick, 1500); };
    tick();
    return () => { stop = true; window.clearTimeout(timer); };
  }, [jobId, active]);

  useEffect(() => { if (!active) setInterativo(false); }, [active]);

  const onClick = (e: MouseEvent<HTMLImageElement>) => {
    if (!interativo || !jobId) return;
    const r = e.currentTarget.getBoundingClientRect();
    api.click(jobId, (e.clientX - r.left) / r.width, (e.clientY - r.top) / r.height).catch(() => {});
  };

  const enviarTexto = (e: FormEvent) => {
    e.preventDefault();
    if (!jobId || !texto) return;
    api.type(jobId, texto).catch(() => {});
    setTexto("");
  };

  return (
    <div className="card overflow-hidden">
      <div className="flex items-center justify-between gap-3 border-b border-slate-200 px-4 py-3 dark:border-slate-800">
        <div className="flex items-center gap-2 text-sm font-semibold">
          <Monitor className="h-4 w-4 text-brand-500" /> Navegador na nuvem
        </div>
        <label className={`flex items-center gap-2 text-xs font-medium ${active ? "cursor-pointer" : "opacity-50"}`}>
          <MousePointerClick className="h-3.5 w-3.5" /> Modo interativo
          <button type="button" role="switch" aria-checked={interativo} disabled={!active}
            onClick={() => setInterativo((v) => !v)}
            className={`relative h-5 w-9 rounded-full transition ${interativo ? "bg-brand-500" : "bg-slate-300 dark:bg-slate-700"}`}>
            <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-white shadow transition-all ${interativo ? "left-[18px]" : "left-0.5"}`} />
          </button>
        </label>
      </div>

      <div className="relative aspect-video bg-slate-100 dark:bg-slate-950">
        {src && jobId ? (
          <img src={src} alt="Tela do navegador remoto" onClick={onClick} draggable={false}
            className={`h-full w-full object-contain ${interativo ? "cursor-crosshair ring-2 ring-inset ring-brand-500" : ""} ${active ? "" : "opacity-60 grayscale"}`} />
        ) : (
          <div className="flex h-full flex-col items-center justify-center gap-2 px-6 text-center text-sm text-slate-400">
            <Monitor className="h-8 w-8" />
            {active ? "Abrindo navegador..." : "A tela do navegador aparecerá aqui durante a execução"}
          </div>
        )}
      </div>

      {interativo && (
        <form onSubmit={enviarTexto} className="flex gap-2 border-t border-slate-200 p-3 dark:border-slate-800">
          <div className="relative flex-1">
            <Keyboard className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input className="input pl-9" placeholder="Digitar no campo selecionado..." value={texto}
              onChange={(e) => setTexto(e.target.value)} />
          </div>
          <button className="btn-secondary" type="submit"><Send className="h-4 w-4" /></button>
        </form>
      )}
    </div>
  );
}
