# SELIX – Case Completo para o Prêmio ECO Amcham 2026

## 1. Contexto e Motivação
A Selic alta (14,5%) é um entrave ao crescimento, à geração de empregos e ao pagamento de direitos trabalhistas. O SELIX nasce para **provar matematicamente** qual seria a taxa justa e **monitorar em tempo real** o impacto no mercado de energia e nos trabalhadores.

## 2. Arquitetura e Tecnologia
- **Prova formal**: Z3 + Lean4 (5 teoremas).
- **Worker** em Python (coleta OilPriceAPI, BCB, Yahoo Finance).
- **API REST** (Flask) com 12 endpoints, rate limiting via NGINX.
- **Banco SQLite** com proveniência (fontes, observações, cenários, projeções).
- **Agente Bluesky** que publica threads segmentadas e responde a menções.
- **LLM local** (Ollama/llama.cpp) para respostas inteligentes (fallback).
- **Testes**: pytest (15 unitários + 5 integração), k6 (carga e estresse).

## 3. Dados e Métricas
- Brent real (OilPriceAPI): ~US$97
- Selic real (BCB): 14,25%
- TTF (Europa): ~€49 / MWh
- Rating geoenergético do Brasil: AA (score 0,266)
- Índice de confiança do cenário Selix_925: 46,5% (calculado com fatores reais)

## 4. Resultados de Testes
- Unitários: 15/15 ✅
- Integração: 5/5 ✅
- Carga: 68 req/s, p95=995ms
- Estresse: suportou 500 VUs com 4,64% de erro (limite conhecido)

## 5. Impacto Social e Ambiental
- Mix energético otimizado reduz emissões.
- Defesa do PLR e TrampoForte.
- Matriz renovável: 65% hidro, 12% eólica, 8% solar, 8% biomassa.

## 6. Transparência e Governança
- Código aberto (MIT), rastreável.
- Separação entre fatos (observações) e cenários (projeções).
- Documentação para DevOps e públicos-alvo.

## 7. Links e Anexos
- [Repositório](https://github.com/scoobiii/selix)
- [Perfil Bluesky](https://bsky.app/profile/zeh-sobrinho.bsky.social)
- [Release v4.0.0](https://github.com/scoobiii/selix/releases/tag/v4.0.0)
- [Vídeo de demonstração](https://youtu.be/...)
