# SELIX para Investidores

## Valuation projetado com Selic 9,25%

| Empresa | Upside projetado |
|---------|------------------|
| **GPA (PCAR3)** | +68% |
| **Raízen (RAIZ4)** | +76% |

## Cenário macroeconômico

- PIB per capita: **US$ 130.000** (+118%)
- B3 Market Cap: **US$ 10 trilhões** (6x atual)
- Investment Grade: **A-** (hoje BB)

## API para integração\n\nA URL de produção precisa ser confirmada no ambiente de deploy; não presuma que um domínio personalizado esteja ativo.

```bash
# Configure a URL real do serviço implantado antes de executar:
export SELIX_API_BASE_URL="https://<URL-real-do-servico>"
curl "$SELIX_API_BASE_URL/v1/selic/snapshot"
```

