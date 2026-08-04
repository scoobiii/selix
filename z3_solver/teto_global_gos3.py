#!/usr/bin/env python3
"""SELIX GOS3 — Verificação do teto global com Z3 (s_star = 6.25)"""
from z3 import *

def verificar_teto_global():
    inflacao       = RealVal("4.48")
    juro_real_max  = RealVal("5")
    relacao_global = RealVal("1")
    premio_risco   = RealVal("2")
    teto_1_digito  = RealVal("9.99")
    grid           = RealVal("0.25")
    roe            = RealVal("31.23")
    folga_roe      = RealVal("0.95")

    teto_juro_real = inflacao + juro_real_max
    teto_global    = relacao_global * inflacao + premio_risco
    teto_roe       = roe * folga_roe

    s_continuo = Real("s_continuo")
    s_star     = Real("s_star")

    sol = Solver()

    # min dos quatro tetos
    sol.add(s_continuo ==
        If(teto_global <= teto_juro_real,
           If(teto_global <= teto_1_digito,
              If(teto_global <= teto_roe, teto_global, teto_roe),
              If(teto_1_digito <= teto_roe, teto_1_digito, teto_roe)),
           If(teto_juro_real <= teto_1_digito,
              If(teto_juro_real <= teto_roe, teto_juro_real, teto_roe),
              If(teto_1_digito <= teto_roe, teto_1_digito, teto_roe))))

    # quantização floor(x/0.25)*0.25
    sol.add(s_star == ToReal(ToInt(s_continuo / grid)) * grid)

    # assertivas GOS3
    sol.add(teto_global == RealVal("6.48"))
    sol.add(s_continuo  == RealVal("6.48"))
    sol.add(s_star      == RealVal("6.25"))

    r = sol.check()
    print("Z3 check:", r)
    if r == sat:
        m = sol.model()
        print("teto_global =", m.evaluate(teto_global))
        print("s_continuo  =", m.evaluate(s_continuo))
        print("s_star      =", m.evaluate(s_star))
        print("✅ Teto global GOS3 verificado pelo Z3")
        return True
    print("❌ Insatisfatível")
    return False

if __name__ == "__main__":
    verificar_teto_global()
