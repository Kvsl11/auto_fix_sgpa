"""Gerenciador de execuções: guarda estado, histórico de log e repassa eventos
das threads de automação para os WebSockets (asyncio) conectados."""

from __future__ import annotations

import asyncio
import threading
import uuid
from collections import deque
from dataclasses import asdict
from datetime import datetime
from typing import Optional

from .automation import AutomacaoFicha, Parametros

MAX_LOG = 2000


class Job:
    def __init__(self, params: Parametros, headless: bool, loop: asyncio.AbstractEventLoop):
        self.id = uuid.uuid4().hex[:12]
        self.created_at = datetime.now().isoformat(timespec="seconds")
        self.usuario = params.usuario
        self.modo = params.modo
        self.logs: deque[dict] = deque(maxlen=MAX_LOG)
        self._subs: set[asyncio.Queue] = set()
        self._lock = threading.Lock()
        self._loop = loop
        self.automacao = AutomacaoFicha(
            params, on_log=self._on_log, on_status=self._on_status, headless=headless
        )

    # chamados a partir da thread da automação --------------------------
    def _publish(self, event: dict) -> None:
        with self._lock:
            subs = list(self._subs)
        for q in subs:
            self._loop.call_soon_threadsafe(q.put_nowait, event)

    def _on_log(self, entry: dict) -> None:
        self.logs.append(entry)
        self._publish({"type": "log", "data": entry})
        # estatísticas mudam junto com os logs
        self._publish({"type": "stats", "data": asdict(self.automacao.stats)})

    def _on_status(self, status: str) -> None:
        self._publish({"type": "status", "data": status})

    # assinatura de WebSocket ------------------------------------------
    def subscribe(self) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        with self._lock:
            self._subs.add(q)
        return q

    def unsubscribe(self, q: asyncio.Queue) -> None:
        with self._lock:
            self._subs.discard(q)

    def snapshot(self, with_logs: bool = False) -> dict:
        data = {
            "id": self.id,
            "created_at": self.created_at,
            "usuario": self.usuario,
            "modo": self.modo,
            "status": self.automacao.status,
            "ativo": self.automacao.ativo,
            "stats": asdict(self.automacao.stats),
        }
        if with_logs:
            data["logs"] = list(self.logs)
        return data


class JobManager:
    def __init__(self, max_concurrent: int, headless: bool):
        self.jobs: dict[str, Job] = {}
        self.max_concurrent = max_concurrent
        self.headless = headless
        self.bloqueado = False
        self.mensagem_bloqueio = ""

    def ativos(self) -> list[Job]:
        return [j for j in self.jobs.values() if j.automacao.ativo]

    def criar(self, params: Parametros, loop: asyncio.AbstractEventLoop) -> Job:
        if self.bloqueado:
            raise PermissionError(self.mensagem_bloqueio or "Sistema bloqueado pelo administrador.")
        if len(self.ativos()) >= self.max_concurrent:
            raise RuntimeError(
                f"Limite de {self.max_concurrent} execução(ões) simultânea(s) atingido."
            )
        job = Job(params, self.headless, loop)
        self.jobs[job.id] = job
        job.automacao.start()
        return job

    def get(self, job_id: str) -> Optional[Job]:
        return self.jobs.get(job_id)

    def bloquear(self, mensagem: str) -> None:
        self.bloqueado = True
        self.mensagem_bloqueio = mensagem
        for job in self.ativos():
            job.automacao.log("🔴 Sistema bloqueado remotamente.")
            job.automacao.parar()

    def desbloquear(self) -> None:
        self.bloqueado = False
        self.mensagem_bloqueio = ""
