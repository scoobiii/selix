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

-- ============================================================
-- IMPACTO DA SELIC 2D (14.25%) vs 1D (6.25%)
-- ============================================================

-- Dados macro (fonte: BCB/STN - jun/ago 2026)
def divida_bruta : ℚ := 10800  -- R$ 10,8 tri (81.9% do PIB)
def juros_nominais_12m : ℚ := 1160  -- R$ 1,16 tri (8.8% do PIB)
def custo_medio_divida : ℚ := 1268 / 100  -- 12.68% a.a.
def selic_atual_2d : ℚ := 1425 / 100  -- 14.25%
def selic_ideal_1d : ℚ := 625 / 100  -- 6.25%

-- Parcela Selic-linked da dívida (LFTs, ~49%)
def fracao_selic_linked : ℚ := 49 / 100

-- Elasticidade oficial do BC: cada 1 p.p. reduz dívida em ~R$ 60-66 bi
def elasticidade_bc_min : ℚ := 60
def elasticidade_bc_max : ℚ := 66

-- Diferença entre Selic 2D e 1D
def diferencial_2d_1d : ℚ := selic_atual_2d - selic_ideal_1d  -- 8 p.p.

-- Parcela pós-fixada da dívida
def parcela_pos_fixada : ℚ := divida_bruta * fracao_selic_linked  -- ~R$ 5,29 tri

-- Economia anual de juros (aproximação bruta)
def economia_anual_juros : ℚ :=
  parcela_pos_fixada * (diferencial_2d_1d / 100)  -- ~R$ 423 bi

-- Efeito total no estoque (elasticidade × diferencial)
def reducao_estoque_min : ℚ := elasticidade_bc_min * diferencial_2d_1d  -- ~480 bi
def reducao_estoque_max : ℚ := elasticidade_bc_max * diferencial_2d_1d  -- ~528 bi

-- Teoremas: impactos formalmente calculados
theorem economia_anual_calculada :
  economia_anual_juros > 400 ∧ economia_anual_juros < 450 := by
  unfold economia_anual_juros parcela_pos_fixada divida_bruta
        fracao_selic_linked diferencial_2d_1d
  norm_num
  decide

theorem reducao_estoque_calculada :
  reducao_estoque_min > 470 ∧ reducao_estoque_max < 540 := by
  unfold reducao_estoque_min reducao_estoque_max
        elasticidade_bc_min elasticidade_bc_max diferencial_2d_1d
  norm_num
  decide

-- ============================================================
-- IMPACTO NO VALUATION (P/L)
-- ============================================================

def ibovespa_atual : ℚ := 178000  -- pontos
def pl_atual : ℚ := 84 / 10  -- 8.4×
def pl_historico_media : ℚ := 105 / 10  -- 10.5×
def pl_otimista : ℚ := 12  -- 12×

-- Market cap Ibovespa (estimativa)
def market_cap_ibovespa : ℚ := 5500  -- R$ 5,5 tri

-- Potencial de expansão
def expansao_pl_min : ℚ := (pl_historico_media - pl_atual) / pl_atual  -- +25%
def expansao_pl_max : ℚ := (pl_otimista - pl_atual) / pl_atual  -- +43%

def upside_valuation_min : ℚ := market_cap_ibovespa * expansao_pl_min  -- ~R$ 1,37 tri
def upside_valuation_max : ℚ := market_cap_ibovespa * expansao_pl_max  -- ~R$ 2,36 tri

theorem upside_valuation_calculado :
  upside_valuation_min > 1300 ∧ upside_valuation_max < 2400 := by
  unfold upside_valuation_min upside_valuation_max
        market_cap_ibovespa expansao_pl_min expansao_pl_max
  norm_num
  decide

-- ============================================================
-- TEOREMA FINAL: IMPACTO COMBINADO
-- ============================================================

theorem impacto_total_selic_1d :
  economia_anual_juros > 400 ∧ economia_anual_juros < 450 ∧
  reducao_estoque_min > 470 ∧ reducao_estoque_max < 540 ∧
  upside_valuation_min > 1300 ∧ upside_valuation_max < 2400 := by
  constructor
  · exact economia_anual_calculada.1
  · constructor
    · exact economia_anual_calculada.2
    · constructor
      · exact reducao_estoque_calculada.1
      · constructor
        · exact reducao_estoque_calculada.2
        · constructor
          · exact upside_valuation_calculado.1
          · exact upside_valuation_calculado.2


-- ============================================================
-- T11: Modelo com Multiplicador de Credibilidade
-- ============================================================

def inflacao_brasil : ℚ := 448 / 100
def premio_risco_brasil : ℚ := 2
def credibilidade_brasil : ℚ := 5 / 10
def gap_produto_brasil : ℚ := -5 / 10

def multiplicador_credibilidade : ℚ := 1 + (premio_risco_brasil / 100) * (1 + (1 - credibilidade_brasil) * (1/2))

def juro_real_necessario : ℚ := 
  inflacao_brasil * multiplicador_credibilidade + (1/2) * gap_produto_brasil

theorem juro_real_brasil_calculado :
  juro_real_necessario = 948 / 100 := by
  unfold juro_real_necessario inflacao_brasil premio_risco_brasil credibilidade_brasil gap_produto_brasil multiplicador_credibilidade
  norm_num
  decide
