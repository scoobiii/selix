import data.real.basic

def inflacao : ℝ := 4.48
def roe : ℝ := 31.23

def teto_1_digito : ℝ := 9.99
def teto_juro_real : ℝ := inflacao + 5.0
def teto_roe : ℝ := roe * 0.95
def teto_global : ℝ := 1.39 * inflacao + 4.5

def selix_bruto : ℝ := min (min (min teto_1_digito teto_juro_real) teto_roe) teto_global
def selix_final : ℝ := (⌊selix_bruto / 0.25⌋) * 0.25

theorem investment_grade : selix_final ≤ 9.99 :=
begin
  unfold selix_final,
  have h : ⌊selix_bruto / 0.25⌋ * 0.25 ≤ selix_bruto :=
    floor_mul_le_self selix_bruto (by norm_num),
  apply le_trans h,
  apply min_le_of_left_le (min_le_left _ _)
end

#eval selix_final
