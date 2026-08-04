/-
Copyright (c) 2026 Zeh Sobrinho, GOS3, MEX Energia. All rights reserved.
Released under MIT license.
Padrão GOS3: Derivação formal de parâmetros a partir de modelo econômico real.
-/
import Mathlib.Data.Real.Basic
import Mathlib.Tactic
import Mathlib.Data.Rat.Basic

-- ============================================================
-- 1. MODELO ECONÔMICO (AXIOMAS E DEFINIÇÕES)
-- ============================================================

-- Definição de um modelo econômico sustentável
structure ModeloEconomico where
  inflacao : ℚ
  juro_real_max : ℚ
  roe_medio : ℚ
  folga_roe : ℚ
  premio_risco_pais : ℚ
  teto_prudencial : ℚ

-- Axioma: A Selic não deve canibalizar o setor produtivo (ROE)
def teto_produtivo (m : ModeloEconomico) : ℚ := m.roe_medio * m.folga_roe

-- Axioma: A Selic deve respeitar o juro real máximo suportável pelo Tesouro
def teto_fiscal (m : ModeloEconomico) : ℚ := m.inflacao + m.juro_real_max

-- Axioma: A Selic deve cobrir a inflação mais o prêmio de risco país
def teto_monetario (m : ModeloEconomico) : ℚ := m.inflacao + m.premio_risco_pais

-- Definição da Selic Ideal Contínua (mínimo dos tetos)
def selic_ideal_continua (m : ModeloEconomico) : ℚ :=
  min m.teto_prudencial (min (teto_produtivo m) (min (teto_fiscal m) (teto_monetario m)))

-- Quantização no grid do Copom (0.25)
def quantizar (x : ℚ) (grid : ℚ) : ℚ := (⌊x / grid⌋ : ℚ) * grid

def selic_ideal_quantizada (m : ModeloEconomico) : ℚ :=
  quantizar (selic_ideal_continua m) (25 / 100)

-- ============================================================
-- 2. INSTÂNCIA DO MODELO (DADOS AGOSTO/2026)
-- ============================================================

def selix_v4_model : ModeloEconomico := {
  inflacao := 448 / 100,          -- 4.48% (IPCA-12)
  juro_real_max := 5,             -- 5.00% (Limite fiscal)
  roe_medio := 3123 / 100,        -- 31.23% (Média 6 pontos B3)
  folga_roe := 95 / 100,          -- 0.95 (Margem de segurança)
  premio_risco_pais := 5,         -- 5.00% (Prêmio de risco ajustado)
  teto_prudencial := 999 / 100    -- 9.99% (Investment Grade)
}

-- ============================================================
-- 3. TEOREMAS DE DERIVAÇÃO
-- ============================================================

theorem teto_fiscal_val : teto_fiscal selix_v4_model = 948 / 100 := by
  unfold teto_fiscal selix_v4_model
  norm_num

theorem teto_produtivo_val : teto_produtivo selix_v4_model = 296685 / 10000 := by
  unfold teto_produtivo selix_v4_model
  norm_num

theorem teto_monetario_val : teto_monetario selix_v4_model = 948 / 100 := by
  unfold teto_monetario selix_v4_model
  norm_num

-- Prova que a Selic Contínua é 9.48%
theorem selic_continua_val : selic_ideal_continua selix_v4_model = 948 / 100 := by
  unfold selic_ideal_continua
  rw [teto_fiscal_val, teto_produtivo_val, teto_monetario_val]
  unfold selix_v4_model
  norm_num

-- Prova a quantização 9.48 -> 9.25
theorem selic_quantizada_val : selic_ideal_quantizada selix_v4_model = 925 / 100 := by
  unfold selic_ideal_quantizada
  rw [selic_continua_val]
  unfold quantizar
  norm_num
  decide

-- ============================================================
-- 4. IMPACTO ECONÔMICO (ECONOMIA DE R$ 345 BI)
-- ============================================================

def divida_publica : ℚ := 6900    -- R$ 6.9 tri (DPL)
def selic_atual : ℚ := 1425 / 100 -- 14.25%

def economia_anual (m : ModeloEconomico) (divida : ℚ) (atual : ℚ) : ℚ :=
  divida * (atual - selic_ideal_quantizada m) / 100

theorem economia_anual_val : economia_anual selix_v4_model divida_publica selic_atual = 345 := by
  unfold economia_anual
  rw [selic_quantizada_val]
  unfold selic_atual divida_publica
  norm_num

-- ============================================================
-- 5. TEOREMA FINAL: ZERO GAP
-- ============================================================

theorem selix_v4_final :
  selic_ideal_quantizada selix_v4_model = 925 / 100 ∧
  economia_anual selix_v4_model divida_publica selic_atual = 345 := by
  constructor
  · exact selic_quantizada_val
  · exact economia_anual_val
