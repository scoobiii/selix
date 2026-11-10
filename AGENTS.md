# AGENTS.md: time e regras do SELIX

## Quem decide
- **Product Owner e único executor: scoobiii.** Roda os comandos, aprova merge, publica e autoriza qualquer force-push.
- **Agentes de IA são consultivos.** Não executam nada no repositório.

## Papéis (decididos pelo PO, revisados a cada sprint)
| Agente | Papel | Evidência observada | Limite |
|---|---|---|---|
| GPT | Verificador de estado remoto | Leu PR, checks e package.json com acesso ao GitHub | Toda afirmação de CI exige link do run e SHA |
| Claude (Sonnet 5.5) | Revisor de evidência e autor de patches | Leu tests.yml, .coveragerc, diffs e saídas do terminal | Não vê o GitHub logado nem executa no repo |
| DeepSeek | Dono de contrato de dados | Leu spi.py e CURRENT-DATA-POLICY.md | Errou ao dizer "commit único" e ao propor rebase com force-push |
| Manus | Revisor de consistência e processo | Apontou que os relatos dos agentes se contradizem | Sem leitura de código nesta conversa |
| Grok | Sem papel até provar | Repetiu a descrição do PR, sem ler código | Precisa apresentar saída de arquivo lido |
| Gemini | Sem papel até provar | Afirmou que existia AGENTS.md; não existia | Idem |
| Qwen | Sem papel até provar | Mandou git mv para archive/, que quebrava CI e produção | Idem |
| Meta AI | Sem papel até provar | Propôs sed em massa nos launchers sem ler os arquivos | Idem |

Versão de cada modelo: registrar na primeira resposta de cada sprint.

## Donos por caminho
| Caminho | Dono |
|---|---|
| src/selix/spi.py, src/api/main_v4.py | DeepSeek (contrato de dados) |
| packages/selix-core/ | Pendente (ninguém provou ler o pacote) |
| docs/index.html, .github/workflows/ | Pendente |

## Regras
1. **Evidência primeiro.** Afirmação sobre estado (CI verde, PR mergeável, cobertura) exige saída colada ou link de run. Sem isso, vale "não verificado".
2. **Ler antes de mudar.** Ler a config e o código reais antes de criar comando, script ou config nova.
3. **Um PR por demanda.** A descrição do PR deve listar todos os arquivos alterados.
4. **Proibido sem OK do PO:** git reset, git clean, git stash, git mv ou sed em massa, rebase e force-push em PR aberto.
5. **Dado atual** só com proveniência runtime:BCB SGS 432. Sem fallback, sem número fixo.
6. **Resposta de agente sem identificação não conta.** Começa com o nome do modelo e traz duas listas: "li" (arquivo, linha ou saída) e "não li". O PO pode revogar um papel a qualquer momento.

## Definition of Done
- Suíte integral verde, sem skip fora da lista de exceções.
- Cobertura não cai abaixo do piso (ratchet), medida com o .coveragerc do repo.
- Descrição do PR corresponde ao diff.
- Check verde no GitHub, conferido no SHA do PR.
- Deploy publicado só depois dos testes passarem.

## Exceções de teste (skips)
| Teste | Motivo | Dono | Data |
|---|---|---|---|
| tests/test_api.py:47 | /v1/alertas/geral não implementado | Pendente | 2026-11-10 |

## Dívidas conhecidas
- Entrypoints paralelos: main_v4.py (Dockerfile) vs main_v4_fixed.py (scripts e Makefile) vs server_v6.py (GCP).
- docs/index.html com números fixos e formulário fictício.
- .coveragerc omite cerca de 20 módulos da métrica.
- gh-pages.yml publica em todo push na main, sem esperar os testes.

## Sprint
Sprint Goal: (definido pelo PO)
