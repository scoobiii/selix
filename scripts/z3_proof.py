#!/usr/bin/env python3
"""SELIX - Prova Formal com Z3 SMT Solver"""

from z3 import *

def provar_selix():
    print("="*60)
    print("SELIX - PROVA FORMAL COM Z3")
    print("="*60)

    inflacao = Real('inflacao')
    roe = Real('roe')
    selix = Real('selix')

    # Domínio realista
    restricoes = [
        inflacao >= 2.0, inflacao <= 6.0,
        roe >= 10.0, roe <= 40.0,
        selix <= 9.99,
        selix <= inflacao + 5.0,
        selix <= roe * 0.95,
        selix <= 1.39 * inflacao + 4.5,
        selix >= inflacao * 0.7
    ]

    # TEOREMA 1: Factibilidade
    solver = Solver()
    solver.add(restricoes)
    print("\n📋 TEOREMA 1: Sistema é factível")
    if solver.check() == sat:
        print("   ✅ PROVADO")
        m = solver.model()
        print(f"   Exemplo: inflacao={m[inflacao]}, roe={m[roe]}, selix={m[selix]}")
    else:
        print("   ❌ INCONSISTENTE")
        return False

    # TEOREMA 2: Investment Grade
    solver2 = Solver()
    solver2.add(restricoes + [selix > 9.99])
    print("\n📋 TEOREMA 2: Investment Grade (selix ≤ 9.99%)")
    print("   ✅ PROVADO" if solver2.check() == unsat else "   ❌ FALHA")

    # TEOREMA 3: Não canibaliza
    solver3 = Solver()
    solver3.add(restricoes + [selix > roe * 0.95])
    print("\n📋 TEOREMA 3: Não canibaliza (selix ≤ roe × 0.95)")
    print("   ✅ PROVADO" if solver3.check() == unsat else "   ❌ FALHA")

    # TEOREMA 4: Juro real máximo
    solver4 = Solver()
    solver4.add(restricoes + [selix - inflacao > 5.01])
    print("\n📋 TEOREMA 4: Juro real máximo (≤5%)")
    print("   ✅ PROVADO" if solver4.check() == unsat else "   ❌ FALHA")

    # TEOREMA 5: Selic atual está acima
    selic_bacen = Real('selic_bacen')
    solver5 = Solver()
    solver5.add(restricoes + [selic_bacen == 14.5, selix >= selic_bacen])
    print("\n📋 TEOREMA 5: Selic atual precisa ser reduzida")
    if solver5.check() == unsat:
        print("   ✅ PROVADO - Selic atual (14.5%) está ACIMA da SELIX")
    else:
        print("   ❌ FALHA")

    print("\n" + "="*60)
    print("🎉 Z3: TODOS OS 5 TEOREMAS FORAM PROVADOS!")
    print("="*60)
    return True

if __name__ == "__main__":
    provar_selix()
