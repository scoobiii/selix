#!/usr/bin/env python3
"""
Templates de posts com DISCLAIMER legal
"""

DISCLAIMER = "⚠️ Não é recomendação de investimento. Projeções baseadas em modelo matemático SELIX (Selic 9.48%)."

def adicionar_disclaimer(texto: str) -> str:
    """Adiciona disclaimer ao final do post"""
    if "DISCLAIMER" in texto or "não é recomendação" in texto.lower():
        return texto
    return f"{texto}\n\n{DISCLAIMER}"

# Exemplos de posts seguros
POST_GPA_SEGURO = f"""📊 PROJEÇÃO GPA (PCAR3) 2026-2030:

2026: R$ 1,96 (hoje)
2027: R$ 3,39
2028: R$ 5,87
2029: R$ 10,17
2030: R$ 17,60 (SELIX)

🏆 MÁX HIST: R$ 105,00 (2020)
💰 MKT CAP: R$ 5,5B → R$ 49B

✅ Modelo: Selic 9.48% + TrampoForte
#SELIX #TrampoForte #GPA

{DISCLAIMER}"""

POST_RAIZEN_SEGURO = f"""📊 PROJEÇÃO RAIZEN (RAIZ4) 2026-2030:

2026: R$ 0,34 (hoje)
2027: R$ 0,81
2028: R$ 1,95
2029: R$ 4,66
2030: R$ 11,15 (SELIX)

🏆 MÁX HIST: R$ 9,50 (2022)
💰 MKT CAP: R$ 1,4B → R$ 47B

✅ Modelo: Selic 9.48% + TrampoForte
#SELIX #TrampoForte #RAIZ4

{DISCLAIMER}"""

if __name__ == "__main__":
    print("✅ Templates com disclaimer carregados")
    print(f"\n📏 Tamanho do post GPA: {len(POST_GPA_SEGURO)} caracteres")
    print(f"📏 Tamanho do post RAIZEN: {len(POST_RAIZEN_SEGURO)} caracteres")
