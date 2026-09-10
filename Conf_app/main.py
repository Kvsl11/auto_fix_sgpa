import threading
import tkinter as tk
from tkinter import messagebox
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException
import re
import time
import json
from datetime import datetime
import customtkinter as ctk
import os
import ssl
import subprocess
import urllib.request
import logging
import sys
import requests
import webbrowser
import winreg  # Adicionado para ler a versão do Chrome no Windows
import shutil  # Adicionado para limpar cache do ChromeDriver

# --- Verifica e usa Python interno automaticamente ---
app_dir = os.path.dirname(os.path.abspath(__file__))
python_exe = os.path.join(app_dir, "Python313", "python.exe")

# Se o script não estiver rodando pelo Python interno, relança com ele
if "Python313" not in sys.executable and os.path.exists(python_exe):
    print("🟢 Usando Python interno (embutido na pasta)...")
    subprocess.run([python_exe, os.path.abspath(__file__)])
    sys.exit(0)

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Bypass SSL universal (urllib + requests)
ssl._create_default_https_context = ssl._create_unverified_context
requests.packages.urllib3.disable_warnings()

# Certificado Amazon Root
AMAZON_CERTS = {
    "Amazon Root CA 1": "https://www.amazontrust.com/repository/AmazonRootCA1.pem"
}

def atualizar_certifi():
    """Atualiza o pacote certifi usando o Python interno."""
    try:
        if not os.path.exists(python_exe):
            logger.warning(f"⚠️ Python interno não encontrado em: {python_exe}")
            return
        logger.info("🔍 Verificando e atualizando pacote certifi...")
        subprocess.run([python_exe, "-m", "pip", "install", "--upgrade", "certifi"], check=True)
        import certifi
        logger.info(f"🟢 Certifi atualizado com sucesso: {certifi.where()}")
    except Exception as e:
        logger.warning(f"⚠️ Falha ao atualizar certifi: {e}")

def garantir_certificados_amazon():
    """Garante que o Amazon Root CA 1 esteja presente no cacert.pem."""
    try:
        import certifi
        cacert_path = certifi.where()
        with open(cacert_path, "r", encoding="utf-8") as f:
            conteudo = f.read()

        if "Amazon Root CA 1" not in conteudo:
            logger.info("🔍 Amazon Root CA 1 não encontrado — baixando...")
            resp = requests.get(AMAZON_CERTS["Amazon Root CA 1"], timeout=10, verify=False)
            if resp.status_code == 200:
                with open(cacert_path, "a", encoding="utf-8") as f:
                    f.write(f"\n# Amazon Root CA 1\n{resp.text.strip()}\n")
                logger.info("✅ Certificado Amazon Root CA 1 adicionado com sucesso.")
            else:
                logger.warning(f"❌ Falha ao baixar certificado Amazon: {resp.status_code}")
        else:
            logger.info("🟢 Amazon Root CA 1 já está presente.")
    except Exception as e:
        logger.warning(f"⚠️ Falha ao garantir certificados: {e}")

def testar_ssl():
    """Verifica se há conectividade SSL, aplica fallback se falhar."""
    try:
        import certifi
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        urllib.request.urlopen("https://www.google.com", timeout=5, context=ssl_context)
        logger.info("🟢 Conexão SSL validada com sucesso.")
    except ssl.SSLError as e:
        logger.warning(f"⚠️ Falha SSL detectada ({e}). Aplicando modo não verificado.")
        ssl._create_default_https_context = ssl._create_unverified_context
        try:
            urllib.request.urlopen("https://www.google.com", timeout=5)
            logger.info("🟡 SSL desativado — conexão forçada sem verificação de certificado.")
        except Exception as e2:
            logger.error(f"❌ Mesmo após fallback, falhou: {e2}")
    except Exception as e:
        logger.warning(f"⚠️ Erro genérico ao testar SSL: {e}. Aplicando fallback.")
        ssl._create_default_https_context = ssl._create_unverified_context

# Execução automática de configuração SSL
logger.info("🚀 Iniciando verificação e correção SSL híbrida...")
atualizar_certifi()
garantir_certificados_amazon()
testar_ssl()
logger.info("✅ Configuração SSL concluída com segurança.")

<<<<<<< HEAD:Conf_app/App_py/main.py
# --- VERIFICAÇÃO DE SEGURANÇA VIA GITHUB ---
VERSAO = "4.6.2"

def exibir_erro_fatal(titulo, mensagem):
    """Exibe uma janela de erro travada na tela e fecha o programa."""
    root_temp = tk.Tk()
    root_temp.withdraw()
    root_temp.attributes("-topmost", True) # Garante que a mensagem apareça em cima de tudo
    messagebox.showerror(titulo, mensagem)
    root_temp.destroy()
    os._exit(1)

def verificar_seguranca():
    """
    Verifica a trava de segurança (status.txt).
    Bloqueia o app caso esteja desativado remotamente.
    """
=======
def obter_versao_local():
>>>>>>> b8c1a5b92c7d514eca96179d2b1be171bbf5d871:Conf_app/main.py
    try:
        caminho_versao = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "version_local.txt"
        )

        if os.path.exists(caminho_versao):
            with open(
                caminho_versao,
                "r",
                encoding="utf-8"
            ) as f:
                return f.read().strip()

