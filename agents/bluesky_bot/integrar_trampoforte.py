#!/usr/bin/env python3
"""
Integração SELIX + TrampoForte
Propõe ação legislativa para priorizar PLR em RJ
"""

import json
from datetime import datetime

# Proposta de emenda ao TrampoForte
PROPOSTA_TRAMPOFORTE = """
ARTIGO 1º: Em situação de recuperação judicial, o pagamento de PLR 
e demais direitos trabalhistas tem prioridade ABSOLUTA sobre 
qualquer outra obrigação, incluindo financeiras.

ARTIGO 2º: Quando a Taxa Selic for superior ao ROI da empresa, 
considera-se configurada "crise externa", suspendendo-se 
automaticamente a exigibilidade de juros sobre dívidas 
trabalhistas.

ARTIGO 3º: Aplica-se a empresas onde:
I - Selic > ROI por 3 meses consecutivos
II - Empresa em RJ ou pré-RJ
III - PLR atrasado > 90 dias
"""

def gerar_post_trampoforte():
    """Gera post sobre TrampoForte"""
    texto = f"""{PROPOSTA_TRAMPOFORTE[:250]}...

🔗 github.com/scoobiii/TrampoForte
#TrampoForte #PLR #RecuperaçãoJudicial"""

    return texto

if __name__ == "__main__":
    print("📜 PROPOSTA TRAMPOFORTE PARA PLR EM RJ")
    print("=" * 50)
    print(PROPOSTA_TRAMPOFORTE)
    print("\n📱 Post sugerido para Bluesky:")
    print("-" * 50)
    print(gerar_post_trampoforte())
