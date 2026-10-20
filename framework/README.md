# SELIX Framework — Integração Canônica

Este diretório documenta a integração do SELIX. **Um snapshot versionado não é uma fonte de dados em tempo real.**

## Contrato de dados atuais

Para consumir a Selic com estado `CURRENT`, configure a URL real do serviço implantado em `VITE_SELIX_API_URL` e use o endpoint dinâmico:

```javascript
const API_BASE = import.meta.env.VITE_SELIX_API_URL;
if (!API_BASE) throw new Error("Configure VITE_SELIX_API_URL com a URL implantada do SELIX");

const response = await fetch(`${API_BASE.replace(/\/$/, "")}/v1/selic/snapshot`, {
  cache: "no-store",
  headers: { "Accept": "application/json" }
});

if (!response.ok) {
  // 503 significa que não há observação oficial disponível.
  // Não use o snapshot versionado como fallback.
  throw new Error(`SELIX indisponível: HTTP ${response.status}`);
}

const data = await response.json();
if (
  data.status !== "current" ||
  data.selic_atual_serie !== 432 ||
  data.selic_atual_fonte !== "BCB SGS 432" ||
  data.provenance !== "runtime:BCB SGS 432" ||
  !data.selic_atual_data_bcb
) {
  throw new Error("Resposta SELIX sem proveniência CURRENT válida");
}

console.log("Selic atual:", data.selic_atual);
```

O endpoint público é implementado em `src/api/main_v4.py`, que é o entrypoint do `Dockerfile` de produção. `src/api/main_v4_fastapi.py` também foi corrigido para não expor uma taxa derivada de constantes. Ele delega ao SPI canônico, que consulta o BCB SGS 432 em tempo de requisição. Se o BCB falhar, responde HTTP 503 e não retorna uma taxa estimada ou antiga.

## Snapshot versionado

`public/selix-official.json` é um artefato de publicação e pode ficar desatualizado entre execuções do pipeline. Pode ser usado para arquivo ou contexto histórico, **nunca** para afirmar que a Selic está atual. Consumidores não devem usar GitHub Raw como fallback para uma resposta CURRENT.

## Ticker / CDN

Qualquer ticker ou interface que mostre a etiqueta ATUAL/CURRENT deve obter seus dados do endpoint dinâmico e validar os campos de proveniência acima. Se não conseguir validar, deve mostrar indisponibilidade, não o último valor conhecido.

## Política canônica

Consulte [CURRENT-DATA-POLICY.md](../CURRENT-DATA-POLICY.md). Nenhum número fixo, cache antigo, snapshot estático ou resposta de LLM pode substituir a observação oficial do BCB.