<<<<<<< HEAD:Conf_app/App_py/main.py
        # 1. VERIFICAR A TRAVA DE SEGURANÇA (KILL SWITCH)
        try:
            headers = {"Cache-Control": "no-cache, no-store, must-revalidate", "Pragma": "no-cache"}
            r_status = requests.get(URL_STATUS, timeout=10, verify=False, headers=headers)
            if r_status.status_code == 200:
                status_app = r_status.text.strip().lower()
                if status_app == "false":
                    logger.warning("🔴 TRAVA ATIVADA VIA GITHUB! Bloqueando acesso.")
                    file_logger.warning("🔴 TRAVA ATIVADA VIA GITHUB! Bloqueando acesso.")
                    exibir_erro_fatal("Erro Crítico de Comunicação", "Ocorreu uma falha inesperada ao sincronizar as configurações iniciais do sistema.\n\nCódigo do Erro: ERR_CONNECTION_REFUSED_10061\nPor favor, tente novamente mais tarde.")
            else:
                logger.info(f"⚠️ Status remoto retornou código {r_status.status_code}. Execução permitida.")
        except Exception as e:
            logger.warning(f"⚠️ Falha ao checar status.txt (Internet/GitHub fora do ar). Ignorando trava. Erro: {e}")
            file_logger.warning(f"⚠️ Falha ao checar status.txt (Internet/GitHub fora do ar). Ignorando trava. Erro: {e}")
=======
    except Exception:
        pass
>>>>>>> b8c1a5b92c7d514eca96179d2b1be171bbf5d871:Conf_app/main.py

    return "0.0.0"

<<<<<<< HEAD:Conf_app/App_py/main.py
=======

VERSAO = obter_versao_local()

>>>>>>> b8c1a5b92c7d514eca96179d2b1be171bbf5d871:Conf_app/main.py
# Variáveis globais
executando = False
continuar_execucao = False
em_pausa = False
driver = None
tempo_inicio_ficha = None
tempo_decorrido_inicio = None

# Global UI elements
root = None
log_textbox = None
status_label = None
botao_executar = None
botao_continuar = None
botao_cancelar = None
entry_usuario = None
entry_senha = None
entry_fazenda = None
entry_zona = None
entry_talhao = None
tipo_logica = None

def obter_caminho_imagem(nome_imagem):
    """Obtém o caminho da imagem de forma compatível com o PyInstaller."""
    if getattr(sys, 'frozen', False):
        pasta = sys._MEIPASS
    else:
        pasta = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(pasta, "imagens", nome_imagem)

# --- INÍCIO DAS CORREÇÕES DE ATUALIZAÇÃO DO CHROME ---
def obter_versao_principal_chrome():
    """Detecta a versão principal do Chrome instalada no Windows via Registro."""
    try:
        # Tenta HKEY_CURRENT_USER primeiro
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
        version, _ = winreg.QueryValueEx(key, "version")
        return int(version.split('.')[0])
    except Exception:
        pass
    try:
        # Tenta HKEY_LOCAL_MACHINE como fallback
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"Software\Google\Chrome\BLBeacon")
        version, _ = winreg.QueryValueEx(key, "version")
        return int(version.split('.')[0])
    except Exception:
        return None

def limpar_cache_uc():
    """Limpa a pasta de cache do undetected_chromedriver para evitar drivers zumbis."""
    try:
        # 1. Mata processos zumbis que impedem a limpeza do cache
        if os.name == 'nt':
            os.system("taskkill /f /im undetected_chromedriver.exe /T >nul 2>&1")
            
        # 2. Deleta a pasta de cache
        user_data = os.path.join(os.environ.get('APPDATA', ''), 'undetected_chromedriver')
        if os.path.exists(user_data):
            shutil.rmtree(user_data, ignore_errors=True)
            logger.info("🗑️ Cache de drivers antigos do undetected_chromedriver limpo.")
    except Exception as e:
        logger.warning(f"⚠️ Não foi possível limpar o cache do driver: {e}")
# --- FIM DAS CORREÇÕES DE ATUALIZAÇÃO DO CHROME ---

def iniciar_driver(headless=False, user_data_dir=None):
    """Inicia o WebDriver para o Chrome de forma robusta e limpa."""
    
    chrome_options = Options()

    # --- Configurações essenciais ---
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--kiosk") # Alternativa: Abre em modo totem (F11) se o maximized falhar
    chrome_options.add_argument("--force-device-scale-factor=1") # Evita que o zoom do Windows quebre o layout
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--window-size=1920,1080")

    if headless:
        chrome_options.add_argument("--headless=new")

    if user_data_dir:
        chrome_options.add_argument(f"--user-data-dir={user_data_dir}")

    log_mensagem("🔵 Identificando versão do Chrome e preparando driver...")

    versao_chrome = obter_versao_principal_chrome()

    for tentativa in range(3):
        try:
            limpar_cache_uc()

            # --- Inicialização do driver ---
            if versao_chrome:
                log_mensagem(f"🔍 Chrome v{versao_chrome} detectado. Tentativa {tentativa+1}/3...")
                driver = uc.Chrome(
                    options=chrome_options,
                    version_main=versao_chrome
                )
            else:
                log_mensagem(f"⚠️ Versão não detectada. Tentativa {tentativa+1}/3...")
                driver = uc.Chrome(options=chrome_options)

            # Aguarda o processo do Chrome estabilizar na memória
            time.sleep(2)

            # Apenas foca na janela inicial, sem forçar navegação ou maximização
            if driver.window_handles:
                driver.switch_to.window(driver.window_handles[0])

            return driver

        except Exception as e:
            log_mensagem(f"⚠️ Erro ao iniciar (Tentativa {tentativa+1}): {e}")
            try:
                driver.quit()
            except:
                pass
            time.sleep(2)

    raise Exception("❌ Falha definitiva ao abrir o navegador após múltiplas tentativas.")

