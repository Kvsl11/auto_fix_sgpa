"""API web do AUTO. FICHA - OPE.

Rotas principais
  POST /api/auth/login            -> token de acesso ao painel (se APP_PASSWORD definido)
  GET  /api/system                -> versão, status remoto (config.json), limites
  POST /api/jobs                  -> inicia uma execução
  GET  /api/jobs                  -> lista execuções
  GET  /api/jobs/{id}             -> detalhes + log
  POST /api/jobs/{id}/pause       -> pausar
  POST /api/jobs/{id}/continue    -> continuar
  POST /api/jobs/{id}/stop        -> encerrar e fechar o navegador
  GET  /api/jobs/{id}/screenshot  -> imagem PNG do navegador remoto
  POST /api/jobs/{id}/click       -> clique remoto (x, y relativos)
  POST /api/jobs/{id}/type        -> digitação remota
  WS   /api/jobs/{id}/ws          -> logs / status / estatísticas em tempo real
"""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal, Optional

import httpx
from fastapi import Depends, FastAPI, Header, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .automation import Parametros
from .jobs import JobManager

# ---------------------------------------------------------------- config
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
SECRET_KEY = os.getenv("SECRET_KEY") or hashlib.sha256(
    (APP_PASSWORD or "dev").encode() + b"auto-ficha"
).hexdigest()
TOKEN_TTL = int(os.getenv("TOKEN_TTL_HOURS", "12")) * 3600
CONFIG_URL = os.getenv(
    "REMOTE_CONFIG_URL",
    "https://raw.githubusercontent.com/Kvsl11/auto_fix_sgpa/main/config.json",
)
CONFIG_POLL_SECONDS = int(os.getenv("REMOTE_CONFIG_POLL_SECONDS", "15"))
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT_JOBS", "2"))
HEADLESS = os.getenv("HEADLESS", "1") != "0"
CORS_ORIGINS = [o.strip() for o in os.getenv("CORS_ORIGINS", "*").split(",") if o.strip()]
FRONTEND_DIST = Path(os.getenv("FRONTEND_DIST", Path(__file__).resolve().parents[2] / "frontend" / "dist"))

manager = JobManager(max_concurrent=MAX_CONCURRENT, headless=HEADLESS)
remote_config: dict = {"version": "web", "status": True, "message": ""}


# ------------------------------------------------------- monitor remoto
async def monitorar_config() -> None:
    """Mesmo papel do `monitorar_config` do desktop: trava remota via config.json."""
    global remote_config
    async with httpx.AsyncClient(timeout=10) as client:
        while True:
            try:
                r = await client.get(CONFIG_URL, headers={"Cache-Control": "no-cache"})
                remote_config = r.json()
                if not remote_config.get("status", True):
                    if not manager.bloqueado:
                        manager.bloquear(
                            remote_config.get("message", "O sistema foi desativado pelo administrador.")
                        )
                elif manager.bloqueado:
                    manager.desbloquear()
            except Exception as e:  # rede indisponível: mantém último estado
                print(f"⚠️ Falha ao consultar config.json: {e}", flush=True)
            await asyncio.sleep(CONFIG_POLL_SECONDS)


@asynccontextmanager
async def lifespan(_: FastAPI):
    task = asyncio.create_task(monitorar_config()) if CONFIG_URL else None
    yield
    if task:
        task.cancel()
    for job in manager.ativos():
        job.automacao.parar()


