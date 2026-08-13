# GAIA Upgrade: SELIX como Infraestrutura de Juros

**Versão:** 2.0  
**Data:** 2026-08-13  
**Status:** Final (Estratégia de Produto)

---

## 1. Objetivo

Evoluir o SELIX de um **modelo de auditoria aritmética da Selic** para uma **infraestrutura de inteligência econômica descentralizada**, onde o valor não está no JSON, mas no **ecossistema**: algoritmo + histórico + metodologia + distribuição + API + marca + usuários.

## 2. Fluxo de Valor

```

FONTES (BCB/Yahoo) → SELIX ENGINE → CÁLCULO/STRESS → selix-official.json (ARTEFATO)
↓
┌─────────────────────────────────────┐
│        CAMADAS DE DISTRIBUIÇÃO       │
├─────────────────────────────────────┤
│ 1. GitHub Raw (JSON público)        │
│ 2. Cloud Run /v1/selic (API)        │
│ 3. CDN ticker.js (viral widget)     │
│ 4. WASM Simulator (interativo)      │
└─────────────────────────────────────┘

```

## 3. Modelo de Monetização

| Nível | Produto | O que oferece | Estratégia |
| :--- | :--- | :--- | :--- |
| **FREE** | **SELIX 1D™** | Ticker viral (widget `<script>`), dashboard básico, indicador público. | Aquisição de marca. Nunca cobrar pelo dado bruto. |
| **PRO** | **SELIX Analytics** | Simulador WASM (slider interativo), histórico completo, alertas, exportação de dados. | Assinatura mensal/anual. |
| **ENTERPRISE** | **SELIX API** | API privada dedicada, webhooks em tempo real, SLA, integrações customizadas. | Contrato corporativo sob demanda. |

## 4. Roadmap Técnico (v8.0)

| Etapa | Entregável | Status |
|-------|------------|--------|
| 1 | `selix-official.json` publicado com `8.25% / 6.0 / 14.25` | ✅ Feito |
| 2 | Cloud Run: API `/v1/selic` dinâmica (substitui GitHub Raw) | 🔄 Em andamento |
| 3 | Landing page `selix.com.br` SSR consumindo a API | ⏳ Pendente |
| 4 | Ticker viral `cdn.selix.com.br/ticker.js` (Canvas/WASM) | ⏳ Pendente |
| 5 | WASM Simulator: slider arrastável da Selic | ⏳ Pendente |
| 6 | PWA + Capacitor → APK Play Store | ⏳ Pendente |
| 7 | Stripe + API Keys (gerenciamento de assinaturas) | ⏳ Pendente |
| 8 | Histórico de dados como moat (diferencial competitivo) | ⏳ Pendente |

## 5. Regras de Ouro

1. **Número oficial único:** `src.selix.config` é a fonte absoluta. Todas as camadas (JSON, API, ticker, WASM) devem consumir o mesmo valor.
2. **Proxy externo ≠ modelo próprio:** O endpoint `/v1/dsge/rstar` é referência acadêmica externa (Santos/INTELI), nunca tratado como estimativa endógena do SELIX.
3. **Sem alucinação de lastro:** Se o core não carregar ou a prova formal falhar, o sistema **não publica**.
4. **Versionamento explícito:** Todo snapshot e resposta de agente deve conter `versao` e `updated_at`.

## 6. Estrutura de Diretórios (v8.0)

```

selix/
├── src/selix/                # Core do modelo
├── public/                   # Artefatos públicos (selix-official.json)
├── docs/
│   ├── product/              # Especificações de produto (ticker, etc.)
│   └── framework/            # Guias de integração canônica
├── .github/workflows/        # CI/CD (publish-snapshot, audit)
└── scripts/                  # Utilitários (generate_official_snapshot.py)

```

## 7. Próximas Ações (Sprint 1)

1. Criar o workflow `publish-snapshot.yml` para gerar e comitar `selix-official.json` automaticamente.
2. Configurar o deploy da FastAPI no Cloud Run (projeto `solar-api-468013`).
3. Criar o primeiro protótipo do ticker viral (canvas horizontal) consumindo o JSON oficial.
4. Atualizar o `selixIA` para consumir exclusivamente o `selix-official.json` e eliminar hardcodes.

---

> Este documento substitui a versão GAIA anterior e orienta o desenvolvimento do SELIX como um produto de infraestrutura financeira.