def aguardar_pagina_carregada(driver, timeout=30):
    """Espera até que o status de carregamento da página seja 'complete'."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        log_mensagem("🟢 Página totalmente carregada.")
    except Exception as e:
        log_mensagem(f"⚠️ Erro ao aguardar o carregamento completo da página: {e}")

def mostrar_tempo_decorrido():
    """Calcula e exibe o tempo total de execução."""
    global tempo_decorrido_inicio
    if tempo_decorrido_inicio is not None:
        tempo_total_decorrido = datetime.now() - tempo_decorrido_inicio
        log_mensagem(f"⏳ Tempo total decorrido desde o início: {tempo_total_decorrido}")

def escrever_texto(driver, by_type, selector, texto, timeout=30):
    """Insere texto em um campo de entrada."""
    try:
        campo = WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by_type, selector))
        )
        campo.clear()
        campo.send_keys(texto)
        log_mensagem(f"🟢 Texto inserido no elemento: {selector}")
    except Exception as e:
        log_mensagem(f"⚠️ Erro ao escrever no elemento {selector}: {e}")

def realizar_clique(driver, by_type, selector, timeout=30):
    """Clica em um elemento na página, com tentativas de recuperação."""
    attempts = 0
    while attempts < 3:
        try:
            elemento = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((by_type, selector))
            )
            elemento.click()
            log_mensagem(f"🟢 Clique realizado no elemento: {selector}")
            return
        except StaleElementReferenceException:
            log_mensagem("🔴 Stale element reference exception. Tentando re-obter o elemento...")
            attempts += 1
            time.sleep(1)
        except Exception as e:
            log_mensagem(f"⚠️ Erro ao clicar no elemento {selector}: {e}")
            break
    log_mensagem(f"❌ Não foi possível clicar no elemento {selector} após várias tentativas.")

def clicar_com_js(driver, xpath, timeout=30):
    """Realiza um clique forçado usando JavaScript."""
    try:
        elemento = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        driver.execute_script("arguments[0].click();", elemento)
        log_mensagem(f"🟢 Clique forçado (JS) realizado no elemento: {xpath}")
    except Exception as e:
        log_mensagem(f"⚠️ Erro ao forçar clique no elemento {xpath}: {e}")

def verifica_e_aguarda_tabela(driver, xpath_tabela):
    """Verifica a existência de uma tabela e aguarda novas entradas se necessário."""
    while True:
        try:
            aguardar_pagina_carregada(driver)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, xpath_tabela))
            )
            tabela = driver.find_element(By.XPATH, xpath_tabela)
            log_mensagem("🔵 Tabela encontrada.")
            return tabela
        except NoSuchElementException:
            log_mensagem("🔴 A tabela não foi encontrada. Aguardando nova entrada...")
            while not continuar_execucao:
                time.sleep(0.5)

def ajustar_abas_se_existirem(driver, xpath_aba):
    """Clica em uma nova aba se ela estiver presente e ativa."""
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, xpath_aba))
        )
        aba = driver.find_element(By.XPATH, xpath_aba)
        if aba.is_displayed() and aba.is_enabled():
            aba.click()
            log_mensagem("🟢 Clicado na nova aba.")
            aguardar_pagina_carregada(driver)
        else:
            log_mensagem("🔴 A aba não está visível ou não é habilitada para ser clicada.")
    except NoSuchElementException:
        log_mensagem("🔴 A aba não foi encontrada.")
    except Exception as e:
        log_mensagem(f"⚠️ Erro ao tentar interagir com a aba: {e}")

def log_mensagem(mensagem):
    """Loga a mensagem no console e na interface."""
    print(mensagem)
    if log_textbox:
        log_textbox.configure(state="normal")
        
        # Check for prefixes to apply different colors
        if mensagem.startswith("🟢"):
            log_textbox.insert("end", mensagem + "\n", "green_tag")
        elif mensagem.startswith("🔴") or mensagem.startswith("❌"):
            log_textbox.insert("end", mensagem + "\n", "red_tag")
        elif mensagem.startswith("🟡") or mensagem.startswith("⚠️"):
            log_textbox.insert("end", mensagem + "\n", "yellow_tag")
        elif mensagem.startswith("🔵") or mensagem.startswith("▶️") or mensagem.startswith("⏸️") or mensagem.startswith("⏳") or mensagem.startswith("⏱️"):
            log_textbox.insert("end", mensagem + "\n", "blue_tag")
        else:
            log_textbox.insert("end", mensagem + "\n", "default_tag")
        
        log_textbox.see("end")
        log_textbox.configure(state="disabled")

def clicar_nas_checkboxes_tipo_1(driver, xpath_tabela, xpath_checkbox_relativo, xpath_fazenda, xpath_zona, xpath_talhao, xpath_botao_alterar, xpath_aba):
    """
    Clica em checkboxes de uma tabela com base na lógica 'Tipo 1' (valores zerados).
    Usa valores de entrada da interface para preencher os campos.
    """
    checkboxes_clicadas = 0
    linhas_zeradas = 0
    valor_fazenda_input = entry_fazenda.get()
    valor_zona_input = entry_zona.get()
    valor_talhao_input = entry_talhao.get()
    
    def processar_linhas(linhas):
        nonlocal checkboxes_clicadas, linhas_zeradas
        for linha_index, linha in enumerate(linhas):
            try:
                while not continuar_execucao:
                    time.sleep(0.2)
                celulas = linha.find_elements(By.TAG_NAME, "td")
                if len(celulas) < 7:
                    log_mensagem(f"⚠️ Linha {linha_index} não possui células suficientes, ignorando.")
                    continue
                valor_fazenda = obter_valor_da_celula(linha, 4)
                valor_zona = obter_valor_da_celula(linha, 5)
                valor_talhao = obter_valor_da_celula(linha, 6)
                
                if valor_fazenda == 0 or valor_zona == 0 or valor_talhao == 0:
                    linhas_zeradas += 1
                    log_mensagem(f"✅ Valor encontrado como 0 na linha {linha_index}. Total de linhas zeradas: {linhas_zeradas}")
                    try:
                        checkbox = celulas[0].find_element(By.XPATH, xpath_checkbox_relativo)
                        if checkbox.is_displayed() and checkbox.is_enabled() and not checkbox.is_selected():
                            checkbox.click()
                            checkboxes_clicadas += 1
                            log_mensagem(f"✅ Checkbox clicada na linha {linha_index}.")
                            if valor_fazenda_input:
                                driver.find_element(By.XPATH, xpath_fazenda).clear()
                                driver.find_element(By.XPATH, xpath_fazenda).send_keys(str(int(valor_fazenda_input)))
                                log_mensagem(f"✅ Valor de Fazenda {valor_fazenda_input} inserido.")
                            if valor_zona_input:
                                driver.find_element(By.XPATH, xpath_zona).clear()
                                driver.find_element(By.XPATH, xpath_zona).send_keys(str(int(valor_zona_input)))
                                log_mensagem(f"✅ Valor de Zona {valor_zona_input} inserido.")
                            if valor_talhao_input:
                                driver.find_element(By.XPATH, xpath_talhao).clear()
                                driver.find_element(By.XPATH, xpath_talhao).send_keys(str(int(valor_talhao_input)))
                                log_mensagem(f"✅ Valor de Talhão {valor_talhao_input} inserido.")
                                
                            try:
                                elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_botao_alterar)))
                                driver.execute_script("arguments[0].scrollIntoView();", elemento)
                                driver.execute_script("arguments[0].click();", elemento)
                                log_mensagem("🟢 Clique realizado no botão Alterar.")
                            except Exception as e:
                                log_mensagem(f"⚠️ Erro ao clicar no botão Alterar: {e}")
                                
                    except NoSuchElementException:
                        log_mensagem(f"❌ Checkbox não encontrada na linha {linha_index}.")
                    except Exception as e:
                        log_mensagem(f"⚠️ Erro inesperado ao clicar na checkbox: {e}")
            except Exception as e:
                log_mensagem(f"⚠️ Erro ao processar a linha {linha_index}: {e}")

    try:
        aguardar_linhas_carregadas(driver, xpath_tabela)
        tabela = driver.find_element(By.XPATH, xpath_tabela)
        linhas = tabela.find_elements(By.XPATH, ".//tr")
        if not linhas:
            log_mensagem("🔴 A tabela não contém linhas.")
            return False, 0
            
        processar_linhas(linhas)
        log_mensagem(f"🔵 Total de linhas com valores zerados: {linhas_zeradas}")
        ajustar_abas_se_existirem(driver, xpath_aba)
        aguardar_linhas_carregadas(driver, xpath_tabela)
        tabela = driver.find_element(By.XPATH, xpath_tabela)
        linhas = tabela.find_elements(By.XPATH, ".//tr")
        if linhas:
            processar_linhas(linhas)
            
        return checkboxes_clicadas > 0, linhas_zeradas
        
    except TimeoutException:
        log_mensagem("⚠️ Erro: A tabela não foi encontrada a tempo.")
        return False, linhas_zeradas
    except Exception as e:
        log_mensagem(f"⚠️ Erro ao localizar a tabela ou processar linhas: {e}")
        return False, linhas_zeradas

def clicar_nas_checkboxes_tipo_2(driver, xpath_tabela, xpath_checkbox_relativo, xpath_fazenda, xpath_zona, xpath_talhao, xpath_botao_alterar, xpath_aba):
    """
    Clica em checkboxes de uma tabela com base na lógica 'Tipo 2' (valores parciais).
    Busca valores em linhas adjacentes para preencher os campos.
    """
    checkboxes_clicadas = 0
    linhas_zeradas = 0
    
    def processar_linhas(linhas):
        nonlocal checkboxes_clicadas, linhas_zeradas
        for linha_index, linha in enumerate(linhas):
            try:
                while not continuar_execucao:
                    time.sleep(0.2)
                celulas = linha.find_elements(By.TAG_NAME, "td")
                if len(celulas) < 7:
                    log_mensagem(f"⚠️ Linha {linha_index} não possui células suficientes, ignorando.")
                    continue
                valor_fazenda = obter_valor_da_celula(linha, 4)
                valor_zona = obter_valor_da_celula(linha, 5)
                valor_talhao = obter_valor_da_celula(linha, 6)
                
                if valor_fazenda == 0 or valor_zona == 0 or valor_talhao == 0:
                    linhas_zeradas += 1
                    log_mensagem(f"✅ Valor encontrado como 0 na linha {linha_index}. Total de linhas zeradas: {linhas_zeradas}")
                    try:
                        checkbox = celulas[0].find_element(By.XPATH, xpath_checkbox_relativo)
                        if checkbox.is_displayed() and checkbox.is_enabled() and not checkbox.is_selected():
                            checkbox.click()
                            checkboxes_clicadas += 1
                            log_mensagem(f"✅ Checkbox clicada na linha {linha_index}.")
                            
                            valor_fazenda_preencher = localizar_valores_maior_que_zero(linhas, 4, linha_index)
                            valor_zona_preencher = localizar_valores_maior_que_zero(linhas, 5, linha_index)
                            valor_talhao_preencher = localizar_valores_maior_que_zero(linhas, 6, linha_index)
                            
                            if valor_fazenda_preencher is not None:
                                driver.find_element(By.XPATH, xpath_fazenda).clear()
                                driver.find_element(By.XPATH, xpath_fazenda).send_keys(str(int(valor_fazenda_preencher)))
                                log_mensagem(f"✅ Valor de Fazenda {valor_fazenda_preencher} inserido.")
                                
                            verificar_pausa()
                            if valor_zona_preencher is not None:
                                driver.find_element(By.XPATH, xpath_zona).clear()
                                driver.find_element(By.XPATH, xpath_zona).send_keys(str(int(valor_zona_preencher)))
                                log_mensagem(f"✅ Valor de Zona {valor_zona_preencher} inserido.")
                                
                            verificar_pausa()
                            if valor_talhao_preencher is not None:
                                driver.find_element(By.XPATH, xpath_talhao).clear()
                                driver.find_element(By.XPATH, xpath_talhao).send_keys(str(int(valor_talhao_preencher)))
                                log_mensagem(f"✅ Valor de Talhão {valor_talhao_preencher} inserido.")
                                
                            verificar_pausa()
                            try:
                                elemento = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, xpath_botao_alterar)))
                                driver.execute_script("arguments[0].scrollIntoView();", elemento)
                                driver.execute_script("arguments[0].click();", elemento)
                                log_mensagem("🟢 Clique realizado no botão Alterar.")
                            except Exception as e:
                                log_mensagem(f"⚠️ Erro ao clicar no botão Alterar: {e}")
                                
                    except NoSuchElementException:
                        log_mensagem(f"❌ Checkbox não encontrada na linha {linha_index}.")
                    except Exception as e:
                        log_mensagem(f"⚠️ Erro inesperado ao clicar na checkbox: {e}")
            except Exception as e:
                log_mensagem(f"⚠️ Erro ao processar a linha {linha_index}: {e}")
                
    try:
        aguardar_linhas_carregadas(driver, xpath_tabela)
        tabela = driver.find_element(By.XPATH, xpath_tabela)
        linhas = tabela.find_elements(By.XPATH, ".//tr")
        if not linhas:
            log_mensagem("🔴 A tabela não contém linhas.")
            return False, 0
        
        processar_linhas(linhas)
        log_mensagem(f"🔵 Total de linhas com valores zerados: {linhas_zeradas}")
        ajustar_abas_se_existirem(driver, xpath_aba)
        aguardar_linhas_carregadas(driver, xpath_tabela)
        tabela = driver.find_element(By.XPATH, xpath_tabela)
        linhas = tabela.find_elements(By.XPATH, ".//tr")
        if linhas:
            processar_linhas(linhas)
        
        return checkboxes_clicadas > 0, linhas_zeradas
    except TimeoutException:
        log_mensagem("⚠️ Erro: A tabela não foi encontrada a tempo.")
        return False, linhas_zeradas
    except Exception as e:
        log_mensagem(f"⚠️ Erro ao localizar a tabela ou processar linhas: {e}")
        return False, checkboxes_clicadas

def clicar_nas_checkboxes(driver, xpath_tabela, xpath_checkbox, xpath_checkbox_relativo, xpath_fazenda, xpath_zona, xpath_talhao, xpath_botao_alterar, xpath_aba):
    """Escolhe a lógica de clique com base no modo de operação selecionado."""
    if tipo_logica.get() == 'Tipo 1':
        return clicar_nas_checkboxes_tipo_1(driver, xpath_tabela, xpath_checkbox_relativo, xpath_fazenda, xpath_zona, xpath_talhao, xpath_botao_alterar, xpath_aba)
    elif tipo_logica.get() == 'Tipo 2':
        return clicar_nas_checkboxes_tipo_2(driver, xpath_tabela, xpath_checkbox, xpath_fazenda, xpath_zona, xpath_talhao, xpath_botao_alterar, xpath_aba)

def aguardar_linhas_carregadas(driver, xpath_tabela, timeout=30):
    """Espera até que a tabela tenha pelo menos uma linha."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: len(d.find_elements(By.XPATH, xpath_tabela + "/tr")) > 0
        )
        log_mensagem("🟢 Linhas da tabela carregadas.")
    except TimeoutException:
        log_mensagem("⚠️ Linhas da tabela não carregaram a tempo.")

