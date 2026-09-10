import os
import ssl
import time
import json
import requests
import subprocess

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
APP_DIR = os.path.dirname(os.path.abspath(__file__))
LOCAL_MAIN = os.path.join(APP_DIR, "main.py")
LOCAL_VERSION = os.path.join(
    APP_DIR,
    "version_local.txt"
)
PYTHON_PATH = os.path.join(
    APP_DIR,
    "Python313",
    "python.exe"
)

# =====================================
# FUNCOES
# =====================================

def obter_config():
    try:
        headers = {
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }
        r = requests.get(
            URL_CONFIG,
            timeout=10,
            verify=False,
            headers=headers
        )
        r.raise_for_status()
        return r.json()
    except Exception as erro:
        print(
            f"❌ Erro ao ler config.json: {erro}"
        )
        return None


def obter_versao_local():
    if os.path.exists(LOCAL_VERSION):
        try:
            with open(
                LOCAL_VERSION,
                "r",
                encoding="utf-8"
            ) as f:
                return f.read().strip()

        except Exception:
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

        print(
            f"💾 Versão local salva: {versao}"
        )

    except Exception as erro:

        print(
            f"❌ Erro ao salvar versão local: {erro}"
        )


def atualizar_main():

    try:

        print(
            "⬇️ Baixando main.py..."
        )

        headers = {
            "Cache-Control": "no-cache",
            "Pragma": "no-cache"
        }

        r = requests.get(
            URL_MAIN,
            timeout=30,
            verify=False,
            headers=headers
        )

        r.raise_for_status()

        with open(
            LOCAL_MAIN,
            "wb"
        ) as arquivo:

            arquivo.write(r.content)

        print(
            "✅ main.py atualizado."
        )

        return True

    except Exception as erro:

        print(
            f"❌ Falha ao atualizar main.py: {erro}"
        )

        return False


def iniciar_app():

    print(
        "🚀 Iniciando sistema..."
    )

    try:

        if os.path.exists(PYTHON_PATH):

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
            f"❌ Erro ao iniciar app: {erro}"
        )

    finally:

        os._exit(0)

# =====================================
# EXECUCAO
# =====================================

def main():

    print(
        "🔍 Consultando config.json..."
    )

    config = obter_config()

    if not config:

        print(
            "⚠️ Não foi possível obter config.json."
        )

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

    print(
        f"Versão online: {versao_online}"
    )

    if not status:

        print(
            "🔴 Sistema bloqueado."
        )

        print(mensagem)

        time.sleep(3)

        return

    versao_local = obter_versao_local()

    print(
        f"Versão local: {versao_local}"
    )

    # CRIA version_local.txt automaticamente
    if not os.path.exists(LOCAL_VERSION):

        print(
            "📄 Criando version_local.txt..."
        )

        salvar_versao_local(
            versao_online
        )

    if versao_online != versao_local:

        print(
            f"🟡 Atualização encontrada: {versao_online}"
        )

        if atualizar_main():

            salvar_versao_local(
                versao_online
            )

            print(
                "✅ Atualização concluída."
            )

            time.sleep(1)

    else:

        print(
            "🟢 Sistema já atualizado."
        )

    iniciar_app()


if __name__ == "__main__":
    main()