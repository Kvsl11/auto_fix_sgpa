import { FormEvent, useState } from "react";
import { Eye, EyeOff, KeyRound, Layers, MapPin, Play } from "lucide-react";
import type { JobInput, Modo } from "../lib/api";

const REMEMBER_KEY = "auto-ficha-user";

function loadRemembered(): string {
  try { return localStorage.getItem(REMEMBER_KEY) ?? ""; } catch { return ""; }
}

interface Props {
  disabled: boolean;
  submitting: boolean;
  onSubmit: (input: JobInput) => void;
}

export function RunForm({ disabled, submitting, onSubmit }: Props) {
  const remembered = loadRemembered();
  const [usuario, setUsuario] = useState(remembered);
  const [senha, setSenha] = useState("");
  const [lembrar, setLembrar] = useState(Boolean(remembered));
  const [mostrar, setMostrar] = useState(false);
  const [modo, setModo] = useState<Modo>("zeradas");
  const [fazenda, setFazenda] = useState("");
  const [zona, setZona] = useState("");
  const [talhao, setTalhao] = useState("");

  const submit = (e: FormEvent) => {
    e.preventDefault();
    try {
      // Por segurança, só o usuário é lembrado no navegador — nunca a senha.
      if (lembrar) localStorage.setItem(REMEMBER_KEY, usuario.trim());
      else localStorage.removeItem(REMEMBER_KEY);
    } catch {}
    onSubmit({
      usuario: usuario.trim(),
      senha,
      modo,
      fazenda: modo === "zeradas" ? fazenda || undefined : undefined,
      zona: modo === "zeradas" ? zona || undefined : undefined,
      talhao: modo === "zeradas" ? talhao || undefined : undefined,
    });
  };

  const onlyDigits = (set: (v: string) => void) => (e: React.ChangeEvent<HTMLInputElement>) =>
    set(e.target.value.replace(/\D/g, ""));

  return (
    <form onSubmit={submit} className="card divide-y divide-slate-200 dark:divide-slate-800">
      <section className="p-5">
        <h2 className="mb-4 flex items-center gap-2 text-sm font-semibold">
          <KeyRound className="h-4 w-4 text-brand-500" /> Credenciais SGPA
        </h2>
        <div className="space-y-3">
          <div>
            <label className="label" htmlFor="usuario">Usuário</label>
            <input id="usuario" className="input" autoComplete="username" value={usuario}
              onChange={(e) => setUsuario(e.target.value)} disabled={disabled} required />
          </div>
          <div>
            <label className="label" htmlFor="senha">Senha</label>
            <div className="relative">
              <input id="senha" className="input pr-10" type={mostrar ? "text" : "password"}
                autoComplete="current-password" value={senha} onChange={(e) => setSenha(e.target.value)}
                disabled={disabled} required />
              <button type="button" onClick={() => setMostrar((v) => !v)}
                className="absolute inset-y-0 right-0 flex w-10 items-center justify-center text-slate-400 hover:text-slate-600"
                aria-label={mostrar ? "Ocultar senha" : "Mostrar senha"}>
                {mostrar ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
          </div>
          <label className="flex cursor-pointer items-center gap-2 text-sm text-slate-600 dark:text-slate-300">
            <input type="checkbox" className="h-4 w-4 rounded accent-brand-500" checked={lembrar}
              onChange={(e) => setLembrar(e.target.checked)} />
            Lembrar usuário neste navegador
          </label>
        </div>
      </section>

      <section className="p-5">
        <h2 className="mb-4 flex items-center gap-2 text-sm font-semibold">
          <Layers className="h-4 w-4 text-brand-500" /> Modo de operação
        </h2>
        <div className="grid grid-cols-2 gap-2 rounded-xl bg-slate-100 p-1 dark:bg-slate-800/70" role="radiogroup">
          {([
            ["zeradas", "Zeradas", "Usa os valores informados"],
            ["parciais", "Parciais", "Copia das linhas vizinhas"],
          ] as const).map(([value, title, hint]) => (
            <button key={value} type="button" role="radio" aria-checked={modo === value} disabled={disabled}
              onClick={() => setModo(value)}
              className={`rounded-lg px-3 py-2 text-left transition ${
                modo === value
                  ? "bg-white shadow-sm ring-1 ring-slate-200 dark:bg-slate-900 dark:ring-slate-700"
                  : "text-slate-500 hover:text-slate-700 dark:hover:text-slate-200"
              }`}>
              <div className="text-sm font-semibold">{title}</div>
              <div className="text-xs text-slate-500 dark:text-slate-400">{hint}</div>
            </button>
          ))}
        </div>
      </section>

      {modo === "zeradas" && (
        <section className="animate-fade-in p-5">
          <h2 className="mb-1 flex items-center gap-2 text-sm font-semibold">
            <MapPin className="h-4 w-4 text-brand-500" /> Dados de preenchimento
          </h2>
          <p className="mb-4 text-xs text-slate-500 dark:text-slate-400">Opcionais. Preenchidos nas linhas com valor zerado.</p>
          <div className="grid grid-cols-3 gap-3">
            {([
              ["Fazenda", fazenda, setFazenda],
              ["Zona", zona, setZona],
              ["Talhão", talhao, setTalhao],
            ] as const).map(([lbl, val, set]) => (
              <div key={lbl}>
                <label className="label">{lbl}</label>
                <input className="input" inputMode="numeric" value={val} onChange={onlyDigits(set)} disabled={disabled} placeholder="—" />
              </div>
            ))}
          </div>
        </section>
      )}

      <div className="p-5">
        <button type="submit" className="btn-primary w-full py-3" disabled={disabled || submitting}>
          <Play className="h-4 w-4" />
          {submitting ? "Iniciando..." : "Executar automação"}
        </button>
      </div>
    </form>
  );
}