def localizar_valores_maior_que_zero(linhas, coluna_index, linha_atual_index):
    """
    Procura valores não nulos e maiores que zero em linhas adjacentes.
    Primeiro para cima, depois para baixo.
    """
    for i in range(linha_atual_index - 1, -1, -1):
        valor = obter_valor_da_celula(linhas[i], coluna_index)
        if valor is not None and valor > 0:
            return valor
    for i in range(linha_atual_index + 1, len(linhas)):
        valor = obter_valor_da_celula(linhas[i], coluna_index)
        if valor is not None and valor > 0:
            return valor
    return None

def obter_valor_da_celula(linha, coluna_index):
    """Extrai e converte o valor de uma célula para float."""
    celulas = linha.find_elements(By.TAG_NAME, "td")
    if coluna_index < len(celulas):
        texto = re.sub(r"\s+", "", celulas[coluna_index].text)
        if texto == "":
            return None
        try:
            return float(texto)
        except ValueError:
            log_mensagem(f"❌ Erro ao converter valor da célula para float: '{texto}'")
            return None
    else:
        return None

def continuar_execucao_func(event=None):
    """Retoma a execução do script."""
    global continuar_execucao, em_pausa, executando
    if executando and not continuar_execucao:
        log_mensagem("🔵 Botão 'Continuar' pressionado. Retomando a execução...")
        continuar_execucao = True
        em_pausa = False
        atualizar_estado_botoes()
    elif em_pausa:
        log_mensagem("🔵 Botão 'Continuar' pressionado. Saindo da pausa...")
        em_pausa = False
        atualizar_estado_botoes()

