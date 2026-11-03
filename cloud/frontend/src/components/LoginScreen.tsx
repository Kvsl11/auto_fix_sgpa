import { FormEvent, useState } from "react";
import { Lock, ShieldCheck } from "lucide-react";
import { api, token } from "../lib/api";

export function LoginScreen({ onLogged }: { onLogged: () => void }) {
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const r = await api.login(password);
      token.set(r.token);
      onLogged();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha no login");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-50 via-slate-50 to-slate-100 px-4 dark:from-slate-950 dark:via-slate-950 dark:to-brand-900/30">
      <form onSubmit={submit} className="card w-full max-w-sm animate-fade-in p-8">
        <div className="mx-auto mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-brand-500 text-white shadow-lg shadow-brand-500/30">
          <ShieldCheck className="h-6 w-6" />
        </div>
        <h1 className="text-center text-xl font-semibold">Auto Ficha OPE</h1>
        <p className="mb-6 mt-1 text-center text-sm text-slate-500 dark:text-slate-400">Informe a senha de acesso ao painel</p>
        <div className="relative">
          <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input type="password" className="input pl-9" placeholder="Senha de acesso" autoFocus
            value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        {error && <p className="mt-3 text-sm text-red-600">{error}</p>}
        <button className="btn-primary mt-5 w-full" disabled={loading || !password}>{loading ? "Entrando..." : "Entrar"}</button>
      </form>
    </div>
  );
}
