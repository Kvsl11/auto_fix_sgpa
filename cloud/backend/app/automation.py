"""
Lógica de automação da Ficha do Operador (SGPA / Solinftec).

Esta é a mesma lógica do `main.py` desktop, reorganizada em uma classe
`AutomacaoFicha` independente de interface gráfica:

- Sem Tkinter / winreg / caminhos do Windows.
- Cada execução tem seu próprio navegador, estado e log (multiusuário).
- Pausar / Continuar / Parar são controlados por `threading.Event`.
- Os logs são enviados a um callback (que o servidor repassa via WebSocket).
"""

from __future__ import annotations

import os
import re
import time
import threading
from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# ---------------------------------------------------------------------------
# URLs e XPATHs (idênticos ao script original)
# ---------------------------------------------------------------------------
URL_LOGIN = os.getenv("SGPA_URL", "https://adecoagro.saas-solinftec.com/#!/login/")

XP = {
    "usuario": "/html/body/div[1]/div/div/div/div/form/fieldset/section[1]/label[2]/input",
    "senha": "/html/body/div[1]/div/div/div/div/form/fieldset/section[2]/label[2]/input",
    "botao_login": "/html/body/div[1]/div/div/div/div/form/footer/button",
    "botao_ferramentas": '//*[@id="left-panel"]/div/nav/ul/li[10]/a',
    "botao_ficha_operador": '//*[@id="left-panel"]/div/nav/ul/li[10]/ul/li[1]/a',
    "inserir": '//*[@id="maintable"]/tbody/tr[1]/td[12]/button',
    "tabela": "/html/body/div[1]/div/div/div/div[3]/div[1]/table/tbody",
    "checkbox": ".//input[@type='checkbox']",
    "checkbox_relativo": "/html/body/div[1]/div/div/div/div[3]/div[1]/table/thead/tr/th[1]/label",
    "fazenda": '//*[@id="fazenda"]',
    "zona": '//*[@id="zona"]',
    "talhao": '//*[@id="talhao"]',
    "botao_alterar": "/html/body/div[1]/div/div/div/div[2]/form/div/div[3]/button",
    "botao_salvar": "/html/body/div[1]/div/div/div/div[3]/div[2]/button[2]",
    "aba": "/html/body/div[1]/div/div/div/div[3]/div[1]/nav/span/ul/li[3]/a",
}
CSS_ROUTER = "div.router-animation-container"


def _err(e: Exception) -> str:
    """Mensagem curta da exceção (sem o stacktrace do Selenium)."""
    if isinstance(e, TimeoutException) and not getattr(e, "msg", None):
        return "tempo de espera esgotado (elemento não encontrado)"
    texto = (getattr(e, "msg", None) or str(e)).split("Stacktrace")[0]
    texto = texto.replace("Message:", "").strip()
    return texto.splitlines()[0] if texto else e.__class__.__name__


class JobCancelled(Exception):
    """Levantada internamente quando o usuário encerra a execução."""


def classificar_nivel(msg: str) -> str:
    """Mesmo critério de cores do log Tkinter original."""
    if msg.startswith(("🟢", "✅")):
        return "success"
    if msg.startswith(("🔴", "❌")):
        return "error"
    if msg.startswith(("🟡", "⚠️")):
        return "warning"
    if msg.startswith(("🔵", "▶️", "⏸️", "⏳", "⏱️")):
        return "info"
    return "default"


@dataclass
class Parametros:
    usuario: str
    senha: str
    modo: str = "zeradas"  # "zeradas" (Tipo 1) | "parciais" (Tipo 2)
    fazenda: Optional[str] = None
    zona: Optional[str] = None
    talhao: Optional[str] = None


@dataclass
class Estatisticas:
    fichas_processadas: int = 0
    linhas_zeradas: int = 0
    checkboxes_marcadas: int = 0
    iniciado_em: Optional[str] = None
    finalizado_em: Optional[str] = None


