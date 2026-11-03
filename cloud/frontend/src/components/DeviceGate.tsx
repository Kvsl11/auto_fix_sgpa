import { ReactNode, useEffect, useState } from "react";
import { Monitor, Tablet } from "lucide-react";

/** Largura mínima suportada: tablet (768px). Celulares veem apenas um aviso. */
const QUERY = "(min-width: 768px)";

export function DeviceGate({ children }: { children: ReactNode }) {
  const [ok, setOk] = useState(() => window.matchMedia(QUERY).matches);

  useEffect(() => {
    const mq = window.matchMedia(QUERY);
    const onChange = () => setOk(mq.matches);
    mq.addEventListener("change", onChange);
    return () => mq.removeEventListener("change", onChange);
  }, []);

  if (ok) return <>{children}</>;

  return (
    <div className="flex min-h-screen items-center justify-center px-6">
      <div className="card max-w-sm p-8 text-center">
        <div className="mb-4 flex justify-center gap-3 text-brand-500">
          <Monitor className="h-8 w-8" />
          <Tablet className="h-8 w-8" />
        </div>
        <h1 className="text-lg font-semibold">Disponível para computador e tablet</h1>
        <p className="mt-2 text-sm text-slate-500 dark:text-slate-400">
          O Auto Ficha OPE não é compatível com celular. Acesse por um computador ou tablet
          (em tablets pequenos, gire a tela para a horizontal).
        </p>
      </div>
    </div>
  );
}
