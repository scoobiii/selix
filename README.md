
<div align="center">

# 🤖 SELIX v5.0 — Sistema de Inteligência Econômica Autônoma

**Selic real:** 14,25% · **Selic ideal:** 9,25% · **Economia anual:** R$ 270 bi

[![Bluesky Bot](https://img.shields.io/badge/Bluesky-@zeh--sobrinho-1DA1F2)](https://bsky.app/profile/zeh-sobrinho.bsky.social)
[![API v5.0](https://img.shields.io/badge/API-v5.0-green)](https://github.com/scoobiii/selix)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

---

## 🎯 O que é o SELIX?

SELIX é um **bot autônomo** que:
- Coleta dados reais de **Selic (BCB)** e **Brent (Yahoo Finance)**
- Publica **threads econômicas no Bluesky** às 9h, 13h e 18h (BRT)
- Oferece uma **API REST** para consulta de indicadores
- É **resiliente**: watchdog reinicia serviços automaticamente

**Resultado principal:** Selic ideal = **9,25%** (Selic atual = 14,25%)

---

## 🤖 Bluesky Bot

Perfil: [@zeh-sobrinho.bsky.social](https://bsky.app/profile/zeh-sobrinho.bsky.social)

O bot posta **3 threads por dia** com temas como:
- Fact-check da Selic
- Impacto nos trabalhadores e inadimplência
- Comparação internacional
- Oportunidades de investimento

O agendamento é feito internamente (biblioteca `schedule`), **sem depender de cron**.

---

## 🛠️ Arquitetura

| Componente | Função | Script |
|------------|--------|--------|
| **Worker** | Coleta Selic e Brent a cada 5 min | `worker_v7.py` |
| **API** | Endpoints REST (opcional) | `src.api.main_v4` |
| **Campaign Supervisor** | Agenda e publica threads | `scripts/campaign_supervisor.py` |
| **Watchdog** | Monitora e reinicia serviços | `scripts/watchdog.sh` |

Todos os serviços são iniciados em background pelo `run_selix.sh`.

---

## 🚀 Instalação e uso

### 1. Clone o repositório

```bash
git clone https://github.com/scoobiii/selix.git
cd selix
```

2. Crie o ambiente virtual e instale dependências

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Configure as credenciais do Bluesky

Crie um arquivo .env:

```
BLUESKY_USERNAME=zeh-sobrinho.bsky.social
BLUESKY_APP_PASSWORD=senha_do_app
```

A senha de app é gerada no Bluesky em Configurações → Senhas de Aplicativo.

4. Inicie o sistema

```bash
./run_selix.sh
```

O script inicia worker, API e campaign supervisor em segundo plano.
Logs ficam em logs/worker.log, logs/api.log, logs/supervisor.log.

5. Parar os serviços

```bash
pkill -f "worker_v7|main_v4|campaign_supervisor"
```

---

📦 API REST (opcional)

A API roda em http://localhost:5000. Endpoints principais:

Endpoint Método Descrição
/v1/health GET Status da API
/v1/selic GET Última Selic real
/v1/energia/mistura GET Brent e mix recomendado

---

🐧 Execução no Termux (Android)

O SELIX roda dentro de um contêiner proot (Ubuntu).
Para iniciar automaticamente após reinicialização do celular:

1. Instale Termux:Boot pelo F-Droid
2. Crie ~/.termux/boot/start_selix.sh:

```bash
#!/data/data/com.termux/files/usr/bin/bash
sleep 20
proot-distro login ubuntu -- bash -c "cd /root/selix && ./run_selix.sh"
```

3. Torne executável: chmod +x ~/.termux/boot/start_selix.sh

---

🧪 Testes

```bash
source venv/bin/activate
pytest tests/ -v
```

---

📄 Licença

MIT © 2026 – Zeh Sobrinho

```