def pausar_execucao():
    """Pausa a execução do script."""
    global em_pausa, executando
    if executando and not em_pausa:
        log_mensagem("🟡 Botão 'Pausar' pressionado. A execução será pausada.")
        em_pausa = True
        messagebox.showinfo("Pausado", "A execução foi pausada. Clique em 'Continuar' para retomar.")
        mostrar_tempo_decorrido()
        atualizar_estado_botoes()

def verificar_pausa():
    """Verifica se o script está em estado de pausa e aguarda a retomada."""
    global em_pausa
    if em_pausa:
        log_mensagem("⏸️ Execução em pausa. Aguardando comando 'Continuar'...")
        while em_pausa:
            time.sleep(0.5)
            if not executando:
                break
        log_mensagem("▶️ Execução retomada.")

def executar_script(usuario, senha):
    """Função principal que orquestra a automação."""
    global executando, driver, continuar_execucao, em_pausa, tempo_inicio_ficha, tempo_decorrido_inicio
    executando = True
    continuar_execucao = True
    em_pausa = False
    atualizar_estado_botoes("Executando...")

    try:
        driver = iniciar_driver()
    except Exception as e:
        log_mensagem(f"🔴 Erro Crítico: Falha ao iniciar o WebDriver.")
        log_mensagem(f"🔴 Detalhes do erro: {e}")
        messagebox.showerror("Erro Crítico", f"Não foi possível iniciar o navegador. O programa será encerrado.\n\nDetalhes: {e}")
        executando = False
        atualizar_estado_botoes("Aguardando...")
        return

    try:
        # --- Definições de XPATHs e URLs ---
        url = "https://adecoagro.saas-solinftec.com/#!/login/"
        xpath_usuario = '/html/body/div[1]/div/div/div/div/form/fieldset/section[1]/label[2]/input'
        xpath_senha = '/html/body/div[1]/div/div/div/div/form/fieldset/section[2]/label[2]/input'
        xpath_botao_login = '/html/body/div[1]/div/div/div/div/form/footer/button'
        xpath_botao_ferramentas = '//*[@id="left-panel"]/div/nav/ul/li[10]/a'
        xpath_botao_ficha_operador = '//*[@id="left-panel"]/div/nav/ul/li[10]/ul/li[1]/a'
        xpath_inserir = '//*[@id="maintable"]/tbody/tr[1]/td[12]/button'
        xpath_tabela = "/html/body/div[1]/div/div/div/div[3]/div[1]/table/tbody"
        xpath_checkbox = ".//input[@type='checkbox']"
        xpath_checkbox_relativo = "/html/body/div[1]/div/div/div/div[3]/div[1]/table/thead/tr/th[1]/label"
        xpath_fazenda = '//*[@id="fazenda"]'
        xpath_zona = '//*[@id="zona"]'
        xpath_talhao = '//*[@id="talhao"]'
        xpath_botao_alterar = '/html/body/div[1]/div/div/div/div[2]/form/div/div[3]/button'
        xpath_botao_salvar = '/html/body/div[1]/div/div/div/div[3]/div[2]/button[2]'
        xpath_aba = '/html/body/div[1]/div/div/div/div[3]/div[1]/nav/span/ul/li[3]/a'
        # --- Fim das Definições ---

       # 1. Acessa o site
        log_mensagem("🔵 Acessando o portal Adecoagro...")
        driver.get(url)
        
        # 2. Força o foco e tenta maximizar de várias formas
        time.sleep(2) # Pequena pausa para o SO processar a janela
        try:
            driver.set_window_rect(0, 0, 1920, 1080) # Define um tamanho fixo antes de maximizar
            driver.maximize_window()
            log_mensagem("🟢 Janela maximizada via Selenium.")
        except Exception:
            try:
                # Fallback via JavaScript (Garante que o navegador ocupe a tela)
                driver.execute_script("window.moveTo(0, 0); window.resizeTo(screen.availWidth, screen.availHeight);")
                log_mensagem("🟢 Janela ajustada via JavaScript.")
            except:
                log_mensagem("⚠️ Não foi possível forçar tela cheia, tentando prosseguir assim mesmo.")

        # 3. Aguarda o carregamento antes de tentar o login
        aguardar_pagina_carregada(driver)
        
        # 3.1. Verifica se o campo de usuário está visível antes de escrever
        WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, xpath_usuario)))

        # 3. Segue o fluxo normal de login
        escrever_texto(driver, By.XPATH, xpath_usuario, usuario)
        escrever_texto(driver, By.XPATH, xpath_senha, senha)
        clicar_com_js(driver, xpath_botao_login)
        clicar_com_js(driver, xpath_botao_ferramentas)
        clicar_com_js(driver, xpath_botao_ficha_operador)

        tempo_decorrido_inicio = datetime.now()

        while executando:
            verificar_pausa()
            try:
                elementos_inserir = driver.find_elements(By.XPATH, xpath_inserir)
                if not elementos_inserir:
                    log_mensagem("🔴 Não há mais elementos para inserir. Aguardando continuação da execução...")
                    continuar_execucao = False
                    atualizar_estado_botoes("Aguardando nova entrada...")
                    while not continuar_execucao and executando:
                        time.sleep(0.5)
                    if not executando:
                        break
                    log_mensagem("🔵 Prosseguindo com a execução...")
                    atualizar_estado_botoes("Executando...")
                    continue
                if tempo_inicio_ficha is None:
                    tempo_inicio_ficha = datetime.now()
                clicar_com_js(driver, xpath_inserir)
                aguardar_pagina_carregada(driver)
                tabela = verifica_e_aguarda_tabela(driver, xpath_tabela)
                verificar_pausa()
                clicar_nas_checkboxes(
                    driver, xpath_tabela, xpath_checkbox, xpath_checkbox_relativo,
                    xpath_fazenda, xpath_zona, xpath_talhao,
                    xpath_botao_alterar, xpath_aba
                )
                verificar_pausa()
                realizar_clique(driver, By.XPATH, xpath_botao_salvar)
                aguardar_pagina_carregada(driver)
                css_selector_elemento = "div.router-animation-container"
                try:
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, css_selector_elemento))
                    )
                    WebDriverWait(driver, 30).until(
                        lambda d: d.execute_script("return arguments[0].classList.contains('active') && getComputedStyle(arguments[0]).overflow === 'hidden';",
                        driver.find_element(By.CSS_SELECTOR, css_selector_elemento))
                    )
                    log_mensagem("🔴 O elemento está hidden. Aguardando para ficar visível novamente...")
                    WebDriverWait(driver, 30).until(
                        lambda d: not d.execute_script("return arguments[0].classList.contains('active') && getComputedStyle(arguments[0]).overflow === 'hidden';",
                        driver.find_element(By.CSS_SELECTOR, css_selector_elemento))
                    )
                    log_mensagem("🟢 O elemento está visível novamente. Prosseguindo...")
                except TimeoutException:
                    log_mensagem("⚠️ Tempo de espera esgotado! O elemento não foi encontrado na tela.")
                except Exception as e:
                    log_mensagem(f"⚠️ Erro inesperado ao verificar o elemento: {e}")
            except Exception as e:
                log_mensagem(f"⚠️ Erro durante o processo: {e}")
                break
    finally:
        executando = False
        log_mensagem("🔵 Thread de execução finalizada.")
        atualizar_estado_botoes("Aguardando...")

