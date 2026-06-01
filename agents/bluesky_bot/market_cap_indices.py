#!/usr/bin/env python3
"""
Comparação de Market Cap dos Principais Índices Globais
IBOVESPA (Brasil) vs DOW JONES (EUA) vs S&P 500 (EUA)
"""

class MarketCapIndices:
    def __init__(self):
        # Dados atualizados (Maio/2026)
        self.indices = {
            "IBOVESPA": {
                "nome": "Ibovespa (Brasil)",
                "pais": "Brasil",
                "empresas": 88,
                "market_cap_usd": 420e9,      # US$ 420 bilhões
                "market_cap_brl": 2_300e9,    # R$ 2.3 trilhões
                "selic": 0.145,
                "p_l_medio": 7.6,
                "dy": 0.085,
                "roi_medio": 0.09
            },
            "DOW_JONES": {
                "nome": "Dow Jones Industrial Average (EUA)",
                "pais": "EUA",
                "empresas": 30,
                "market_cap_usd": 12_500e9,   # US$ 12.5 trilhões
                "market_cap_brl": 68_750e9,   # R$ 68.75 trilhões
                "selic": 0.0525,              # 5.25% (Fed)
                "p_l_medio": 22.5,
                "dy": 0.018,
                "roi_medio": 0.15
            },
            "SP500": {
                "nome": "S&P 500 (EUA)",
                "pais": "EUA",
                "empresas": 500,
                "market_cap_usd": 45_000e9,   # US$ 45 trilhões
                "market_cap_brl": 247_500e9,  # R$ 247.5 trilhões
                "selic": 0.0525,
                "p_l_medio": 24.0,
                "dy": 0.015,
                "roi_medio": 0.16
            }
        }
        
        # Projeção com SELIX + TrampoForte
        self.fatores_brasil = {
            "selic_nova": 0.0948,
            "multiplo_p_l_expansao": 2.5,     # P/L pode triplicar
            "roi_melhoria": 0.04,              # +4% ROI com juros menores
            "investment_grade": True,
            "risco_pais_reducao": 0.50         # 50% menos risco
        }
    
    def calcular_market_cap_projetado(self, indice):
        """Calcula market cap projetado com SELIX + TrampoForte"""
        
        dados = self.indices[indice]
        
        if indice != "IBOVESPA":
            # EUA não mudam com SELIX
            return dados["market_cap_usd"], 0
        
        # Brasil: expansão do múltiplo + novos IPOs
        mult_atual = dados["p_l_medio"]
        mult_novo = mult_atual * self.fatores_brasil["multiplo_p_l_expansao"]
        
        # Lucro total atual
        lucro_total = dados["market_cap_usd"] / mult_atual
        
        # Novo market cap
        market_cap_novo_usd = lucro_total * mult_novo
        
        # +35% de novas empresas (IPOs descongelados)
        market_cap_novo_usd *= 1.35
        
        crescimento = ((market_cap_novo_usd / dados["market_cap_usd"]) - 1) * 100
        
        return market_cap_novo_usd, crescimento
    
    def gerar_relatorio(self):
        """Relatório comparativo"""
        
        print("=" * 80)
        print("🌍 MARKET CAP DOS PRINCIPAIS ÍNDICES GLOBAIS")
        print("=" * 80)
        
        print("\n📊 SITUAÇÃO ATUAL (Maio/2026)")
        print("-" * 80)
        
        for indice, dados in self.indices.items():
            print(f"\n🏛️ {dados['nome']}")
            print(f"   País: {dados['pais']}")
            print(f"   Empresas: {dados['empresas']}")
            print(f"   Market Cap: US$ {dados['market_cap_usd']/1e9:.0f}B")
            print(f"   Market Cap: R$ {dados['market_cap_brl']/1e12:.1f} trilhões")
            print(f"   P/L médio: {dados['p_l_medio']:.1f}x")
            print(f"   Dividend Yield: {dados['dy']*100:.1f}%")
            print(f"   Selic/Fed: {dados['selic']*100:.1f}%")
        
        # Tabela comparativa
        print("\n" + "=" * 80)
        print("📈 TABELA COMPARATIVA")
        print("=" * 80)
        
        print(f"\n{'Índice':<20} {'Market Cap (US$B)':<20} {'P/L':<10} {'DY':<10} {'Empresas':<10}")
        print("-" * 70)
        
        for indice, dados in self.indices.items():
            nome_curto = indice.replace("_", " ")
            print(f"{nome_curto:<20} US$ {dados['market_cap_usd']/1e9:.0f}B{'':<10} {dados['p_l_medio']:.1f}x{'':<7} {dados['dy']*100:.1f}%{'':<7} {dados['empresas']}")
        
        # Proporção
        print("\n" + "=" * 80)
        print("⚖️ PROPORÇÃO BRASIL vs EUA")
        print("=" * 80)
        
        ibov_usd = self.indices["IBOVESPA"]["market_cap_usd"]
        sp500_usd = self.indices["SP500"]["market_cap_usd"]
        dow_usd = self.indices["DOW_JONES"]["market_cap_usd"]
        
        proporcao_sp = (ibov_usd / sp500_usd) * 100
        proporcao_dow = (ibov_usd / dow_usd) * 100
        
        print(f"\nIBOVESPA é {proporcao_sp:.2f}% do tamanho do S&P 500")
        print(f"IBOVESPA é {proporcao_dow:.2f}% do tamanho do Dow Jones")
        
        # Gráfico de barras comparativo
        print("\n" + "=" * 80)
        print("📊 GRÁFICO COMPARATIVO (Market Cap em US$ Bilhões)")
        print("=" * 80)
        
        max_mc = max(d["market_cap_usd"] for d in self.indices.values())
        bar_max = 60
        
        for indice, dados in self.indices.items():
            mc = dados["market_cap_usd"]
            bar_size = int((mc / max_mc) * bar_max)
            bar = "█" * bar_size
            
            nome_display = {
                "IBOVESPA": "IBOVESPA",
                "DOW_JONES": "DOW JONES",
                "SP500": "S&P 500"
            }[indice]
            
            cor = "🟢" if indice == "IBOVESPA" else "🔵" if indice == "SP500" else "🔷"
            print(f"{nome_display:10} {cor} {bar} US$ {mc/1e9:.0f}B")
        
        # PROJEÇÃO BRASIL COM SELIX + TRAMPOFORTE
        print("\n" + "=" * 80)
        print("🚀 PROJEÇÃO BRASIL COM SELIX + TRAMPOFORTE")
        print("=" * 80)
        
        mc_novo_usd, crescimento = self.calcular_market_cap_projetado("IBOVESPA")
        mc_atual_usd = self.indices["IBOVESPA"]["market_cap_usd"]
        
        print(f"\nIBOVESPA ATUAL:")
        print(f"   Market Cap: US$ {mc_atual_usd/1e9:.0f}B")
        print(f"   P/L médio: {self.indices['IBOVESPA']['p_l_medio']:.1f}x")
        
        print(f"\nIBOVESPA COM SELIX + TRAMPOFORTE:")
        print(f"   Market Cap: US$ {mc_novo_usd/1e9:.0f}B")
        print(f"   P/L médio: {self.indices['IBOVESPA']['p_l_medio'] * self.fatores_brasil['multiplo_p_l_expansao']:.1f}x")
        print(f"   Crescimento: +{crescimento:.0f}%")
        
        # Nova proporção
        nova_proporcao_sp = (mc_novo_usd / sp500_usd) * 100
        
        print(f"\nNOVA PROPORÇÃO:")
        print(f"   IBOVESPA passará a ser {nova_proporcao_sp:.2f}% do S&P 500")
        print(f"   (antes era {proporcao_sp:.2f}%)")
        
        # Gráfico da projeção
        print("\n📊 GRÁFICO PROJETADO (Market Cap IBOVESPA)")
        print("-" * 50)
        
        bar_max = 50
        bar_atual = int((mc_atual_usd / mc_novo_usd) * bar_max)
        bar_novo = bar_max
        
        print(f"ATUAL:     🔴 {'█' * bar_atual} US$ {mc_atual_usd/1e9:.0f}B")
        print(f"PROJETADO: 🟢 {'█' * bar_novo} US$ {mc_novo_usd/1e9:.0f}B (+{crescimento:.0f}%)")
        
        # Comparação com EUA após projeção
        print("\n" + "=" * 80)
        print("🎯 COMPARAÇÃO FINAL (PÓS SELIX + TRAMPOFORTE)")
        print("=" * 80)
        
        print(f"\n{'Índice':<20} {'Market Cap (US$B)':<25} {'% do S&P 500':<15}")
        print("-" * 60)
        print(f"{'IBOVESPA (hoje)':<20} US$ {mc_atual_usd/1e9:.0f}B{'':<10} {proporcao_sp:.2f}%")
        print(f"{'IBOVESPA (SELIX)':<20} US$ {mc_novo_usd/1e9:.0f}B{'':<10} {nova_proporcao_sp:.2f}%")
        print(f"{'S&P 500':<20} US$ {sp500_usd/1e9:.0f}B{'':<10} 100.00%")
        print(f"{'Dow Jones':<20} US$ {dow_usd/1e9:.0f}B{'':<10} {(sp500_usd/dow_usd-1)*100:.0f}% do S&P")
        
        # Resumo final
        print("\n" + "=" * 80)
        print("✅ CONCLUSÃO")
        print("=" * 80)
        
        print(f"""
┌─────────────────────────────────────────────────────────────────────────────┐
│ RESULTADO:                                                                  │
│                                                                             │
│ IBOVESPA hoje:      US$ {mc_atual_usd/1e9:.0f}B (R$ {self.indices['IBOVESPA']['market_cap_brl']/1e12:.1f} trilhões)    │
│ IBOVESPA com SELIX: US$ {mc_novo_usd/1e9:.0f}B (R$ {mc_novo_usd * 5.5 / 1e12:.1f} trilhões) │
│                                                                             │
│ CRESCIMENTO:        +{crescimento:.0f}%                                     │
│                                                                             │
│ S&P 500:            US$ {sp500_usd/1e9:.0f}B                                │
│ Dow Jones:          US$ {dow_usd/1e9:.0f}B                                  │
│                                                                             │
│ IBOVESPA (SELIX) = {nova_proporcao_sp:.1f}% do S&P 500 (hoje é {proporcao_sp:.1f}%)     │
└─────────────────────────────────────────────────────────────────────────────┘
        """)

if __name__ == "__main__":
    analise = MarketCapIndices()
    analise.gerar_relatorio()
