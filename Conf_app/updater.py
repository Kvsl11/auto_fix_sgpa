import os
import ssl
import time
import requests
import subprocess
import tkinter as tk
from tkinter import messagebox

# =====================================
# SSL
# =====================================

ssl._create_default_https_context = ssl._create_unverified_context

requests.packages.urllib3.disable_warnings()

# =====================================
# CONFIG
# =====================================

REPO = "Kvsl11/auto_fix_sgpa"

BASE_URL = f"https://raw.githubusercontent.com/{REPO}/main/"

URL_CONFIG = BASE_URL + "config.json"
URL_MAIN = BASE_URL + "main.py"

APP_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

LOCAL_MAIN = os.path.join(
    APP_DIR,
    "main.py"
)

LOCAL_VERSION = os.path.join(
    APP_DIR,
    "version_local.txt"
)

LOCAL_CREDENCIAIS = os.path.join(
    APP_DIR,
    "credenciais.json"
)

PYTHON_PATH = os.path.join(
    APP_DIR,
    "Python313",
    "python.exe"
)

# =====================================
# FUNCOES
# =====================================

def mostrar_bloqueio(mensagem):

    try:

        root = tk.Tk()

        root.withdraw()

        root.attributes(
            "-topmost",
            True
        )

        messagebox.showerror(
            "AUTO. FICHA - OPE",
            mensagem
        )

        root.destroy()

    except:
        pass


def apagar_arquivos_bloqueio():

    arquivos = [
        LOCAL_MAIN,
        LOCAL_VERSION,
        LOCAL_CREDENCIAIS
    ]

    for arquivo in arquivos:

        try:

            if os.path.exists(arquivo):

                os.remove(arquivo)

                print(
                    f"🗑️ Removido: {os.path.basename(arquivo)}"
                )

        except Exception as erro:

            print(
                f"❌ Erro removendo {arquivo}: {erro}"
            )


def obter_config():

    try:

        r = requests.get(
            URL_CONFIG,
            timeout=10,
            verify=False,
            headers={
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
        )

        r.raise_for_status()

        return r.json()

    except Exception as erro:

        print(
            f"❌ Erro ao ler config.json: {erro}"
        )

        return None


def obter_versao_local():

    try:

        if os.path.exists(
            LOCAL_VERSION
        ):

            with open(
                LOCAL_VERSION,
                "r",
                encoding="utf-8"
            ) as f:

                return f.read().strip()

    except:
        pass

    return "0.0.0"


def salvar_versao_local(versao):

    try:

        with open(
            LOCAL_VERSION,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(str(versao))

    except:
        pass


def atualizar_main():

    try:

        print(
            "⬇️ Baixando main.py..."
        )

        r = requests.get(
            URL_MAIN,
            timeout=30,
            verify=False,
            headers={
                "Cache-Control": "no-cache",
                "Pragma": "no-cache"
            }
        )

        r.raise_for_status()

        with open(
            LOCAL_MAIN,
            "wb"
        ) as arquivo:

            arquivo.write(
                r.content
            )

        print(
            "✅ main.py atualizado."
        )

        return True

    except Exception as erro:

        print(
            f"❌ Falha ao baixar main.py: {erro}"
        )

        return False


def iniciar_app():

    if not os.path.exists(
        LOCAL_MAIN
    ):
        return

    try:

        if os.path.exists(
            PYTHON_PATH
        ):

            subprocess.Popen(
                [PYTHON_PATH, LOCAL_MAIN],
                creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW
            )

        else:

            subprocess.Popen(
                ["python", LOCAL_MAIN]
            )

    except Exception as erro:

        print(
            f"❌ Erro ao iniciar aplicação: {erro}"
        )

    finally:

        os._exit(0)

# =====================================
# EXECUCAO
# =====================================

def main():

    config = obter_config()

    if not config:

        if os.path.exists(
            LOCAL_MAIN
        ):
            iniciar_app()

        return

    versao_online = str(
        config.get(
            "version",
            "0.0.0"
        )
    )

    status = config.get(
        "status",
        True
    )

    mensagem = config.get(
        "message",
        ""
    )

    if not status:

        print(
            "🔴 Sistema bloqueado."
        )

        apagar_arquivos_bloqueio()

        mostrar_bloqueio(
            mensagem
            or
            "Sistema bloqueado pelo administrador."
        )

        return

    versao_local = obter_versao_local()

    precisa_baixar = (

        not os.path.exists(
            LOCAL_MAIN
        )

        or

        versao_local
        !=
        versao_online
    )

    if precisa_baixar:

        print(
            f"⬇️ Atualizando para versão {versao_online}"
        )

        if atualizar_main():

            salvar_versao_local(
                versao_online
            )

            time.sleep(1)

        else:

            return

    iniciar_app()


if __name__ == "__main__":
    main()