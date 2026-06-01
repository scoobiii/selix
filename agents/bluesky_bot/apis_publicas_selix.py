#!/usr/bin/env python3
"""
APIs Públicas Integradas ao SELIX
Fontes de dados oficiais e transparentes
"""

apis_utilizadas = {
    "Dados Macroeconômicos": {
        "BCB (Banco Central)": {
            "endpoint": "https://olinda.bcb.gov.br/olinda/servico/Expectativas/versao/v1/documentacao",
            "dados": ["Selic", "IPCA", "PIB", "Câmbio"],
            "frequencia": "Diária"
        },
        "IBGE": {
            "endpoint": "https://servicodados.ibge.gov.br/api/docs/",
            "dados": ["IPCA", "INPC", "IGP-M", "PIB", "Desemprego"],
            "frequencia": "Mensal"
        },
        "IPEADATA": {
            "endpoint": "http://www.ipeadata.gov.br/api/",
            "dados": ["Série histórica Selic", "Juros reais", "Dívida pública"],
            "frequencia": "Diária"
        }
    },
    
    "Mercado Financeiro": {
        "B3 (Dados Abertos)": {
            "endpoint": "https://arquivos.b3.com.br/",
            "dados": ["Preço ações", "Ibovespa", "Volume negociado", "IPOs"],
            "frequencia": "Diária"
        },
        "Investing.com API": {
            "endpoint": "https://www.investing.com/webmaster-tools",
            "dados": ["Brent", "WTI", "Commodities"],
            "frequencia": "Tempo real"
        },
        "Yahoo Finance": {
            "endpoint": "https://query1.finance.yahoo.com/v8/finance/chart/",
            "dados": ["Histórico ações", "Valuation", "Dividendos"],
            "frequencia": "Tempo real"
        }
    },
    
    "Energia": {
        "ANEEL": {
            "endpoint": "https://dadosabertos.aneel.gov.br/",
            "dados": ["Preço energia", "Consumo", "Capacidade instalada"],
            "frequencia": "Mensal"
        },
        "EPE": {
            "endpoint": "https://www.epe.gov.br/pt/publicacoes-dados-abertos/",
            "dados": ["Matriz energética", "Projeções", "Biocombustíveis"],
            "frequencia": "Anual"
        },
        "EIA (US)": {
            "endpoint": "https://www.eia.gov/opendata/",
            "dados": ["Brent", "GNL", "Estoques EUA"],
            "frequencia": "Semanal"
        }
    },
    
    "Judicial/Trabalhista": {
        "Datajud (CNJ)": {
            "endpoint": "https://datajud.cnj.jus.br/api/",
            "dados": ["Processos RJ", "Ações trabalhistas", "Distribuição"],
            "frequencia": "Diária"
        },
        "TST Dados Abertos": {
            "endpoint": "https://dadosabertos.tst.jus.br/",
            "dados": ["Reclamações trabalhistas", "Acordos", "PLR"],
            "frequencia": "Mensal"
        }
    },
    
    "Empresas (CVM)": {
        "CVM Dados Abertos": {
            "endpoint": "https://dados.cvm.gov.br/",
            "dados": ["Demonstrações financeiras", "Fatores relevantes", "Composição acionária"],
            "frequencia": "Trimestral"
        },
        "Receita Federal CNPJ": {
            "endpoint": "https://receita.economia.gov.br/orientacao/tributaria/cadastros/cadastro-nacional-de-pessoas-juridicas-cnpj",
            "dados": ["Cadastro empresas", "Situação cadastral", "Sócios"],
            "frequencia": "Diária"
        }
    }
}

print("=" * 70)
print("🔗 APIS PÚBLICAS INTEGRADAS AO SELIX")
print("=" * 70)

for categoria, fontes in apis_utilizadas.items():
    print(f"\n📁 {categoria}")
    print("-" * 50)
    for nome, info in fontes.items():
        print(f"   • {nome}")
        print(f"     Endpoint: {info['endpoint']}")
        print(f"     Dados: {', '.join(info['dados'][:3])}...")
        print(f"     Frequência: {info['frequencia']}")

print("\n" + "=" * 70)
print("✅ TOTAL DE APIS INTEGRADAS:", sum(len(fontes) for fontes in apis_utilizadas.values()))
print("=" * 70)