def carregar_credenciais():
    """Carrega credenciais de um arquivo JSON."""
    try:
        with open("credenciais.json", "r") as arquivo:
            return json.load(arquivo)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"usuario": "", "senha": ""}

def salvar_credenciais(usuario, senha):
    """Salva credenciais em um arquivo JSON."""
    with open("credenciais.json", "w") as arquivo:
        json.dump({"usuario": usuario, "senha": senha}, arquivo)
        log_mensagem("🔵 Credenciais salvas.")

def remover_credenciais():
    """Remove o arquivo de credenciais se ele existir."""
    if os.path.exists("credenciais.json"):
        os.remove("credenciais.json")
        log_mensagem("🔴 Credenciais removidas.")

def salvar_usuario():
    """Salva ou remove o usuário e senha com base no checkbox."""
    usuario = entry_usuario.get().strip()
    senha = entry_senha.get().strip()
    if var_salvar_usuario.get():
        if usuario and senha:
            salvar_credenciais(usuario, senha)
        else:
            log_mensagem("🔴 Campos de usuário ou senha estão vazios. Credenciais não salvas.")
    else:
        remover_credenciais()

def atualizar_estado_botoes(status_texto="Aguardando..."):
    """Atualiza o estado dos botões da interface."""
    global botao_executar, botao_continuar, botao_cancelar, status_label
    status_label.configure(text=f"Status: {status_texto}")
    if executando:
        botao_executar.configure(state="disabled")
        botao_continuar.configure(state="normal")
        botao_cancelar.configure(state="normal")
    else:
        botao_executar.configure(state="normal")
        botao_continuar.configure(state="disabled")
        botao_cancelar.configure(state="disabled")

