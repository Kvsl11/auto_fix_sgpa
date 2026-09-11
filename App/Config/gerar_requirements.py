import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQ = os.path.join(ROOT, "requirements.txt")

# Ignorar todos os módulos nativos do Python
IGNORAR = set(sys.stdlib_module_names)

IGNORAR.update({"__future__", "winreg"})

CORRECOES = {
    "PIL": "pillow",
    "cv2": "opencv-python",
    "fitz": "PyMuPDF",
    "bs4": "beautifulsoup4",
    "undetected_chromedriver": "undetected-chromedriver",
}

pacotes = set()
modulos_locais = set()

# Descobrir módulos locais do projeto
for pasta, _, arquivos in os.walk(ROOT):

    if "Python313" in pasta:
        continue

    for arquivo in arquivos:

        if arquivo.endswith(".py"):

            nome = os.path.splitext(arquivo)[0]

            modulos_locais.add(nome)

print()
print("=====================================")
print("ANALISANDO ARQUIVOS PYTHON")
print("=====================================")
print()

for pasta, _, arquivos in os.walk(ROOT):

    if "Python313" in pasta:
        continue

    for arquivo in arquivos:

        if not arquivo.endswith(".py"):
            continue

        caminho = os.path.join(pasta, arquivo)

        print(f"Analisando: {arquivo}")

        try:

            with open(caminho, "r", encoding="utf-8", errors="ignore") as f:

                for linha in f:

                    match_import = re.match(r"^\s*import\s+([a-zA-Z0-9_.]+)", linha)

                    if match_import:

                        modulo = match_import.group(1).split(".")[0]

                        if modulo not in IGNORAR and modulo not in modulos_locais:

                            pacotes.add(CORRECOES.get(modulo, modulo))

                    match_from = re.match(r"^\s*from\s+([a-zA-Z0-9_.]+)", linha)

                    if match_from:

                        modulo = match_from.group(1).split(".")[0]

                        if modulo not in IGNORAR and modulo not in modulos_locais:

                            pacotes.add(CORRECOES.get(modulo, modulo))

        except Exception as erro:

            print(f"Erro em {arquivo}: {erro}")

# Dependências obrigatórias
pacotes.update({"requests", "selenium", "customtkinter", "undetected-chromedriver"})

pacotes = {pacote.strip() for pacote in pacotes if pacote.strip()}

with open(REQ, "w", encoding="utf-8") as arquivo:

    for pacote in sorted(pacotes):

        arquivo.write(pacote + "\n")

print()
print("=====================================")
print("REQUIREMENTS GERADO")
print("=====================================")
print()

for pacote in sorted(pacotes):

    print(f"- {pacote}")

print()
print("Arquivo salvo em:")
print(REQ)
print()
