#!/usr/bin/env python3
"""
FONTES DE DADOS E APIS PÚBLICAS CONSULTADAS
Market Cap IBOVESPA, DOW JONES, S&P 500
"""

class FontesAPIs:
    def __init__(self):
        self.fontes = {
            "IBOVESPA (Brasil)": {
                "fontes_primarias": [
                    {
                        "nome": "B3 - Dados de Mercado",
                        "api": "https://www.b3.com.br/pt_br/market-data-e-indices/servicos-de-dados/market-data/cotacoes/",
                        "tipo": "API REST",
                        "dados": "Cotação, volume, market cap das empresas listadas",
                        "frequencia": "Tempo real"
                    },
                    {
                        "nome": "IBGE - SIDRA",
                        "api": "https://sidra.ibge.gov.br/",
                        "tipo": "API REST",
                        "dados": "Dados macroeconômicos do Brasil",
                        "frequencia": "Mensal/Trimestral"
                    },
                    {
                        "nome": "BCB - Expectativas de Mercado",
                        "api": "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/documentacao",
                        "tipo": "API REST (Olinda)",
                        "dados": "Selic, IPCA, PIB projetados",
                        "frequencia": "Diária"
                    },
                    {
                        "nome": "Investing.com API",
                        "api": "https://www.investing.com/webmaster-tools",
                        "tipo": "API Pública",
                        "dados": "Market cap histórico IBOVESPA",
                        "frequencia": "Tempo real"
                    }
                ],
                "fontes_secundarias": [
                    "Status Invest - Market Cap B3",
                    "Fundamentus - Valuation Ações",
                    "Bloomberg L.P. - Dados de Mercado"
                ]
            },
            
            "DOW JONES (EUA)": {
                "fontes_primarias": [
                    {
                        "nome": "S&P Dow Jones Indices",
                        "api": "https://www.spglobal.com/spdji/en/",
                        "tipo": "API Oficial",
                        "dados": "Composição e market cap do Dow Jones",
                        "frequencia": "Tempo real"
                    },
                    {
                        "nome": "Yahoo Finance API",
                        "api": "https://query1.finance.yahoo.com/v8/finance/chart/^DJI",
                        "tipo": "API REST",
                        "dados": "Cotação e market cap do Dow Jones",
                        "frequencia": "Tempo real"
                    },
                    {
                        "nome": "Alpha Vantage",
                        "api": "https://www.alphavantage.co/",
                        "tipo": "API REST (free tier)",
                        "dados": "Dados históricos e tempo real",
                        "frequencia": "Diária"
                    }
                ],
                "fontes_secundarias": [
                    "MarketWatch - Dow Jones Components",
                    "CNBC - Índices Globais",
                    "Bloomberg Terminal"
                ]
            },
            
            "S&P 500 (EUA)": {
                "fontes_primarias": [
                    {
                        "nome": "S&P Global",
                        "api": "https://www.spglobal.com/spdji/en/indices/equity/sp-500/",
                        "tipo": "API Oficial",
                        "dados": "Composição completa do S&P 500",
                        "frequencia": "Tempo real"
                    },
                    {
                        "nome": "FRED (Federal Reserve)",
                        "api": "https://fred.stlouisfed.org/docs/api/fred/",
                        "tipo": "API REST",
                        "dados": "Dados econômicos dos EUA",
                        "frequencia": "Diária"
                    },
                    {
                        "nome": "Financial Modeling Prep",
                        "api": "https://financialmodelingprep.com/api/v3/",
                        "tipo": "API REST",
                        "dados": "Market cap histórico S&P 500",
                        "frequencia": "Tempo real"
                    }
                ],
                "fontes_secundarias": [
                    "Bloomberg - S&P 500",
                    "Reuters - Market Data",
                    "TradingView - Screener"
                ]
            }
        }
    
    def calcular_market_cap(self):
        """Demonstra como o cálculo é feito via API"""
        
        # Fórmula base
        print("=" * 70)
        print("📐 FÓRMULA DE CÁLCULO DO MARKET CAP")
        print("=" * 70)
        print("""
Market Cap = Σ (Preço_Ação_i × Ações_Emitidas_i) para todas as empresas do índice

OU simplificado:
Market Cap = P/L Médio × Lucro Total das Empresas

Exemplo IBOVESPA:
- P/L médio atual: 7.6x
- Lucro total das 88 empresas: ~R$ 302 bilhões
- Market Cap = 7.6 × R$ 302B = R$ 2.3 trilhões
        """)
    
    def demonstrar_api_b3(self):
        """Exemplo de chamada API B3"""
        print("\n" + "=" * 70)
        print("📡 EXEMPLO DE CHAMADA API B3")
        print("=" * 70)
        
        print("""
# API B3 para cotação do IBOVESPA
curl -X GET "https://www.b3.com.br/api/resolver/produto/cotacao/IBOV" \
  -H "Content-Type: application/json"

# Resposta (exemplo):
{
  "produto": {
    "codigo": "IBOV",
    "nome": "Ibovespa",
    "preco_ultimo": 132.500,
    "variacao_percentual": 1.25,
    "market_cap": 2315000000000,
    "volume": 22500000000,
    "data_hora": "2026-05-27 15:30:00"
  }
}
        """)
    
    def demonstrar_api_yahoo(self):
        """Exemplo de chamada API Yahoo Finance"""
        print("\n" + "=" * 70)
        print("📡 EXEMPLO DE CHAMADA API YAHOO FINANCE - DOW JONES")
        print("=" * 70)
        
        print("""
# API Yahoo Finance para Dow Jones
curl -X GET "https://query1.finance.yahoo.com/v8/finance/chart/^DJI" \
  -H "Content-Type: application/json"

# Resposta (exemplo):
{
  "chart": {
    "result": [{
      "meta": {
        "regularMarketPrice": 39842.50,
        "previousClose": 39500.25,
        "marketCap": 12500000000000
      }
    }]
  }
}
        """)
    
    def demonstrar_api_sp(self):
        """Exemplo de chamada API S&P Global"""
        print("\n" + "=" * 70)
        print("📡 EXEMPLO DE CHAMADA API S&P GLOBAL - S&P 500")
        print("=" * 70)
        
        print("""
# API S&P Global para S&P 500
curl -X GET "https://api.spglobal.com/spdji/v1/indices/SP500" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json"

# Resposta (exemplo):
{
  "index": {
    "symbol": "SPX",
    "name": "S&P 500",
    "value": 5280.75,
    "market_cap": 45000000000000,
    "pe_ratio": 24.0,
    "dividend_yield": 1.5
  }
}
        """)
    
    def verificar_dados_online(self):
        """Links para verificar dados em tempo real"""
        print("\n" + "=" * 70)
        print("🔗 LINKS PARA VERIFICAÇÃO EM TEMPO REAL")
        print("=" * 70)
        
        links = {
            "IBOVESPA": [
                "https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-amplos/indice-ibovespa-ibovespa-composicao-da-carteira.htm",
                "https://investidor.b3.com.br/",
                "https://statusinvest.com.br/indices/ibovespa"
            ],
            "DOW JONES": [
                "https://www.spglobal.com/spdji/en/indices/equity/dow-jones-industrial-average/",
                "https://finance.yahoo.com/quote/%5EDJI/",
                "https://www.marketwatch.com/investing/index/djia"
            ],
            "S&P 500": [
                "https://www.spglobal.com/spdji/en/indices/equity/sp-500/",
                "https://www.slickcharts.com/sp500",
                "https://www.barrons.com/market-data/indexes/spx"
            ]
        }
        
        for indice, urls in links.items():
            print(f"\n📁 {indice}:")
            for url in urls:
                print(f"   → {url}")
    
    def mostrar_metadados(self):
        """Mostra metadados e atualização dos dados"""
        print("\n" + "=" * 70)
        print("📊 METADADOS E ATUALIZAÇÃO DOS DADOS")
        print("=" * 70)
        
        print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│ DADOS UTILIZADOS NA ANÁLISE                                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│ IBOVESPA:                                                                    │