class AutomacaoFicha:
    """Uma execução isolada da automação (um navegador por execução)."""

    # Estados expostos para o front-end
    STARTING = "starting"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING = "waiting"  # sem fichas: aguardando o usuário clicar "Continuar"
    STOPPING = "stopping"
    FINISHED = "finished"
    ERROR = "error"

    def __init__(
        self,
        params: Parametros,
        on_log: Callable[[dict], None],
        on_status: Callable[[str], None],
        headless: bool = True,
    ) -> None:
        self.params = params
        self._on_log = on_log
        self._on_status = on_status
        self.headless = headless

        self.status = self.STARTING
        self.stats = Estatisticas()
        self.driver: Optional[webdriver.Chrome] = None
        self._driver_lock = threading.Lock()

        # Equivalentes aos globais do script original
        self._executando = threading.Event()  # executando
        self._continuar = threading.Event()  # continuar_execucao
        self._pausa = threading.Event()  # em_pausa
        self._thread: Optional[threading.Thread] = None

    # ------------------------------------------------------------------ log
    def log(self, mensagem: str) -> None:
        print(mensagem, flush=True)
        self._on_log(
            {
                "ts": datetime.now().isoformat(timespec="seconds"),
                "level": classificar_nivel(mensagem),
                "message": mensagem,
            }
        )

    def _set_status(self, status: str) -> None:
        self.status = status
        self._on_status(status)

    # ------------------------------------------------------------ controles
    def start(self) -> None:
        self._executando.set()
        self._continuar.set()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def pausar(self) -> bool:
        if self._executando.is_set() and not self._pausa.is_set():
            self.log("🟡 Botão 'Pausar' pressionado. A execução será pausada.")
            self._pausa.set()
            self._set_status(self.PAUSED)
            self._mostrar_tempo_decorrido()
            return True
        return False

    def continuar(self) -> bool:
        if self._executando.is_set() and not self._continuar.is_set():
            self.log("🔵 Botão 'Continuar' pressionado. Retomando a execução...")
            self._continuar.set()
            self._pausa.clear()
            self._set_status(self.RUNNING)
            return True
        if self._pausa.is_set():
            self.log("🔵 Botão 'Continuar' pressionado. Saindo da pausa...")
            self._pausa.clear()
            self._set_status(self.RUNNING)
            return True
        return False

    def parar(self) -> None:
        if not self._executando.is_set():
            return
        self.log("🔵 Encerrando a execução e fechando o navegador...")
        self._set_status(self.STOPPING)
        self._executando.clear()
        self._continuar.set()
        self._pausa.clear()

    @property
    def ativo(self) -> bool:
        return self._executando.is_set()

    # ------------------------------------------------------ navegador remoto
    def screenshot_png(self) -> Optional[bytes]:
        """Captura a tela do navegador remoto (para a pré-visualização ao vivo)."""
        with self._driver_lock:
            if not self.driver:
                return None
            try:
                return self.driver.get_screenshot_as_png()
            except Exception:
                return None

    def clicar_em(self, x_ratio: float, y_ratio: float) -> bool:
        """Clica em um ponto da página (coordenadas relativas 0..1 da captura)."""
        with self._driver_lock:
            if not self.driver:
                return False
            try:
                return bool(
                    self.driver.execute_script(
                        """
                        const x = arguments[0] * window.innerWidth;
                        const y = arguments[1] * window.innerHeight;
                        const el = document.elementFromPoint(x, y);
                        if (!el) return false;
                        ['mousedown','mouseup','click'].forEach(t =>
                          el.dispatchEvent(new MouseEvent(t, {bubbles: true, clientX: x, clientY: y})));
                        if (el.focus) el.focus();
                        return true;
                        """,
                        x_ratio,
                        y_ratio,
                    )
                )
            except Exception:
                return False

    def digitar(self, texto: str) -> bool:
        """Envia texto ao elemento com foco no navegador remoto."""
        with self._driver_lock:
            if not self.driver:
                return False
            try:
                self.driver.switch_to.active_element.send_keys(texto)
                return True
            except Exception:
                return False

    # --------------------------------------------------------------- driver
    def _iniciar_driver(self) -> webdriver.Chrome:
        opts = Options()
        for arg in (
            "--disable-gpu",
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-software-rasterizer",
            "--window-size=1920,1080",
            "--force-device-scale-factor=1",
            "--lang=pt-BR",
        ):
            opts.add_argument(arg)
        if self.headless:
            opts.add_argument("--headless=new")
        chrome_bin = os.getenv("CHROME_BIN")
        if chrome_bin:
            opts.binary_location = chrome_bin

        self.log("🔵 Preparando navegador na nuvem...")
        ultimo_erro: Optional[Exception] = None
        for tentativa in range(3):
            self._checar_cancelado()
            try:
                driver_path = os.getenv("CHROMEDRIVER_PATH")
                service = Service(driver_path) if driver_path else Service()
                driver = webdriver.Chrome(service=service, options=opts)
                driver.set_window_size(1920, 1080)
                self.log(f"🟢 Navegador iniciado (tentativa {tentativa + 1}/3).")
                return driver
            except Exception as e:  # pragma: no cover - depende do ambiente
                ultimo_erro = e
                self.log(f"⚠️ Erro ao iniciar (Tentativa {tentativa + 1}): {_err(e)}")
                time.sleep(2)
        raise RuntimeError(
            f"❌ Falha definitiva ao abrir o navegador após múltiplas tentativas: {ultimo_erro}"
        )

    def _fechar_driver(self) -> None:
        with self._driver_lock:
            if self.driver:
                try:
                    self.driver.quit()
                except Exception:
                    pass
                self.driver = None

    # ------------------------------------------------------------- esperas
    def _checar_cancelado(self) -> None:
        if not self._executando.is_set():
            raise JobCancelled()

    def _aguardar_continuar(self) -> None:
        """`while not continuar_execucao: sleep` do original."""
        while not self._continuar.is_set():
            self._continuar.wait(0.2)
        self._checar_cancelado()

    def _verificar_pausa(self) -> None:
        if self._pausa.is_set():
            self.log("⏸️ Execução em pausa. Aguardando comando 'Continuar'...")
            while self._pausa.is_set() and self._executando.is_set():
                time.sleep(0.3)
            self._checar_cancelado()
            self.log("▶️ Execução retomada.")

    def _mostrar_tempo_decorrido(self) -> None:
        if self.stats.iniciado_em:
            inicio = datetime.fromisoformat(self.stats.iniciado_em)
            self.log(f"⏳ Tempo total decorrido desde o início: {datetime.now() - inicio}")

    # ------------------------------------------------------ helpers Selenium
    def _aguardar_pagina_carregada(self, timeout: int = 30) -> None:
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            self.log("🟢 Página totalmente carregada.")
        except Exception as e:
            self.log(f"⚠️ Erro ao aguardar o carregamento completo da página: {_err(e)}")

    def _escrever_texto(self, xpath: str, texto: str, timeout: int = 30) -> None:
        try:
            campo = WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located((By.XPATH, xpath))
            )
            campo.clear()
            campo.send_keys(texto)
            self.log(f"🟢 Texto inserido no elemento: {xpath}")
        except Exception as e:
            self.log(f"⚠️ Erro ao escrever no elemento {xpath}: {_err(e)}")

    def _realizar_clique(self, xpath: str, timeout: int = 30) -> None:
        for _ in range(3):
            try:
                el = WebDriverWait(self.driver, timeout).until(
                    EC.element_to_be_clickable((By.XPATH, xpath))
                )
                el.click()
                self.log(f"🟢 Clique realizado no elemento: {xpath}")
                return
            except StaleElementReferenceException:
                self.log("🔴 Stale element reference exception. Tentando re-obter o elemento...")
                time.sleep(1)
            except Exception as e:
                self.log(f"⚠️ Erro ao clicar no elemento {xpath}: {_err(e)}")
                break
        self.log(f"❌ Não foi possível clicar no elemento {xpath} após várias tentativas.")

    def _clicar_com_js(self, xpath: str, timeout: int = 30) -> None:
        try:
            el = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            self.driver.execute_script("arguments[0].click();", el)
            self.log(f"🟢 Clique forçado (JS) realizado no elemento: {xpath}")
        except Exception as e:
            self.log(f"⚠️ Erro ao forçar clique no elemento {xpath}: {_err(e)}")

    def _verifica_e_aguarda_tabela(self, xpath_tabela: str):
        while True:
            self._checar_cancelado()
            try:
                self._aguardar_pagina_carregada()
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, xpath_tabela))
                )
                tabela = self.driver.find_element(By.XPATH, xpath_tabela)
                self.log("🔵 Tabela encontrada.")
                return tabela
            except (NoSuchElementException, TimeoutException):
                self.log("🔴 A tabela não foi encontrada. Aguardando nova entrada...")
                self._aguardar_continuar()

    def _ajustar_abas_se_existirem(self, xpath_aba: str) -> None:
        try:
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath_aba))
            )
            aba = self.driver.find_element(By.XPATH, xpath_aba)
            if aba.is_displayed() and aba.is_enabled():
                aba.click()
                self.log("🟢 Clicado na nova aba.")
                self._aguardar_pagina_carregada()
            else:
                self.log("🔴 A aba não está visível ou não é habilitada para ser clicada.")
        except NoSuchElementException:
            self.log("🔴 A aba não foi encontrada.")
        except Exception as e:
            self.log(f"⚠️ Erro ao tentar interagir com a aba: {_err(e)}")

    def _aguardar_linhas_carregadas(self, xpath_tabela: str, timeout: int = 30) -> None:
        try:
            WebDriverWait(self.driver, timeout).until(
                lambda d: len(d.find_elements(By.XPATH, xpath_tabela + "/tr")) > 0
            )
            self.log("🟢 Linhas da tabela carregadas.")
        except TimeoutException:
            self.log("⚠️ Linhas da tabela não carregaram a tempo.")

    def _obter_valor_da_celula(self, linha, coluna_index: int) -> Optional[float]:
        celulas = linha.find_elements(By.TAG_NAME, "td")
        if coluna_index >= len(celulas):
            return None
        texto = re.sub(r"\s+", "", celulas[coluna_index].text)
        if texto == "":
            return None
        try:
            return float(texto)
        except ValueError:
            self.log(f"❌ Erro ao converter valor da célula para float: '{texto}'")
            return None

    def _localizar_valores_maior_que_zero(self, linhas, coluna_index, linha_atual_index):
        for i in range(linha_atual_index - 1, -1, -1):
            v = self._obter_valor_da_celula(linhas[i], coluna_index)
            if v is not None and v > 0:
                return v
        for i in range(linha_atual_index + 1, len(linhas)):
            v = self._obter_valor_da_celula(linhas[i], coluna_index)
            if v is not None and v > 0:
                return v
        return None

    def _preencher(self, xpath: str, valor, nome: str) -> None:
        campo = self.driver.find_element(By.XPATH, xpath)
        campo.clear()
        self.driver.find_element(By.XPATH, xpath).send_keys(str(int(float(valor))))
        self.log(f"✅ Valor de {nome} {valor} inserido.")

    def _clicar_alterar(self) -> None:
        try:
            el = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, XP["botao_alterar"]))
            )
            self.driver.execute_script("arguments[0].scrollIntoView();", el)
            self.driver.execute_script("arguments[0].click();", el)
            self.log("🟢 Clique realizado no botão Alterar.")
        except Exception as e:
            self.log(f"⚠️ Erro ao clicar no botão Alterar: {_err(e)}")

    # ---------------------------------------------- lógica Tipo 1 / Tipo 2
    def _clicar_nas_checkboxes(self) -> tuple[bool, int]:
        """
        Tipo 1 ("zeradas"): usa Fazenda/Zona/Talhão informados pelo usuário.
        Tipo 2 ("parciais"): busca valores > 0 em linhas adjacentes.
        (Mantém exatamente os seletores usados por cada modo no original.)
        """
        parciais = self.params.modo == "parciais"
        xpath_cb = XP["checkbox"] if parciais else XP["checkbox_relativo"]
        clicadas = 0
        zeradas = 0

        def processar(linhas) -> None:
            nonlocal clicadas, zeradas
            for idx, linha in enumerate(linhas):
                try:
                    self._aguardar_continuar()
                    celulas = linha.find_elements(By.TAG_NAME, "td")
                    if len(celulas) < 7:
                        self.log(f"⚠️ Linha {idx} não possui células suficientes, ignorando.")
                        continue
                    vf = self._obter_valor_da_celula(linha, 4)
                    vz = self._obter_valor_da_celula(linha, 5)
                    vt = self._obter_valor_da_celula(linha, 6)
                    if not (vf == 0 or vz == 0 or vt == 0):
                        continue

                    zeradas += 1
                    self.stats.linhas_zeradas += 1
                    self.log(
                        f"✅ Valor encontrado como 0 na linha {idx}. Total de linhas zeradas: {zeradas}"
                    )
                    try:
                        cb = celulas[0].find_element(By.XPATH, xpath_cb)
                        if not (cb.is_displayed() and cb.is_enabled() and not cb.is_selected()):
                            continue
                        cb.click()
                        clicadas += 1
                        self.stats.checkboxes_marcadas += 1
                        self.log(f"✅ Checkbox clicada na linha {idx}.")

                        if parciais:
                            valores = [
                                self._localizar_valores_maior_que_zero(linhas, c, idx)
                                for c in (4, 5, 6)
                            ]
                        else:
                            valores = [
                                self.params.fazenda or None,
                                self.params.zona or None,
                                self.params.talhao or None,
                            ]

                        for valor, campo, nome in zip(
                            valores, ("fazenda", "zona", "talhao"), ("Fazenda", "Zona", "Talhão")
                        ):
                            if valor is not None:
                                self._preencher(XP[campo], valor, nome)
                            if parciais:
                                self._verificar_pausa()

                        self._clicar_alterar()
                    except JobCancelled:
                        raise
                    except NoSuchElementException:
                        self.log(f"❌ Checkbox não encontrada na linha {idx}.")
                    except Exception as e:
                        self.log(f"⚠️ Erro inesperado ao clicar na checkbox: {_err(e)}")
                except JobCancelled:
                    raise
                except Exception as e:
                    self.log(f"⚠️ Erro ao processar a linha {idx}: {_err(e)}")

        try:
            self._aguardar_linhas_carregadas(XP["tabela"])
            linhas = self.driver.find_element(By.XPATH, XP["tabela"]).find_elements(By.XPATH, ".//tr")
            if not linhas:
                self.log("🔴 A tabela não contém linhas.")
                return False, 0
            processar(linhas)
            self.log(f"🔵 Total de linhas com valores zerados: {zeradas}")
            self._ajustar_abas_se_existirem(XP["aba"])
            self._aguardar_linhas_carregadas(XP["tabela"])
            linhas = self.driver.find_element(By.XPATH, XP["tabela"]).find_elements(By.XPATH, ".//tr")
            if linhas:
                processar(linhas)
            return clicadas > 0, zeradas
        except JobCancelled:
            raise
        except TimeoutException:
            self.log("⚠️ Erro: A tabela não foi encontrada a tempo.")
            return False, zeradas
        except Exception as e:
            self.log(f"⚠️ Erro ao localizar a tabela ou processar linhas: {_err(e)}")
            return False, zeradas

    def _aguardar_transicao_salvar(self) -> None:
        script = (
            "return arguments[0].classList.contains('active') && "
            "getComputedStyle(arguments[0]).overflow === 'hidden';"
        )
        try:
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, CSS_ROUTER))
            )
            WebDriverWait(self.driver, 30).until(
                lambda d: d.execute_script(script, d.find_element(By.CSS_SELECTOR, CSS_ROUTER))
            )
            self.log("🔴 O elemento está hidden. Aguardando para ficar visível novamente...")
            WebDriverWait(self.driver, 30).until(
                lambda d: not d.execute_script(script, d.find_element(By.CSS_SELECTOR, CSS_ROUTER))
            )
            self.log("🟢 O elemento está visível novamente. Prosseguindo...")
        except TimeoutException:
            self.log("⚠️ Tempo de espera esgotado! O elemento não foi encontrado na tela.")
        except Exception as e:
            self.log(f"⚠️ Erro inesperado ao verificar o elemento: {_err(e)}")

    # ---------------------------------------------------------- fluxo main
    def _run(self) -> None:
        self.stats.iniciado_em = datetime.now().isoformat(timespec="seconds")
        self._set_status(self.STARTING)
        erro = False
        try:
            driver = self._iniciar_driver()
            with self._driver_lock:
                self.driver = driver
            self._set_status(self.RUNNING)

            self.log("🔵 Acessando o portal Adecoagro...")
            self.driver.get(URL_LOGIN)
            self._aguardar_pagina_carregada()
            WebDriverWait(self.driver, 20).until(
                EC.visibility_of_element_located((By.XPATH, XP["usuario"]))
            )
            self._escrever_texto(XP["usuario"], self.params.usuario)
            self._escrever_texto(XP["senha"], self.params.senha)
            self._clicar_com_js(XP["botao_login"])
            self._clicar_com_js(XP["botao_ferramentas"])
            self._clicar_com_js(XP["botao_ficha_operador"])

            while self._executando.is_set():
                self._verificar_pausa()
                try:
                    if not self.driver.find_elements(By.XPATH, XP["inserir"]):
                        self.log(
                            "🔴 Não há mais elementos para inserir. Aguardando continuação da execução..."
                        )
                        self._continuar.clear()
                        self._set_status(self.WAITING)
                        self._aguardar_continuar()
                        self.log("🔵 Prosseguindo com a execução...")
                        self._set_status(self.RUNNING)
                        continue

                    self._clicar_com_js(XP["inserir"])
                    self._aguardar_pagina_carregada()
                    self._verifica_e_aguarda_tabela(XP["tabela"])
                    self._verificar_pausa()
                    self._clicar_nas_checkboxes()
                    self._verificar_pausa()
                    self._realizar_clique(XP["botao_salvar"])
                    self._aguardar_pagina_carregada()
                    self._aguardar_transicao_salvar()
                    self.stats.fichas_processadas += 1
                    self.log(f"🟢 Ficha #{self.stats.fichas_processadas} salva.")
                except JobCancelled:
                    raise
                except Exception as e:
                    self.log(f"⚠️ Erro durante o processo: {_err(e)}")
                    erro = True
                    break
        except JobCancelled:
            pass
        except Exception as e:
            erro = True
            self.log("🔴 Erro Crítico: Falha ao iniciar o WebDriver.")
            self.log(f"🔴 Detalhes do erro: {_err(e)}")
        finally:
            self._executando.clear()
            self._fechar_driver()
            self.stats.finalizado_em = datetime.now().isoformat(timespec="seconds")
            self._mostrar_tempo_decorrido()
            self.log("🔵 Execução finalizada.")
            self._set_status(self.ERROR if erro else self.FINISHED)