def criar_interface():
    """Cria e configura a interface gráfica da aplicação."""
    global root, entry_usuario, entry_senha, entry_fazenda, entry_zona, entry_talhao
    global var_salvar_usuario, tipo_logica, log_textbox, status_label
    global botao_executar, botao_continuar, botao_cancelar

    PALETTE_BG = "#FFFFFF"
    PALETTE_TEXT = "#43948c"
    PALETTE_PRIMARY_BLUE = "#43948c"
    PALETTE_HOVER_BLUE = "#2e6862"
    PALETTE_SECONDARY_GREEN = "#7f7f7f"
    PALETTE_HOVER_GREEN = "#464545"
    PALETTE_ERROR_RED = "#b90000"
    PALETTE_HOVER_RED = "#861823"

    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title(f"AUTO. FICHA - OPE v{VERSAO}")
    root.geometry("500x1000")
    root.state("zoomed")

    main_frame = ctk.CTkFrame(root, fg_color=PALETTE_BG, corner_radius=10)
    main_frame.pack(pady=20, padx=20, fill="both", expand=True)

    title_font = ctk.CTkFont(family="Segoe UI", size=24, weight="bold")
    ctk.CTkLabel(main_frame, text="AUTO. FICHA - OPE", font=title_font, text_color=PALETTE_PRIMARY_BLUE).pack(pady=(10, 0))
    ctk.CTkLabel(main_frame, text=f"Versão {VERSAO}", text_color=PALETTE_TEXT).pack(pady=(0, 20))

    credentials_frame = ctk.CTkFrame(main_frame, fg_color="#F8F9FA", corner_radius=10)
    credentials_frame.pack(pady=10, padx=20, fill="x")
    
    ctk.CTkLabel(credentials_frame, text="Credenciais de Acesso", font=ctk.CTkFont(weight="bold"), text_color=PALETTE_TEXT).pack(pady=(10, 5), padx=20, anchor="w")
    
    entry_usuario = ctk.CTkEntry(credentials_frame, placeholder_text="Usuário", fg_color="#FFFFFF", border_color="#7f7f7f", text_color=PALETTE_TEXT)
    entry_usuario.pack(pady=5, padx=20, fill="x")
        
    entry_senha = ctk.CTkEntry(credentials_frame, placeholder_text="Senha", show="*", fg_color="#FFFFFF", border_color="#7f7f7f", text_color=PALETTE_TEXT)
    entry_senha.pack(pady=5, padx=20, fill="x")
    
    check_frame = ctk.CTkFrame(credentials_frame, fg_color="transparent")
    check_frame.pack(pady=5, padx=20, fill="x")
    
    var_salvar_usuario = tk.BooleanVar()
    check_salvar = ctk.CTkCheckBox(check_frame, text="Salvar credenciais", variable=var_salvar_usuario, text_color=PALETTE_TEXT, hover_color=PALETTE_PRIMARY_BLUE, fg_color=PALETTE_SECONDARY_GREEN, border_color="#7f7f7f")
    check_salvar.pack(side="left")

    def alternar_visualizacao_senha():
        current_show = entry_senha.cget("show")
        if current_show == "*":
            entry_senha.configure(show="")
            check_mostrar_senha.configure(text="Ocultar senha")
        else:
            entry_senha.configure(show="*")
            check_mostrar_senha.configure(text="Mostrar senha")

    check_mostrar_senha = ctk.CTkCheckBox(check_frame, text="Mostrar senha", command=alternar_visualizacao_senha, text_color=PALETTE_TEXT, hover_color=PALETTE_PRIMARY_BLUE, fg_color=PALETTE_SECONDARY_GREEN, border_color="#7f7f7f")
    check_mostrar_senha.pack(side="right")
    
    fill_data_frame = ctk.CTkFrame(main_frame, fg_color="#F8F9FA", corner_radius=10)
    fill_data_frame.pack(pady=10, padx=20, fill="x")

    ctk.CTkLabel(fill_data_frame, text="Dados de Preenchimento", font=ctk.CTkFont(weight="bold"), text_color=PALETTE_TEXT).pack(pady=(10, 5), padx=20, anchor="w")
    
    entry_fazenda = ctk.CTkEntry(fill_data_frame, placeholder_text="Fazenda (Opcional)", fg_color="#FFFFFF", border_color="#7f7f7f", text_color=PALETTE_TEXT)
    entry_fazenda.pack(pady=5, padx=20, fill="x")
    
    entry_zona = ctk.CTkEntry(fill_data_frame, placeholder_text="Zona (Opcional)", fg_color="#FFFFFF", border_color="#7f7f7f", text_color=PALETTE_TEXT)
    entry_zona.pack(pady=5, padx=20, fill="x")
    
    entry_talhao = ctk.CTkEntry(fill_data_frame, placeholder_text="Talhão (Opcional)", fg_color="#FFFFFF", border_color="#7f7f7f", text_color=PALETTE_TEXT)
    entry_talhao.pack(pady=5, padx=20, fill="x")

    mode_frame = ctk.CTkFrame(main_frame, fg_color="#F8F9FA", corner_radius=10)
    mode_frame.pack(pady=10, padx=20, fill="x")
    
    ctk.CTkLabel(mode_frame, text="Modo de Operação", font=ctk.CTkFont(weight="bold"), text_color=PALETTE_TEXT).pack(pady=(10, 5), padx=20, anchor="w")
    
    tipo_logica = tk.StringVar(value='Tipo 1')
    
    radio_frame = ctk.CTkFrame(mode_frame, fg_color="transparent")
    radio_frame.pack(pady=5, padx=10, fill="x")

    rb_zeradas = ctk.CTkRadioButton(radio_frame, text="Zeradas", variable=tipo_logica, value='Tipo 1', text_color=PALETTE_TEXT, hover_color=PALETTE_PRIMARY_BLUE, fg_color=PALETTE_SECONDARY_GREEN, border_color="#7f7f7f")
    rb_zeradas.pack(side="left", padx=10, pady=10, expand=True)
    
    rb_parciais = ctk.CTkRadioButton(radio_frame, text="Parciais", variable=tipo_logica, value='Tipo 2', text_color=PALETTE_TEXT, hover_color=PALETTE_PRIMARY_BLUE, fg_color=PALETTE_SECONDARY_GREEN, border_color="#7f7f7f")
    rb_parciais.pack(side="left", padx=10, pady=10, expand=True)

    button_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
    button_frame.pack(pady=20, padx=20, fill="x")

    def iniciar_execucao():
        if not executando:
            salvar_usuario()
            usuario = entry_usuario.get()
            senha = entry_senha.get()
            if not usuario or not senha:
                messagebox.showerror("Erro", "Usuário e senha são obrigatórios.")
                return
            threading.Thread(target=executar_script, args=(usuario, senha), daemon=True).start()
        else:
            log_mensagem("🔵 O script já está em execução.")

    botao_executar = ctk.CTkButton(button_frame, text="Executar", command=iniciar_execucao, height=40, fg_color=PALETTE_SECONDARY_GREEN, text_color="#FFFFFF", hover_color=PALETTE_HOVER_GREEN, font=ctk.CTkFont(weight="bold"))
    botao_executar.pack(side="left", fill="x", expand=True, padx=(0, 5))

    botao_continuar = ctk.CTkButton(button_frame, text="Continuar", command=continuar_execucao_func, height=40, fg_color=PALETTE_PRIMARY_BLUE, text_color="#FFFFFF", hover_color=PALETTE_HOVER_BLUE, state="disabled", font=ctk.CTkFont(weight="bold"))
    botao_continuar.pack(side="left", fill="x", expand=True, padx=5)

    botao_cancelar = ctk.CTkButton(button_frame, text="Pausar", command=pausar_execucao, height=40, fg_color=PALETTE_ERROR_RED, text_color="#FFFFFF", hover_color=PALETTE_HOVER_RED, state="disabled", font=ctk.CTkFont(weight="bold"))
    botao_cancelar.pack(side="left", fill="x", expand=True, padx=(5, 0))
    

    log_frame = ctk.CTkFrame(main_frame, fg_color="#F0F0F0", corner_radius=10)
    log_frame.pack(pady=(10, 0), padx=20, fill="both", expand=False)
    
    status_label = ctk.CTkLabel(log_frame, text="Status: Aguardando...", font=ctk.CTkFont(weight="bold"), text_color=PALETTE_TEXT)
    status_label.pack(pady=5, anchor="w", padx=10)
    
    log_textbox = ctk.CTkTextbox(log_frame, wrap="word", state="disabled", fg_color="#FFFFFF", text_color=PALETTE_TEXT, border_width=1, border_color="#7f7f7f", corner_radius=5)
    log_textbox.pack(pady=(0, 10), padx=10, fill="both", expand=True)

    log_textbox.tag_config("green_tag", foreground="#43948c")
    log_textbox.tag_config("red_tag", foreground="#b90000")
    log_textbox.tag_config("yellow_tag", foreground="#ee8715")
    log_textbox.tag_config("blue_tag", foreground="#7f7f7f")
    log_textbox.tag_config("default_tag", foreground=PALETTE_TEXT)

    credenciais = carregar_credenciais()
    if credenciais:
        entry_usuario.insert(0, credenciais.get("usuario", ""))
        entry_senha.insert(0, credenciais.get("senha", ""))
        if credenciais.get("usuario"):
            var_salvar_usuario.set(True)

    root.bind('<Return>', lambda event: iniciar_execucao())
    root.bind('<Escape>', lambda event: pausar_execucao())

    def fechar_janela():
        """Função para encerrar a aplicação e o navegador."""
        global executando, driver
        log_mensagem("🔵 Fechando a aplicação...")
        executando = False 
        if driver:
            try:
                log_mensagem("🔵 Fechando o navegador...")
                driver.quit()
            except Exception as e:
                log_mensagem(f"⚠️ Erro ao fechar o navegador (pode já estar fechado): {e}")
        time.sleep(1) 
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", fechar_janela)
    root.mainloop()

# --- Ponto de Entrada da Aplicação ---
if __name__ == "__main__":
    criar_interface()