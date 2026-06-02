# 🧠 Skill: Agentes Humanizados do SELIX

## Objetivo
Transformar interações passivas (curtidas, menções) em **relacionamentos ativos** que amplificam o alcance e geram leads qualificados.

## Perfil dos Agentes Humanizados
- São contas com **score > 70** (bio, avatar, posts coerentes, comportamento não‑bot).
- Tendem a ser **influenciadores de nicho**, profissionais ou usuários engajados.
- Valorizam reciprocidade e conteúdo relevante.

## Instruções para o SELIX (sistema)

### 1. Identificação
- Execute `analisar_curtidores.py` diariamente para atualizar a lista.
- Armazene na tabela `perfis_analisados` com campo `classificado_como`.

### 2. Engajamento automático (script `engajar_agentes.py`)
- **Seguir de volta** (se não seguir).
- **Curtir e repostar** (até 2 posts recentes) – repost com 30% de probabilidade.
- **Enviar menção amigável** (uma vez a cada 30 dias) apresentando o SELIX.

### 3. Inclusão em CCs estratégicos
Quando o `responder_inteligente.py` identificar perguntas sobre **tecnologia, inovação, energia ou economia**, adicionar dinamicamente os handles dos 3 agentes com maior score no campo `cc_handles` da resposta.

### 4. Métricas de sucesso
- **Taxa de follow‑back** (quantos agentes seguem de volta).
- **Engajamento gerado** (curtidas/reposts em posts do SELIX atribuídos a esses agentes).
- **Conversões** (agentes que se tornaram leads ou clientes pagantes).

### 5. Limites de taxa (rate limit)
- Respeitar os limites do Bluesky: no máximo 3 ações (follow/like/repost) por minuto.
- Intervalo mínimo de 2 segundos entre ações.

## Exemplo de fluxo
1. Agente @talentx curte um post do SELIX sobre energia solar.
2. SELIX identifica que é um agente humanizado (score 90).
3. Na próxima execução do `engajar_agentes.py`:
   - Segue @talentx.
   - Curte e reposta (30% chance) o último post dele.
   - Envia menção: *"@talentx obrigado pelo apoio! Acompanhe dados de energia e Selic ideal = 9,25%."*
4. Nas próximas respostas a perguntas sobre "inovação", o SELIX inclui @talentx no CC.

## Por que isso funciona?
- **Reciprocidade** → aumenta a probabilidade de reposts e menções.
- **Alcance orgânico** → os agentes compartilham conteúdo com suas audiências.
- **Lead nurturing** → agentes com perfil profissional podem se tornar clientes pagantes.

## Referências
- Scripts envolvidos: `analisar_curtidores.py`, `engajar_agentes.py`, `responder_inteligente.py`.
- Tabelas: `perfis_analisados`, `interacoes_agentes`.
