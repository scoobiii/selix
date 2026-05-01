/- SELIX - Prova Corrigida (sintaxe Lean 4 padrão) -/

def inflacao : Float := 4.48
def roe : Float := 31.23

def teto_1_digito : Float := 9.99
def teto_juro_real : Float := inflacao + 5.0
def teto_roe : Float := roe * 0.95
def teto_global : Float := 1.39 * inflacao + 4.5

def min2 (a b : Float) : Float := if a < b then a else b
def min4 (a b c d : Float) : Float := min2 (min2 a b) (min2 c d)

def selix_bruto : Float := min4 teto_1_digito teto_juro_real teto_roe teto_global
def selix_final : Float := (Int.floor (selix_bruto / 0.25)).toFloat * 0.25

#eval selix_final
