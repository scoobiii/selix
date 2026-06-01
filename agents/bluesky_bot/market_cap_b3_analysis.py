#!/usr/bin/env python3
"""
Análise do Market Cap da B3 (B3SA3)
Cenários: Hoje (Selic 14.5%) vs SELIX (9.48%) vs TrampoForte
"""

class MarketCapB3:
    def __init__(self):
        # Dados fundamentais da B3 (B3SA3)
        self.b3 = {
            "nome": "B3 S.A. - Brasil, Bolsa, Balcão",
            "codigo": "B3SA3",
            "preco_atual": 12.50,           # R$ por ação (IPO congelado)
            "acoes_emitidas": 1_900_000_000,  # 1.9 bilhões de ações
            "free_float": 0.75,               # 75% livre circulação
            "lucro_anual": 6_500_000_000,     # R$ 6.5 bilhões (2025)
            "payout": 0.75,                   # 75% de payout
            "roe": 0.18,                      # 18% ROE
            "crescimento_historico": 0.08,    # 8% ao ano
        }
        
        # Cenários macroeconômicos
        self.cenarios = {
            "hoje": {
                "selic": 0.145,      # 14.5%
                "risco_brasil": 0.035,  # 350bps
                "confidence": 0.65,   # 65% confiança
                "ipos_ano": 0,        # IPOs congelados
                "investment_grade": False
            },
            "selix": {
                "selic": 0.0948,     # 9.48%
                "risco_brasil": 0.025,  # 250bps (melhora)
                "confidence": 0.80,   # 80% confiança
                "ipos_ano": 25,       # 25 IPOs/ano
                "investment_grade": True
            },
            "trampoforte": {
                "selic": 0.0948,     # 9.48%
                "risco_brasil": 0.015,  # 150bps (redução risco trabalhista)
                "confidence": 0.95,   # 95% confiança
                "ipos_ano": 45,       # 45 IPOs/ano
                "investment_grade": True
            }
        }
        
    def calcular_custo_capital(self, selic, risco_brasil):
        """CAPM: Ke = RF + Risco_Brasil + Beta * Prêmio_Mercado"""
        beta = 0.85
        premio_mercado = 0.06
        return selic + risco_brasil + (beta * premio_mercado)
    
    def calcular_valuation_gordon(self, selic, risco_brasil):
        """Modelo de Gordon: P = D1 / (Ke - g)"""
        ke = self.calcular_custo_capital(selic, risco_brasil)
        g = 0.05  # crescimento esperado conservador
        
        # Dividendo = Lucro × Payout / Ações
        d1 = (self.b3["lucro_anual"] * self.b3["payout"]) / self.b3["acoes_emitidas"]
        
        if ke <= g:
            return 999.99  # valuation infinito
        
        return d1 / (ke - g)
    
    def calcular_market_cap(self, preco_acao):
        """Market Cap = Preço × Ações Emitidas"""
        return preco_acao * self.b3["acoes_emitidas"]
    
    def calcular_multiplo_ipo(self, ipos_ano):
        """IPOs descongelados aumentam volume e múltiplo da B3"""
        # Cada IPO aumenta o market cap da B3 em aproximadamente R$ 500M
        # (taxa de listagem + aumento de volume)
        return 1 + (ipos_ano * 500_000_000 / self.b3["lucro_anual"])
    
    def calcular_preco_final(self, cenario):
        """Preço final considerando valuation + descongelamento IPOs"""
        
        dados = self.cenarios[cenario]
        
        # Valuation base pelo modelo de Gordon
        preco_base = self.calcular_valuation_gordon(dados["selic"], dados["risco_brasil"])
        
        # Multiplicador de confiança
        multiplicador_confianca = dados["confidence"] / 0.65
        
        # Multiplicador de IPOs
        multiplicador_ipos = self.calcular_multiplo_ipo(dados["ipos_ano"])
        
        # Fator Investment Grade
        fator_ig = 1.15 if dados["investment_grade"] else 1.0
        
        # Preço final
        preco_final = preco_base * multiplicador_confianca * multiplicador_ipos * fator_ig
        
        return preco_final
    
    def gerar_relatorio_completo(self):
        """Relatório comparativo dos 3 cenários"""
        
        print("=" * 80)
        print("🏦 MARKET CAP DA B3 (B3SA3) - ANÁLISE COMPARATIVA")
        print("=" * 80)
        
        resultados = {}
        
        for cenario in ["hoje", "selix", "trampoforte"]:
            dados = self.cenarios[cenario]
            preco = self.calcular_preco_final(cenario)
            market_cap = self.calcular_market_cap(preco)
            ke = self.calcular_custo_capital(dados["selic"], dados["risco_brasil"])
            
            resultados[cenario] = {
                "preco": preco,
                "market_cap": market_cap,
                "ke": ke,
                "selic": dados["selic"],
                "risco": dados["risco_brasil"],
                "confianca": dados["confidence"],
                "ipos": dados["ipos_ano"]
            }
        
        # Tabela comparativa
        print("\n📊 TABELA COMPARATIVA")
        print("-" * 80)
        print(f"{'Indicador':<25} {'Hoje (14.5%)':<20} {'SELIX':<20} {'TrampoForte':<20}")
        print("-" * 80)
        
        for indicador, key in [
            ("Preço B3SA3 (R$)", "preco"),
            ("Market Cap (R$ bilhões)", "market_cap"),
            ("Selic (%)", "selic"),
            ("Custo Capital (Ke)", "ke"),
            ("Risco Brasil (bps)", "risco"),
            ("Confiança (%)", "confianca"),
            ("IPOs/ano", "ipos")
        ]:
            hoje_val = resultados["hoje"][key]
            selix_val = resultados["selix"][key]
            trampo_val = resultados["trampoforte"][key]
            
            if "bilhões" in indicador:
                hoje_fmt = f"R$ {hoje_val/1e9:.1f}B"
                selix_fmt = f"R$ {selix_val/1e9:.1f}B"
                trampo_fmt = f"R$ {trampo_val/1e9:.1f}B"
            elif "Risco" in indicador:
                hoje_fmt = f"{hoje_val*10000:.0f}bps"
                selix_fmt = f"{selix_val*10000:.0f}bps"
                trampo_fmt = f"{trampo_val*10000:.0f}bps"
            elif "Confiança" in indicador:
                hoje_fmt = f"{hoje_val*100:.0f}%"
                selix_fmt = f"{selix_val*100:.0f}%"
                trampo_fmt = f"{trampo_val*100:.0f}%"
            elif "%" in indicador or "IPOs" in indicador:
                hoje_fmt = f"{hoje_val*100:.1f}%" if "Selic" in indicador or "Custo" in indicador else f"{hoje_val:.0f}"
                selix_fmt = f"{selix_val*100:.1f}%" if "Selic" in indicador or "Custo" in indicador else f"{selix_val:.0f}"
                trampo_fmt = f"{trampo_val*100:.1f}%" if "Selic" in indicador or "Custo" in indicador else f"{trampo_val:.0f}"
            else:
                hoje_fmt = f"R$ {hoje_val:.2f}" if "Preço" in indicador else f"{hoje_val:.0f}"
                selix_fmt = f"R$ {selix_val:.2f}" if "Preço" in indicador else f"{selix_val:.0f}"
                trampo_fmt = f"R$ {trampo_val:.2f}" if "Preço" in indicador else f"{trampo_val:.0f}"
            
            print(f"{indicador:<25} {hoje_fmt:<20} {selix_fmt:<20} {trampo_fmt:<20}")
        
        print("-" * 80)
        
        # Crescimento percentual
        print("\n📈 CRESCIMENTO PERCENTUAL")
        print("-" * 50)
        
        for indicador, key in [
            ("Preço B3SA3", "preco"),
            ("Market Cap", "market_cap")
        ]:
            hoje = resultados["hoje"][key]
            selix = resultados["selix"][key]
            trampo = resultados["trampoforte"][key]
            
            cresc_selix = ((selix / hoje) - 1) * 100
            cresc_trampo = ((trampo / hoje) - 1) * 100
            
            print(f"{indicador:<20} SELIX: +{cresc_selix:.0f}%   TrampoForte: +{cresc_trampo:.0f}%")
        
        # Gráfico ASCII
        print("\n📊 GRÁFICO COMPARATIVO (Market Cap em R$ Bilhões)")
        print("-" * 50)
        
        max_mc = max(r["market_cap"] for r in resultados.values())
        bar_max = 50  # caracteres máximo do gráfico
        
        for cenario, cor in [("hoje", "🔴"), ("selix", "🟡"), ("trampoforte", "🟢")]:
            mc = resultados[cenario]["market_cap"]
            bar_size = int((mc / max_mc) * bar_max)
            bar = "█" * bar_size
            
            if cenario == "hoje":
                nome = "Hoje"
                label = f"{nome:15} {cor} {bar} R$ {mc/1e9:.0f}B"
            elif cenario == "selix":
                nome = "SELIX"
                label = f"{nome:15} {cor} {bar} R$ {mc/1e9:.0f}B"
            else:
                nome = "TrampoForte"
                label = f"{nome:15} {cor} {bar} R$ {mc/1e9:.0f}B"
            
            print(label)
        
        # Resumo final
        print("\n" + "=" * 80)
        print("🎯 CONCLUSÃO FINAL")
        print("=" * 80)
        
        hoje_mc = resultados["hoje"]["market_cap"] / 1e9
        selix_mc = resultados["selix"]["market_cap"] / 1e9
        trampo_mc = resultados["trampoforte"]["market_cap"] / 1e9
        
        print(f"""
🏦 MARKET CAP B3 (B3SA3):

┌─────────────────────────────────────────────────────────────────┐
│  HOJE (Selic 14.5%, IPOs congelados)                            │
│  → Market Cap: R$ {hoje_mc:.0f}B                                 │
│  → Preço: R$ {resultados['hoje']['preco']:.2f}                   │
├─────────────────────────────────────────────────────────────────┤
│  COM SELIX (Selic 9.48%)                                        │
│  → Market Cap: R$ {selix_mc:.0f}B                                │
│  → Preço: R$ {resultados['selix']['preco']:.2f}                  │
│  → CRESCIMENTO: +{(selix_mc/hoje_mc -1)*100:.0f}%                │
├─────────────────────────────────────────────────────────────────┤
│  COM TRAMPOFORTE (SELIX + Segurança Trabalhista)                │
│  → Market Cap: R$ {trampo_mc:.0f}B                               │
│  → Preço: R$ {resultados['trampoforte']['preco']:.2f}            │
│  → CRESCIMENTO: +{(trampo_mc/hoje_mc -1)*100:.0f}%               │
└─────────────────────────────────────────────────────────────────┘

✅ RESULTADO: TrampoForte gera +{((trampo_mc/selix_mc)-1)*100:.0f}% adicional sobre SELIX
✅ RESULTADO FINAL: +{(trampo_mc/hoje_mc -1)*100:.0f}% sobre o valor atual
        """)
        
        return resultados

if __name__ == "__main__":
    analise = MarketCapB3()
    analise.gerar_relatorio_completo()