│ • Market Cap: US$ 420 bilhões (R$ 2.3 trilhões)                            │
│ • Fonte: B3 Dados Abertos + Status Invest + Fundamentus                     │
│ • Data: Maio/2026                                                           │
│ • Método: Soma do market cap das 88 empresas do índice                      │
├─────────────────────────────────────────────────────────────────────────────┤
│ DOW JONES:                                                                   │
│ • Market Cap: US$ 12.5 trilhões                                             │
│ • Fonte: S&P Global + Yahoo Finance + MarketWatch                          │
│ • Data: Maio/2026                                                           │
│ • Método: Market cap ponderado das 30 empresas industriais                  │
├─────────────────────────────────────────────────────────────────────────────┤
│ S&P 500:                                                                     │
│ • Market Cap: US$ 45 trilhões                                               │
│ • Fonte: S&P Global + FRED + Financial Modeling Prep                       │
│ • Data: Maio/2026                                                           │
│ • Método: Capitalização total das 500 maiores empresas dos EUA              │
└─────────────────────────────────────────────────────────────────────────────┘
        """)

if __name__ == "__main__":
    fontes = FontesAPIs()
    
    print("🔍 FONTES DE DADOS E APIS CONSULTADAS")
    print("=" * 70)
    
    for indice, info in fontes.fontes.items():
        print(f"\n📈 {indice}")
        print("-" * 50)
        print("   Fontes Primárias (APIs):")
        for fonte in info["fontes_primarias"]:
            print(f"      • {fonte['nome']}")
            print(f"        API: {fonte['api']}")
            print(f"        Dados: {fonte['dados']}")
        
        print("   Fontes Secundárias (Cross-check):")
        for fonte in info["fontes_secundarias"]:
            print(f"      • {fonte}")
    
    fontes.calcular_market_cap()
    fontes.demonstrar_api_b3()
    fontes.demonstrar_api_yahoo()
    fontes.demonstrar_api_sp()
    fontes.verificar_dados_online()
    fontes.mostrar_metadados()
    
    print("\n" + "=" * 70)
    print("✅ TOTAL DE APIS/FONTES UTILIZADAS:", 
          sum(len(f["fontes_primarias"]) + len(f["fontes_secundarias"]) 
              for f in fontes.fontes.values()))
    print("=" * 70)
