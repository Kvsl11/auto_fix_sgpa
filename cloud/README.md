# Auto Ficha OPE — versão Cloud (Web)

Versão web do app desktop `main.py`. A mesma automação Selenium agora roda **no servidor** e é controlada por um painel web moderno, acessado pelo navegador do **computador ou tablet** (telas a partir de 768 px; celulares veem apenas um aviso).

```
┌────────────────────────┐   HTTPS / WebSocket   ┌──────────────────────────────────┐
│  Front-end (React)     │ ────────────────────▶ │  Backend (FastAPI)               │
│  • formulário          │                       │  • /api/jobs  (iniciar/pausar…)  │
│  • log em tempo real   │ ◀──────────────────── │  • WebSocket de logs             │
│  • tela do navegador   │   logs, status, PNG   │  • AutomacaoFicha (Selenium)     │
└────────────────────────┘                       │      └─ Chromium headless ──▶ SGPA│
                                                 └──────────────────────────────────┘
```

## O que mudou em relação ao desktop

| Desktop (`main.py`)                    | Cloud                                                        |
|----------------------------------------|--------------------------------------------------------------|
| Interface Tkinter/CustomTkinter        | Painel web React + Tailwind (tema claro/escuro, PC e tablet) |
| Chrome visível no Windows              | Chromium headless no servidor + **pré-visualização ao vivo** |
| Mexer no navegador com o mouse         | **Modo interativo**: clicar/digitar na tela remota pelo painel |
| Variáveis globais (1 execução)         | Classe `AutomacaoFicha` por execução (multiusuário)          |
| `credenciais.json` com senha em texto  | Senha só trafega para iniciar a execução; o navegador lembra apenas o usuário |
| Trava remota via `config.json`         | Mantida: o servidor bloqueia e encerra as execuções          |
| Esc = Pausar                           | Mantido no painel                                            |

A lógica de negócio (XPaths, modos **Zeradas**/Tipo 1 e **Parciais**/Tipo 2, abas, espera da transição após salvar) é a mesma do script original — veja `backend/app/automation.py`.

## Estrutura

```
cloud/
├── backend/
│   ├── app/automation.py   # lógica Selenium (refatorada do main.py)
│   ├── app/jobs.py         # gerenciador de execuções + fan-out de logs
│   ├── app/main.py         # API FastAPI, WebSocket, auth, trava remota, serve o front
│   └── requirements.txt
├── frontend/               # React + Vite + TypeScript + Tailwind
├── Dockerfile              # imagem única: front compilado + API + Chromium
├── docker-compose.yml
├── render.yaml             # deploy no Render
└── .env.example
```

## Rodando localmente

Com Docker (recomendado):

```bash
cd cloud
```

```bash
APP_PASSWORD=minha-senha docker compose up --build
```

Abra http://localhost:8000.

Sem Docker (desenvolvimento, precisa de Chrome + chromedriver instalados):

```bash
cd cloud/backend && pip install -r requirements.txt && uvicorn app.main:app --reload
```

```bash
cd cloud/frontend && npm install && npm run dev
```

O Vite (http://localhost:5173) redireciona `/api` para o backend na porta 8000.

## Deploy na nuvem

O backend **precisa rodar em um servidor com container** (Chromium + execuções longas). Plataformas serverless como a Vercel não executam Selenium nem mantêm WebSockets abertos.

**Opção A — tudo em um serviço (mais simples):** Render, Railway, Fly.io, Google Cloud Run (com instância mínima 1) ou uma VPS. Use o `Dockerfile` desta pasta; no Render basta importar o `render.yaml` como Blueprint. Reserve **≥ 1 GB de RAM** (cada navegador usa ~300–500 MB).

**Opção B — front na Vercel + backend em container:**
1. Faça o deploy do backend como na opção A e defina `CORS_ORIGINS=https://seu-app.vercel.app`.
2. Na Vercel, crie o projeto com *Root Directory* `cloud/frontend` e a variável `VITE_API_URL=https://seu-backend.onrender.com`.

## Variáveis de ambiente

| Variável                      | Padrão                         | Descrição |
|-------------------------------|--------------------------------|-----------|
| `APP_PASSWORD`                | vazio (sem login)              | Senha do painel. **Defina sempre em produção.** |
| `SECRET_KEY`                  | derivada da senha              | Chave para assinar os tokens de sessão. |
| `MAX_CONCURRENT_JOBS`         | `2`                            | Navegadores simultâneos. |
| `CORS_ORIGINS`                | `*`                            | Domínios do front, se hospedado separado. |
| `REMOTE_CONFIG_URL`           | `config.json` deste repositório | Trava remota (`"status": false` bloqueia). Vazio desativa. |
| `HEADLESS`                    | `1`                            | `0` para ver o navegador (apenas local). |
| `SGPA_URL`                    | portal Adecoagro               | URL de login do SGPA. |

## Observações

- As credenciais do SGPA ficam apenas na memória da execução e não são gravadas em disco.
- O IP de saída passa a ser o do servidor. Se o SGPA restringir acesso por IP/rede, libere o IP do provedor ou use uma VPS com IP fixo.
- O app desktop (`App/`, `main.py`, `updater.py`) continua intacto e funcionando como antes.
