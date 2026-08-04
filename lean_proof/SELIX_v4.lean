/-
Copyright (c) 2026 Zeh Sobrinho, GOS3, MEX Energia. All rights reserved.
Released under MIT license.
Padrão GOS3: Python ↔ Lean sincronizados. Números do core.py (ago/2026).
-/
import Mathlib.Data.Real.Basic
import Mathlib.Tactic
import Mathlib.Data.Rat.Basic

-- ============================================================
-- Parâmetros do core.py (fonte de verdade)
-- ============================================================
def inflacao : ℚ := 448 / 100          -- 4.48
def juro_real_maximo : ℚ := 5
def relacao_global : ℚ := 1
def premio_risco : ℚ := 2
def teto_1_digito : ℚ := 999 / 100     -- 9.99

-- ============================================================
-- Derivação dos tetos (idêntica ao __init__ + calcular_selix_continuo)
-- ============================================================
def teto_juro_real : ℚ := inflacao + juro_real_maximo          -- 9.48
def teto_global : ℚ := (relacao_global * inflacao) + premio_risco  -- 6.48

def s_star_continuo : ℚ := min teto_1_digito (min teto_juro_real teto_global)  -- 6.48

-- ============================================================
-- Quantização no grid do Copom (0.25)
-- ============================================================
def quantizar (x : ℚ) (grid : ℚ) : ℚ := (⌊x / grid⌋ : ℚ) * grid

def s_star : ℚ := quantizar s_star_continuo (25 / 100)   -- 6.25

-- ============================================================
-- Provas
-- ============================================================
theorem teto_global_correto : teto_global = 648 / 100 := by
  unfold teto_global relacao_global inflacao premio_risco
  norm_num

theorem s_star_continuo_correto : s_star_continuo = 648 / 100 := by
  unfold s_star_continuo teto_1_digito teto_juro_real teto_global
  unfold inflacao juro_real_maximo relacao_global premio_risco
  norm_num

theorem quantizacao_gos3 :
  quantizar (648 / 100) (25 / 100) = 625 / 100 := by
  unfold quantizar
  norm_num
  decide

theorem s_star_gos3 : s_star = 625 / 100 := by
  unfold s_star s_star_continuo
  unfold teto_1_digito teto_juro_real teto_global
  unfold inflacao juro_real_maximo relacao_global premio_risco quantizar
  norm_num
  decide

-- Teorema final GOS3: Python e Lean concordam em 6.25
theorem selix_gos3_completo :
  s_star = 625 / 100 ∧
  quantizar (648 / 100) (25 / 100) = 625 / 100 := by
  constructor
  · exact s_star_gos3
  · exact quantizacao_gos3
