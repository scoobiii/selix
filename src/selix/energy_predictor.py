"""Energy Predictor - Regras de mistura E% e B% baseadas no Brent"""

class EnergyPredictor:
    
    # Gatilhos para mistura de etanol na gasolina (E%)
    GATILHOS_E = [
        {"limite": 200, "mistura": "E42", "tempo": "12h", "status": "EMERGÊNCIA MÁXIMA", "cor": "🔴"},
        {"limite": 150, "mistura": "E40", "tempo": "24h", "status": "EMERGÊNCIA", "cor": "🔴"},
        {"limite": 120, "mistura": "E35", "tempo": "48h", "status": "CRISE", "cor": "🟠"},
        {"limite": 90, "mistura": "E30", "tempo": "72h", "status": "ALERTA", "cor": "🟡"},
        {"limite": 70, "mistura": "E27", "tempo": "normal", "status": "NORMAL", "cor": "🟢"},
    ]
    
    # Gatilhos para mistura de biodiesel no diesel (B%)
    GATILHOS_B = [
        {"limite": 150, "mistura": "B25", "tempo": "12h", "status": "EMERGÊNCIA", "cor": "🔴"},
        {"limite": 120, "mistura": "B20", "tempo": "24h", "status": "CRÍTICO", "cor": "🟠"},
        {"limite": 90, "mistura": "B15", "tempo": "48h", "status": "ALERTA", "cor": "🟡"},
        {"limite": 70, "mistura": "B14", "tempo": "normal", "status": "NORMAL", "cor": "🟢"},
    ]
    
    # Capacidade de termelétricas flex (MW)
    TERMELETRICAS = {
        "etanol": {"capacidade_mw": 1200, "usinas": 12, "empresas": ["Raízen", "BP Bioenergy", "Cargill", "São Martinho"]},
        "gnv": {"capacidade_mw": 15000, "usinas": 35, "empresas": ["Eletrobras", "Engie", "Petrobras", "Shell"]},
        "biodiesel": {"capacidade_mw": 800, "usinas": 8, "empresas": ["Cargill", "Granol", "Bunge"]},
        "biogas": {"capacidade_mw": 300, "usinas": 5, "empresas": ["CESP", "Raízen", "Atvos"]},
    }
    
    @classmethod
    def get_mistura_e(cls, brent_preco):
        """Recomenda mistura de etanol baseada no Brent"""
        for gatilho in cls.GATILHOS_E:
            if brent_preco > gatilho["limite"]:
                return {k: v for k, v in gatilho.items() if k != "limite"}
        return {k: v for k, v in cls.GATILHOS_E[-1].items() if k != "limite"}
    
    @classmethod
    def get_mistura_b(cls, brent_preco):
        """Recomenda mistura de biodiesel baseada no Brent"""
        for gatilho in cls.GATILHOS_B:
            if brent_preco > gatilho["limite"]:
                return {k: v for k, v in gatilho.items() if k != "limite"}
        return {k: v for k, v in cls.GATILHOS_B[-1].items() if k != "limite"}
    
    @classmethod
    def get_geracao_termica(cls, brent_preco):
        """Recomenda acionamento de termelétricas flex"""
        if brent_preco > 150:
            return {
                "status": "ACIONAMENTO TOTAL",
                "capacidade_utilizada": "100%",
                "recomendacao": "Acionar TODAS as usinas flex",
                "potencial_mw": sum(t["capacidade_mw"] for t in cls.TERMELETRICAS.values())
            }
        elif brent_preco > 120:
            return {
                "status": "ACIONAMENTO PARCIAL",
                "capacidade_utilizada": "70%",
                "recomendacao": "Acionar usinas a gás e etanol",
                "potencial_mw": cls.TERMELETRICAS["gnv"]["capacidade_mw"] + cls.TERMELETRICAS["etanol"]["capacidade_mw"]
            }
        elif brent_preco > 90:
            return {
                "status": "ACIONAMENTO MÍNIMO",
                "capacidade_utilizada": "40%",
                "recomendacao": "Acionar apenas usinas a gás",
                "potencial_mw": cls.TERMELETRICAS["gnv"]["capacidade_mw"]
            }
        else:
            return {
                "status": "DESLIGADAS",
                "capacidade_utilizada": "0%",
                "recomendacao": "Priorizar hidrelétricas e renováveis",
                "potencial_mw": 0
            }
    
    @classmethod
    def get_resumo_energetico(cls, brent_preco):
        """Resumo completo do cenário energético"""
        return {
            "brent_usd": brent_preco,
            "mistura_etanol": cls.get_mistura_e(brent_preco),
            "mistura_biodiesel": cls.get_mistura_b(brent_preco),
            "geracao_termica": cls.get_geracao_termica(brent_preco),
            "termicas_flex": cls.TERMELETRICAS,
            "capacidade_total_mw": sum(t["capacidade_mw"] for t in cls.TERMELETRICAS.values())
        }

if __name__ == "__main__":
    # Teste com diferentes preços de Brent
    print("=" * 60)
    print("🔬 ENERGY PREDICTOR - TESTE")
    print("=" * 60)
    
    for brent in [80, 100, 130, 170]:
        print(f"\n🛢️ BRENT: US$ {brent}")
        e = EnergyPredictor.get_mistura_e(brent)
        b = EnergyPredictor.get_mistura_b(brent)
        g = EnergyPredictor.get_geracao_termica(brent)
        print(f"   E%: {e['mistura']} ({e['status']})")
        print(f"   B%: {b['mistura']} ({b['status']})")
        print(f"   Térmicas: {g['status']}")
