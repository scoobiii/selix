/- SELIX - Prova Simplificada (não requer mathlib) -/

def inflacao : Float := 4.48
def roe : Float := 31.23

def teto_1_digito : Float := 9.99
def teto_juro_real : Float := inflacao + 5.0
def teto_roe : Float := roe * 0.95
def teto_global : Float := 1.39 * inflacao + 4.5

def selix_bruto : Float :=
  let t1 := teto_1_digito
  let t2 := teto_juro_real
  let t3 := teto_roe
  let t4 := teto_global in
  if t1 < t2 then
    if t1 < t3 then
      if t1 < t4 then t1 else t4
    else
      if t3 < t4 then t3 else t4
  else
    if t2 < t3 then
      if t2 < t4 then t2 else t4
    else
      if t3 < t4 then t3 else t4

def selix_final : Float :=
  ((selix_bruto / 0.25).floor) * 0.25

#eval selix_final
