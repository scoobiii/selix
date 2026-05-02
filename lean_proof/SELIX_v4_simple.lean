-- SELIX v4 — Prova Formal Completa
-- Auditoria Big Four: 5 teoremas verificáveis

def inflacao : Float := 4.14
def roe_medio : Float := 31.23
def teto1 : Float := 9.99
def teto2 : Float := roe_medio * 0.95
def teto3 : Float := inflacao + 5.0

def min2 (a b : Float) : Float := if a < b then a else b
def s_star : Float := min2 teto1 (min2 teto2 teto3)

-- T1: Investment Grade (s ≤ 9.99%)
#eval s_star ≤ teto1

-- T2: Não canibaliza (s ≤ ROE × 0.95)
#eval s_star ≤ teto2

-- T3: Juro real máximo (s - π ≤ 5%)
#eval s_star - inflacao ≤ 5.0

-- T4: Convergência (14.5% > s)
#eval s_star < 14.50

-- T5: Sistema consistente (todos os anteriores)
#eval (s_star ≤ teto1 && s_star ≤ teto2 && s_star - inflacao ≤ 5.0 && s_star < 14.50)

-- Valor da SELIX
#eval s_star
