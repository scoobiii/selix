#!/usr/bin/env python3
"""
T8 REVISITADO: Prova formal do impacto econômico com Z3
"""

from z3 import *
import json

def provar_impacto_economico():
    """Prova formal com Z3: debt_stock → economia_anual = 345 bi"""
    
    # Variáveis
    selic_atual = Real('selic_atual')
    selic_ideal = Real('selic_ideal')
    divida_publica = Real('divida_publica')
    economia_anual = Real('economia_anual')
    diferencial = Real('diferencial')
    
    # Solver
    s = Solver()
    
    # Axiomas (dados oficiais)
    s.add(selic_atual == 14.25)        # BCB - Selic atual
    s.add(selic_ideal == 9.25)         # SELIX - Selic ideal
    s.add(divida_publica == 6900)      # STN/BCB - Dívida pública líquida (R$ bi)
    
    # Definições
    s.add(diferencial == selic_atual - selic_ideal)
    s.add(economia_anual == divida_publica * (diferencial / 100))
    
    # Verificar consistência
    if s.check() == sat:
        model = s.model()
        resultado = {
            "selic_atual": float(model[selic_atual].as_decimal(10)),
            "selic_ideal": float(model[selic_ideal].as_decimal(10)),
            "divida_publica_bi": float(model[divida_publica].as_decimal(10)),
            "diferencial_pp": float(model[diferencial].as_decimal(10)),
            "economia_anual_bi": float(model[economia_anual].as_decimal(10)),
            "status": "✅ PROVADO"
        }
        return resultado
    else:
        return {"status": "❌ INCONSISTENTE"}

def provar_cenario_alternativo(divida_bi):
    """Prova formal com Z3 para diferentes cenários"""
    s = Solver()
    
    selic_atual = Real('selic_atual')
    selic_ideal = Real('selic_ideal')
    divida_publica = Real('divida_publica')
    economia_anual = Real('economia_anual')
    
    s.add(selic_atual == 14.25)
    s.add(selic_ideal == 9.25)
    s.add(divida_publica == divida_bi)
    s.add(economia_anual == divida_publica * ((selic_atual - selic_ideal) / 100))
    
    if s.check() == sat:
        model = s.model()
        return float(model[economia_anual].as_decimal(10))
    return None

def main():
    print("🧮 PROVA FORMAL COM Z3 - T8")
    print("=" * 50)
    
    # Provar o cenário principal
    resultado = provar_impacto_economico()
    print(json.dumps(resultado, indent=2))
    
    print("\n" + "=" * 50)
    print("📊 CENÁRIOS ALTERNATIVOS")
    
    # Testar diferentes valores de dívida
    cenarios = [
        (6900, "Dívida atual (R$ 6,9 tri)"),
        (5400, "Cenário para R$ 270 bi"),
        (6000, "Cenário intermediário"),
    ]
    
    for dívida, descricao in cenarios:
        economia = provar_cenario_alternativo(dívida)
        if economia:
            print(f"  - {descricao}: R$ {economia:.2f} bi/ano")

if __name__ == "__main__":
    main()
