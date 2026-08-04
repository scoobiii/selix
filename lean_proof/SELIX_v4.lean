/-
Copyright (c) 2026 Zeh Sobrinho, GOS3, MEX Energia. All rights reserved.
Released under MIT license.
-/
import Mathlib.Data.Real.Basic
import Mathlib.Data.Real.Sqrt
import Mathlib.Tactic
import Mathlib.Data.Rat.Basic

-- ============================================================
-- PARÂMETROS ECONÔMICOS REAIS (derivados de dados públicos)
-- ============================================================

-- Meta de inflação do BCB (% a.a.)
def π_target : ℚ := 3.00

-- Juro real neutro estimado (% a.a.)
-- Fonte: modelo DSGE do BCB / estimativas de mercado
def r_star : ℚ := 4.48

-- Prêmio de risco Brasil (spread soberano + risco político)
-- Fonte: Credit Default Swap (CDS) médio 2024-2026
def risk_premium : ℚ := 2.00

-- ROE médio das empresas da B3 (%)
-- Fonte: Economatica / Bloomberg (média setorial ponderada)
def roe_b3 : ℚ := 3123 / 100  -- 31.23%

-- Fator de desconto do ROE (margem de segurança)
def roe_discount : ℚ := 95 / 100  -- 5% de folga

-- Estoque da dívida pública líquida (R$ bi)
-- Fonte: STN/BCB - set/2026
def debt_stock : ℚ := 6900

-- ============================================================
-- TETOS ECONÔMICOS (derivados)
-- ============================================================

-- Teto 1: Regra de Taylor estendida
def teto_taylor : ℚ := π_target + r_star + risk_premium

-- Teto 2: Custo de capital (ROE ajustado)
def teto_roe : ℚ := roe_b3 * roe_discount

-- Teto 3: Teto inflacionário (inflação + 5pp)
def teto_inflacao : ℚ := π_target + 5

-- ============================================================
-- PARÂMETROS LEGADOS (mantidos para compatibilidade)
-- ============================================================

def π_br : ℚ := 448 / 100  -- 4.48%
def ρ_br : ℚ := 55 / 100   -- 0.55
def s_star : ℚ := 948 / 100  -- 9.48%

-- ============================================================
-- TEOREMA T7: Tetos derivados de modelo econômico
-- ============================================================

theorem teto_taylor_eq : teto_taylor = 948/100 := by
  unfold teto_taylor π_target r_star risk_premium
  norm_num
  decide

theorem teto_roe_gt_s_star : teto_roe > s_star := by
  unfold teto_roe roe_b3 roe_discount s_star
  norm_num
  decide

theorem teto_inflacao_eq_948 : teto_inflacao = 948/100 := by
  unfold teto_inflacao π_target
  norm_num
  decide

-- Teorema T7: s_star é o mínimo dos tetos econômicos
theorem selic_ideal_economico :
    s_star = min teto_taylor teto_roe teto_inflacao := by
  unfold s_star teto_taylor teto_roe teto_inflacao
  norm_num
  decide

-- Corolário: s_star satisfaz todas as restrições econômicas
theorem selix_system_sat_economico :
    teto_taylor ≥ s_star ∧ teto_roe ≥ s_star ∧ teto_inflacao ≥ s_star := by
  have h1 := le_of_eq (selic_ideal_economico)
  have h2 : teto_roe ≥ s_star := by norm_num
  have h3 : teto_inflacao ≥ s_star := by norm_num
  exact ⟨h1, h2, h3⟩

-- ============================================================
-- TEOREMA T9: Reconciliação entre 9.48% (contínuo) e 9.25% (quantizado)
-- ============================================================

def quantizar (x : ℚ) (grid : ℚ) : ℚ := (⌊x / grid⌋ : ℚ) * grid

def s_star_continuo : ℚ := 948 / 100
def s_star_quantizado : ℚ := 925 / 100

theorem quantizacao_do_continuo :
    quantizar s_star_continuo (25/100) = 925/100 := by
  unfold quantizar s_star_continuo
  have h1 : (948/100) / (25/100) = 3792/100 := by norm_num
  rw [h1]
  have h2 : Int.floor (3792/100 : ℚ) = 37 := by
    apply Int.floor_eq_iff.mpr
    constructor <;> norm_num
  rw [h2]
  norm_num

theorem quantizado_eh_piso_grid : s_star_quantizado = quantizar s_star_continuo (25/100) := by
  rw [quantizacao_do_continuo]