app = FastAPI(title="AUTO. FICHA - OPE", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ------------------------------------------------------------------ auth
def _assinar(exp: int) -> str:
    sig = hmac.new(SECRET_KEY.encode(), str(exp).encode(), hashlib.sha256).hexdigest()
    return f"{exp}.{sig}"


def _token_valido(token: Optional[str]) -> bool:
    if not APP_PASSWORD:
        return True
    if not token or "." not in token:
        return False
    exp_s, _ = token.split(".", 1)
    try:
        exp = int(exp_s)
    except ValueError:
        return False
    return exp > time.time() and hmac.compare_digest(_assinar(exp), token)


def exigir_auth(authorization: Optional[str] = Header(default=None)) -> None:
    token = authorization.removeprefix("Bearer ").strip() if authorization else None
    if not _token_valido(token):
        raise HTTPException(status_code=401, detail="Não autorizado")


class LoginIn(BaseModel):
    password: str


@app.post("/api/auth/login")
def login(body: LoginIn):
    if APP_PASSWORD and not hmac.compare_digest(body.password, APP_PASSWORD):
        raise HTTPException(status_code=401, detail="Senha de acesso inválida")
    return {"token": _assinar(int(time.time()) + TOKEN_TTL), "expires_in": TOKEN_TTL}


# --------------------------------------------------------------- sistema
@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/system")
def system_info():
    return {
        "auth_required": bool(APP_PASSWORD),
        "version": remote_config.get("version", "web"),
        "bloqueado": manager.bloqueado,
        "mensagem": manager.mensagem_bloqueio,
        "max_concurrent": manager.max_concurrent,
        "ativos": len(manager.ativos()),
    }


# ------------------------------------------------------------------ jobs
class JobIn(BaseModel):
    usuario: str = Field(min_length=1)
    senha: str = Field(min_length=1)
    modo: Literal["zeradas", "parciais"] = "zeradas"
    fazenda: Optional[str] = Field(default=None, pattern=r"^\d*$")
    zona: Optional[str] = Field(default=None, pattern=r"^\d*$")
    talhao: Optional[str] = Field(default=None, pattern=r"^\d*$")


class ClickIn(BaseModel):
    x: float = Field(ge=0, le=1)
    y: float = Field(ge=0, le=1)


class TypeIn(BaseModel):
    text: str = Field(max_length=500)


def _job_or_404(job_id: str):
    job = manager.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Execução não encontrada")
    return job


@app.post("/api/jobs", dependencies=[Depends(exigir_auth)])
async def criar_job(body: JobIn):
    try:
        job = manager.criar(Parametros(**body.model_dump()), asyncio.get_running_loop())
    except PermissionError as e:
        raise HTTPException(status_code=423, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=429, detail=str(e))
    return job.snapshot()


@app.get("/api/jobs", dependencies=[Depends(exigir_auth)])
def listar_jobs():
    return sorted((j.snapshot() for j in manager.jobs.values()), key=lambda j: j["created_at"], reverse=True)


@app.get("/api/jobs/{job_id}", dependencies=[Depends(exigir_auth)])
def detalhe_job(job_id: str):
    return _job_or_404(job_id).snapshot(with_logs=True)


@app.post("/api/jobs/{job_id}/pause", dependencies=[Depends(exigir_auth)])
def pausar(job_id: str):
    _job_or_404(job_id).automacao.pausar()
    return {"ok": True}


@app.post("/api/jobs/{job_id}/continue", dependencies=[Depends(exigir_auth)])
def continuar(job_id: str):
    _job_or_404(job_id).automacao.continuar()
    return {"ok": True}


@app.post("/api/jobs/{job_id}/stop", dependencies=[Depends(exigir_auth)])
def parar(job_id: str):
    _job_or_404(job_id).automacao.parar()
    return {"ok": True}


@app.get("/api/jobs/{job_id}/screenshot")
async def screenshot(job_id: str, token: Optional[str] = Query(default=None)):
    # <img src> não envia header Authorization -> token via query string
    if not _token_valido(token):
        raise HTTPException(status_code=401, detail="Não autorizado")
    png = await asyncio.to_thread(_job_or_404(job_id).automacao.screenshot_png)
    if not png:
        return Response(status_code=204)
    return Response(content=png, media_type="image/png", headers={"Cache-Control": "no-store"})


@app.post("/api/jobs/{job_id}/click", dependencies=[Depends(exigir_auth)])
async def clicar(job_id: str, body: ClickIn):
    ok = await asyncio.to_thread(_job_or_404(job_id).automacao.clicar_em, body.x, body.y)
    return {"ok": ok}


@app.post("/api/jobs/{job_id}/type", dependencies=[Depends(exigir_auth)])
async def digitar(job_id: str, body: TypeIn):
    ok = await asyncio.to_thread(_job_or_404(job_id).automacao.digitar, body.text)
    return {"ok": ok}


@app.websocket("/api/jobs/{job_id}/ws")
async def job_ws(ws: WebSocket, job_id: str, token: Optional[str] = Query(default=None)):
    if not _token_valido(token):
        await ws.close(code=4401)
        return
    job = manager.get(job_id)
    if not job:
        await ws.close(code=4404)
        return
    await ws.accept()
    queue = job.subscribe()
    try:
        await ws.send_json({"type": "snapshot", "data": job.snapshot(with_logs=True)})
        while True:
            event = await queue.get()
            await ws.send_json(event)
    except WebSocketDisconnect:
        pass
    finally:
        job.unsubscribe(queue)


# ------------------------------------------------------ front-end (SPA)
if FRONTEND_DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    def spa(full_path: str):
        alvo = FRONTEND_DIST / full_path
        if full_path and alvo.is_file() and FRONTEND_DIST in alvo.resolve().parents:
            return FileResponse(alvo)
        return FileResponse(FRONTEND_DIST / "index.html")
