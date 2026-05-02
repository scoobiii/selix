# SELIX: Um Modelo Matemático para a Determinação da Taxa Selic Ótima

**Autores:** Zeh Sobrinho¹, GOS3²

¹ MEX Energia — mex.eco.br | São Paulo, Brasil  
² Grupo de Otimização de Sistemas Econômicos

**Versão:** 3.0 | **Data:** 02 mai 2026 | **Status:** Working Paper

---

## Abstract

> We present SELIX (*Sistema de Equilíbrio Linear de Juros e Investment Grade*), a
> formal mathematical model that determines the optimal Brazilian benchmark rate (Selic)
> subject to five simultaneously binding constraints: sovereign investment-grade
> classification, non-cannibalization of private-sector return on equity, primary-surplus
> solvency of the National Treasury, convergence feasibility, and global system
> consistency. Using the Z3 SMT Solver (Microsoft Research) we prove all five theorems
> hold at **SELIX = 9.48 %** given current parameters (IPCA = 4.48 %, ROE = 31.23 %,
> Selic<sub>BCB</sub> = 14.50 %), implying a reduction of **502 basis points** achievable
> in approximately **10 months** at standard COPOM cadence. The model is open-source,
> reproducible, and falsifiable.

**JEL Codes:** E43 · E52 · E58 · H63 · D72 · O11  
**Keywords:** taxa Selic, juro neutro, investment grade, SMT Solver, Z3, otimização sob restrições,
política monetária discricionária, inconsistência temporal, economia política, PIB setorial, stakeholders

---

## 1. Introdução

A taxa Selic brasileira encerrou o ciclo de alta de 2024–2025 em **14,50 % a.a.** —
o maior nível em 19 anos, superior às taxas de referência de todas as economias
emergentes com grau de investimento comparável (Tabela 1). O custo fiscal desta
anomalia é expressivo: cada 100 bps acima do equilíbrio representa aproximadamente
**R$ 68 bilhões/ano** em despesas financeiras adicionais do Tesouro Nacional,
considerando estoque de DPMFi de R$ 6,8 trilhões (BCB, 2025).

A literatura canônica sobre regras de taxa de juros — Taylor (1993), Woodford (2003),
Clarida, Galí & Gertler (1999) — estabelece que a taxa nominal ótima é função da
inflação corrente, do hiato do produto e da taxa neutra real. O SELIX estende essa
abordagem ao incorporar **restrições institucionais observáveis** específicas ao Brasil:
(i) limiar de *rating* soberano, (ii) custo de oportunidade do capital privado e
(iii) sustentabilidade da dívida pública.

### 1.1 Problema de Pesquisa

> **Questão central:** Existe uma taxa Selic *s\** que satisfaz simultaneamente todas
> as restrições de solvência soberana, *investment grade*, não-canibalização do setor
> produtivo e convergência monetária? Em caso afirmativo, qual o valor e qual o caminho
> de convergência?

### 1.2 Contribuições

1. Formalização das cinco restrições como sistema de inequações lineares
2. Prova de satisfatibilidade via SMT Solver (Z3) — **reproducível em < 1 segundo**
3. Cálculo fechado de *s\** sem calibração bayesiana ou simulação estocástica
4. Análise de sensibilidade paramétrica com superfície de resposta

---

## 2. Revisão de Literatura

### 2.1 Regra de Taylor e Extensões

Taylor (1993) propôs:

$$
i_t = r^* + \pi_t + 0.5(\pi_t - \pi^*) + 0.5 y_t
$$

onde $i_t$ é a taxa nominal, $r^*$ a taxa neutra real, $\pi_t$ a inflação corrente,
$\pi^*$ a meta e $y_t$ o hiato do produto. A regra implica, para os parâmetros
brasileiros de maio/2026 (IPCA = 4,48 %, meta = 3,0 %, hiato ≈ 0 %):

$$
i_{Taylor} = 3.5 + 4.48 + 0.5(4.48 - 3.0) + 0 = 8.72\%
$$

O SELIX opera em faixa superior (9,48 %) pois incorpora o **prêmio de risco-país
estrutural** (CDS 5Y ≈ 150 bps) ausente na regra original.

### 2.2 Juro Neutro para Economias Emergentes

Holston, Laubach & Williams (2017) e Ferreira & Nakane (2015) estimam o juro neutro
real brasileiro entre **3,5 % e 5,0 %**. O FMI (WEO Apr/2026) aponta convergência
global do juro neutro real para 2,5–3,5 %. O SELIX adota $r^*_{BR} = 3.5\%$ como
piso conservador.

### 2.3 Comparação Internacional (Tabela 1)

| País | Rating S&P | Taxa nominal | Juro real | SELIX equiv. |
|------|-----------|-------------|-----------|--------------|
| México | BBB | 9,50 % | 4,82 % | 9,30 % |
| Colombia | BB+ | 9,75 % | 5,07 % | 9,55 % |
| Brasil | BB | **14,50 %** | **10,02 %** | **9,48 %** |
| África do Sul | BB- | 8,25 % | 3,95 % | — |
| Turquia | B+ | 42,50 % | 9,50 % | — |
| Índia | BBB- | 6,25 % | 1,77 % | — |

*Fontes: BCB, Banxico, Banco de la República, SARB, TCMB, RBI — mai/2026.*

O Brasil possui **o maior juro real entre emergentes com rating BB ou superior**,
sugerindo desalinhamento sistemático não justificado pelos fundamentos.

---

## 3. Modelo SELIX

### 3.1 Definições

Seja $s \in \mathbb{R}_{>0}$ a taxa Selic anual em percentual. Definem-se:

| Símbolo | Descrição | Valor (mai/2026) | Fonte |
|---------|-----------|-----------------|-------|
| $\pi$ | IPCA acumulado 12 meses | 4,48 % | BCB SGS 13522 |
| $\rho$ | ROE médio IBOVESPA | 31,23 % | B3 Ranking abr/2026 |
| $s_{BCB}$ | Selic corrente | 14,50 % | BCB, COPOM 03/2026 |
| $r^*$ | Juro neutro global | 3,50 % | IMF WEO 2026 |
| $\phi$ | Fator de ajuste emergentes | 1,39 | Holston et al. 2017 |
| $\delta$ | Prêmio de risco-Brasil | 4,50 pp | CDS 5Y médio 2025 |

### 3.2 As Cinco Restrições Formais

**R1 — Investment Grade:**

$$
s \leq 9{,}99\%
$$

*Rationale:* S&P, Moody's e Fitch documentam que economias com juro real > 5,5 %
sistematicamente não mantêm grau de investimento. O limiar de 9,99 % corresponde ao
máximo nominal consistente com inflação alvo de 3 % e juro real de 6,99 % — ainda
acima do limite, mas teto conservador.

**R2 — Não-canibalização do setor produtivo:**

$$
s \leq \rho \cdot 0{,}95
$$

*Rationale:* Quando $s \geq \rho$, o capital migra de atividade produtiva para renda
fixa soberana (crowding-out financeiro). O fator 0,95 preserva margem mínima de
atratividade do capital de risco.

**R3 — Solvência do Tesouro (juro real):**

$$
s - \pi \leq 5{,}00\%
$$

*Rationale:* Blanchard (2019) demonstra que $r > g$ (juro real > crescimento) implica
trajetória explosiva da dívida/PIB. Com crescimento potencial brasileiro de 2,5–3,0 %,
o teto de 5,0 % de juro real já é conservador.

**R4 — Viabilidade de convergência:**

$$
s_{BCB} > s
$$

*Rationale:* Condição trivial, porém necessária: só há convergência se a taxa atual
está acima da ótima. Com $s_{BCB} = 14{,}50 \%$, a condição é satisfeita para qualquer
$s < 14{,}50 \%$.

**R5 — Consistência do sistema (∃ solução):**

$$
\exists\, s > \pi \text{ tal que } R1 \wedge R2 \wedge R3 \wedge R4 \text{ são satisfeitas}
$$

### 3.3 Piso de Equilíbrio Global

Independentemente das restrições de teto, $s$ deve remunerar o risco soberano acima
do neutro global:

$$
s_{piso} = r^* \cdot \phi + \delta = 3{,}50 \times 1{,}39 + 4{,}50 = 9{,}365\%
$$

### 3.4 Solução Fechada

O SELIX ótimo é:

$$
\boxed{
s^* = \max\!\left(s_{piso},\; \min(R1_{teto},\; R2_{teto},\; R3_{teto})\right)
}
$$

Calculando com os parâmetros de mai/2026:

$$
R1_{teto} = 9{,}99\%
$$
$$
R2_{teto} = 31{,}23 \times 0{,}95 = 29{,}67\%
$$
$$
R3_{teto} = 4{,}48 + 5{,}00 = 9{,}48\%
$$

A restrição ativa (mais apertada) é **R3**:

$$
s^* = \max(9{,}365,\; \min(9{,}99,\; 29{,}67,\; 9{,}48)) = \max(9{,}365,\; 9{,}48) = \mathbf{9{,}48\%}
$$

---

## 4. Prova Formal (Z3 SMT Solver)

O Z3 Theorem Prover (de Moura & Bjørner, 2008) recebe o sistema como fórmula SMT-LIB2
e verifica **satisfatibilidade** (SAT) ou **insatisfatibilidade** (UNSAT).

### 4.1 Resultados de Verificação

```
SELIX v3.2 — PROVA FORMAL COM Z3 SMT SOLVER
============================================================
  Parametros: inflacao=4.48% | ROE=31.23% | BACEN=14.50%
------------------------------------------------------------
  T1 Investment Grade    (s <= 9.99):        ✓ PROVADO  (SAT)
  T2 Nao Canibaliza      (s <= ROE×0.95):    ✓ PROVADO  (SAT)
  T3 Tesouro Solvente    (s−π <= 5.0%):      ✓ PROVADO  (SAT)
  T4 Convergencia        (14.50 > s):        ✓ PROVADO  (SAT)
  T5 Sistema Consistente (T1∧T2∧T3∧T4 SAT): ✓ PROVADO  (SAT)
------------------------------------------------------------
  Resultado: 5/5 teoremas provados
============================================================
```

*Tempo de execução: 0,03 s em CPU single-thread.*

### 4.2 Teorema Principal (enunciado formal)

**Teorema SELIX (T5):** O sistema $\{R1, R2, R3, R4\}$ é satisfatível e admite
solução única sob a função objetivo $s^* = \min(R1_{teto}, R2_{teto}, R3_{teto})$
sujeito a $s \geq s_{piso}$.

**Prova:** Por construção. Os tetos $R1 = 9{,}99$, $R2 = 29{,}67$ e $R3 = 9{,}48$
formam um conjunto convexo não-vazio: $[s_{piso}, \min(R1, R2, R3)] = [9{,}365, 9{,}48]$.
O mínimo existe, é único e satisfaz $R4$ pois $9{,}48 < 14{,}50$. □

### 4.3 Esboço de Prova em Lean 4

```lean4
-- SELIX Lean 4 sketch (v0.1 — verificação pendente)
theorem selix_sat
    (π ρ s_bcb s : Float)
    (hπ  : π = 4.48)
    (hρ  : ρ = 31.23)
    (hbcb: s_bcb = 14.50)
    (hR1 : s ≤ 9.99)
    (hR2 : s ≤ ρ * 0.95)
    (hR3 : s - π ≤ 5.0)
    (hR4 : s < s_bcb) :
    s ≤ 9.48 ∧ s > π := by
  constructor
  · linarith [hR3, hπ]   -- s ≤ π + 5.0 = 9.48
  · linarith [hπ]         -- s > π (pelo piso)
```

*Nota: prova Lean 4 completa com verificação de piso em desenvolvimento no branch
`lean4/proof` do repositório.*

---

## 5. Análise de Sensibilidade

### 5.1 SELIX como função da inflação

Mantendo ROE = 31,23 % e variando IPCA:

| IPCA (%) | R3_teto (%) | s* (%) | Juro real (%) | IG? |
|----------|------------|--------|---------------|-----|
| 2,00 | 7,00 | 7,00 | 5,00 | ✓ |
| 3,00 | 8,00 | 8,00 | 5,00 | ✓ |
| 4,48 | **9,48** | **9,48** | **5,00** | ✓ |
| 5,00 | 10,00 | **9,99** | 4,99 | ✓ (no limite) |
| 6,00 | 11,00 | 9,99 | 3,99 | ✓ |
| 7,00 | 12,00 | 9,99 | 2,99 | ✓ |

*Insight: acima de IPCA = 5 %, a restrição ativa muda de R3 para R1 (teto IG).*

### 5.2 SELIX como função do ROE

Mantendo IPCA = 4,48 % e variando ROE:

| ROE (%) | R2_teto (%) | Restrição ativa | s* (%) |
|---------|------------|-----------------|--------|
| 10,00 | 9,50 | R2 | 9,48 |
| 15,00 | 14,25 | R3 | 9,48 |
| 20,00 | 19,00 | R3 | 9,48 |
| 31,23 | 29,67 | R3 | 9,48 |
| 10,52 | **9,99** | R1 = R2 | 9,99 |

*Insight: para ROE ≤ 10,52 %, R2 torna-se a restrição ativa. Abaixo de 9,98 %,
o modelo implicaria SELIX inferior ao IG — situação de dominância de risco soberano
sobre retorno privado (anomalia estrutural).*

### 5.3 Caminho de Convergência

Assumindo cortes de 50 bps por reunião COPOM (cadência histórica):

$$
N_{reunioes} = \left\lceil \frac{14{,}50 - 9{,}48}{0{,}50} \right\rceil = \left\lceil 10{,}04 \right\rceil = 11 \text{ reuniões}
$$

Com reuniões COPOM a cada ~45 dias:

$$
T_{convergencia} \approx 11 \times 45 = 495 \text{ dias} \approx \mathbf{16{,}5 \text{ meses}}
$$

*Nota: com cortes de 75 bps (cenário agressivo): 7 reuniões ≈ 10,5 meses.*

---

## 6. Implicações Fiscais

### 6.1 Custo da Anomalia

O custo anual de manter a Selic em 14,50 % ao invés de 9,48 %:

$$
\Delta_{fiscal} = DPMFi \times (s_{BCB} - s^*) = 6{,}8T \times 0{,}0502 \approx \mathbf{R\$\, 341 \text{ bi/ano}}
$$

*Fonte DPMFi: Tesouro Nacional, abr/2026.*

### 6.2 Impacto no Rating Soberano

A literatura empírica (Afonso, 2003; Cantor & Packer, 1996) identifica o juro real
como uma das cinco variáveis mais correlacionadas com *rating* soberano. Juro real
atual de 10,02 % coloca o Brasil como **outlier positivo de risco** — pagando
prêmio não justificado pelos demais fundamentos (dívida/PIB, crescimento, inflação).

---

## 7. Limitações e Trabalhos Futuros

1. **Endogeneidade do ROE:** o retorno bancário é parcialmente função da própria Selic;
   o modelo trata ROE como exógeno — aproximação válida no curto prazo.

2. **Prêmio de risco dinâmico:** $\delta = 4{,}50$ é média de 2025; o CDS 5Y flutua
   com percepção fiscal. Extensão natural: $\delta_t$ como série estocástica.

3. **Prova Lean 4 completa:** o esboço da Seção 4.3 precisa de verificação formal
   completa com sistema de tipos de Lean 4 para flutuação de ponto fixo.

4. **Modelo de equilíbrio geral:** o SELIX é modelo parcial (only monetary). Integração
   com modelo DSGE do BCB (SAMBA) é extensão de médio prazo.

---

## 8. Conclusão

O modelo SELIX demonstra formalmente que existe uma taxa Selic ótima
$s^* = 9{,}48\%$ que satisfaz simultaneamente as cinco restrições institucionais
relevantes para a economia brasileira. A taxa corrente de 14,50 % excede $s^*$ em
**502 bps** — excesso com custo fiscal estimado em **R$ 341 bilhões/ano** — sem
contrapartida nos fundamentos de risco soberano.

A prova é:
- **Reproduzível:** `git clone && make z3` em < 1 minuto
- **Falsificável:** qualquer alteração nos parâmetros gera novo $s^*$ automaticamente
- **Auditável:** código aberto em `github.com/scoobiii/selix`

---

## Referências

Afonso, A. (2003). *Understanding the determinants of sovereign debt ratings.*
Journal of Economics and Finance, 27(1), 56–74.

Banco Central do Brasil (2026). *Nota de Política Monetária — abril 2026.* BCB/DEPOM.

Blanchard, O. (2019). *Public Debt and Low Interest Rates.* AER 109(4), 1197–1229.

Cantor, R., & Packer, F. (1996). *Determinants and Impact of Sovereign Credit Ratings.*
FRBNY Economic Policy Review, 2(2), 37–54.

Clarida, R., Galí, J., & Gertler, M. (1999). *The Science of Monetary Policy.*
Journal of Economic Literature, 37(4), 1661–1707.

de Moura, L., & Bjørner, N. (2008). *Z3: An Efficient SMT Solver.*
TACAS 2008, LNCS 4963, 337–340.

Ferreira, P., & Nakane, M. (2015). *Estimativa da Taxa de Juro Natural no Brasil.*
Pesquisa e Planejamento Econômico, 45(3), 7–45.

Holston, K., Laubach, T., & Williams, J. C. (2017). *Measuring the Natural Rate of
Interest: International Trends and Determinants.* JIE 108, S59–S75.

IMF (2026). *World Economic Outlook — April 2026.* Washington: IMF.

Taylor, J. B. (1993). *Discretion versus Policy Rules in Practice.*
Carnegie-Rochester CSP 39, 195–214.

Woodford, M. (2003). *Interest and Prices.* Princeton University Press.

---

## Apêndice A — Reprodução Computacional

```bash
# Ambiente mínimo
git clone https://github.com/scoobiii/selix.git
cd selix
pip install z3-solver pytest

# Executar modelo
python src/selix/core.py

# Prova formal Z3
python src/selix/z3_proof.py

# Suite de testes (13 casos)
pytest tests/ -v

# Pipeline completo
make all
```

**Output esperado (core.py):**
```
SELIX IDEAL      : 9.48%
Selic BACEN      : 14.50%
Diferencial      : -5.02 pp
Juro real SELIX  : 5.0%
Investment Grade : SIM ✓
Convergencia     : 10.0 meses
```

---

## Apêndice B — Glossário

| Termo | Definição |
|-------|-----------|
| SMT Solver | *Satisfiability Modulo Theories* — verificador formal de fórmulas lógicas com aritmética |
| SAT | Fórmula satisfatível — existe atribuição de valores que torna a fórmula verdadeira |
| UNSAT | Fórmula insatisfatível — nenhuma atribuição satisfaz a fórmula |
| Investment Grade | *Rating* soberano BBB- ou superior (S&P/Fitch) ou Baa3 (Moody's) |
| DPMFi | Dívida Pública Mobiliária Federal interna |
| COPOM | Comitê de Política Monetária do Banco Central do Brasil |
| Juro real | Taxa nominal menos IPCA acumulado 12 meses (ex-post) |
| ROE | *Return on Equity* — lucro líquido / patrimônio líquido médio |
| CDS 5Y | *Credit Default Swap* 5 anos — proxy de risco soberano de mercado |

---

---

## 9. Fundamentos Nobel: Discrição vs. Regra na Política Monetária

### 9.1 O Problema da Inconsistência Temporal (Kydland & Prescott — Nobel 2004)

Finn Kydland e Edward Prescott provaram o teorema da **inconsistência temporal**
da política discricionária:

> *A política ótima calculada no presente deixa de ser ótima no futuro quando o
> agente pode recalcular livremente. A solução racional é o comprometimento com regras.*

Aplicado ao Brasil: um BCB que fixa a Selic **discricionariamente** a cada 45 dias,
sem âncora quantitativa transparente, gera **viés inflacionário de equilíbrio** —
o mercado antecipa a tentação de estimular crescimento via juro baixo e exige prêmio
de risco adicional ex-ante. Resultado: a Selic de equilíbrio sob discrição é
**estruturalmente maior** que sob regra:

$$
s_{discricao} = s^* + \underbrace{\lambda \cdot \mathbb{E}[\Delta y]}_{\text{prêmio de inconsistência}} > s^*
$$

O SELIX opera como **regra explícita e auditável** — exatamente o mecanismo que
Kydland & Prescott prescrevem para eliminar esse prêmio.

### 9.2 Expectativas Racionais e Credibilidade (Sargent & Sims — Nobel 2011)

Thomas Sargent e Christopher Sims demonstraram que agentes formam expectativas usando
**toda informação disponível**, incluindo o regime de política monetária vigente.
Duas implicações diretas para o SELIX:

1. **Efeito antecipação:** a mera publicação de uma regra como o SELIX reduz
   expectativas de inflação antes de qualquer corte efetivo, diminuindo o custo
   real de convergência.

2. **Identificação de choque vs. regime:** Sims (VAR estrutural) mostra que boa
   parte da "rigidez inflacionária" brasileira é endógena ao regime de alta
   discricionariedade — não a fundamentos. Mudar o regime muda a dinâmica.

### 9.3 A Crítica de Lucas (Lucas — Nobel 1995)

Robert Lucas estabeleceu que parâmetros econométricos mudam quando a política muda.
Para o SELIX:

> Se o BCB adotar formalmente a regra SELIX, os coeficientes de pass-through
> câmbio-inflação e o próprio juro neutro **se reduzem**, pois a ancoragem reduz
> volatilidade cambial e prêmio de risco soberano.

Em outras palavras: a adoção da regra melhora os próprios parâmetros de entrada —
o modelo é auto-reforçante. A SELIX calculada no dia 2 da adoção é menor que a
calculada no dia 0.

### 9.4 Teoria dos Jogos e Regulação (Tirole — Nobel 2014)

Jean Tirole demonstra que um banco central com mandato dual sem regra quantitativa
joga um **jogo de Stackelberg** contra o mercado cujo equilíbrio de Nash resulta
em juro permanentemente elevado:

| Estratégia BCB | Estratégia Mercado | Resultado |
|---------------|-------------------|-----------|
| Discrição pura | Prêmio alto | Selic alta — equilíbrio instável |
| Regra SELIX | Prêmio baixo | **Selic ótima — equilíbrio estável** |
| Regra + credibilidade plena | Sem prêmio | $s = s^*$ convergência total |

### 9.5 Instituições Inclusivas (Acemoglu & Johnson — Nobel 2024)

Daron Acemoglu e Simon Johnson demonstraram que **instituições inclusivas** são o
principal determinante de prosperidade de longo prazo. O SELIX é, nesse
enquadramento, uma proposta de **institucionalização da regra monetária**:

- Substituir discrição do COPOM por fórmula pública auditável
- Reduzir captura regulatória pelo setor financeiro rentista
- Ampliar acesso ao crédito produtivo via custo de capital menor

Uma Selic estruturalmente 5 pp acima do ótimo é **instituição extrativista**
transferindo renda do setor produtivo para credores soberanos — exatamente o
mecanismo que Acemoglu identifica como travão do desenvolvimento.

### 9.6 Síntese Nobel

| Nobel | Ano | Contribuição central | Implicação para SELIX |
|-------|-----|---------------------|----------------------|
| Lucas | 1995 | Crítica paramétrica | Adoção melhora os próprios inputs do modelo |
| Kydland & Prescott | 2004 | Inconsistência temporal | Regra > Discrição em credibilidade |
| Sargent & Sims | 2011 | Expectativas racionais | Anúncio da regra já reduz prêmio de risco |
| Tirole | 2014 | Jogos + regulação | Equilíbrio Nash estável somente sob regra |
| Acemoglu & Johnson | 2024 | Instituições inclusivas | Regra monetária = instituição não-extrativista |

---

## 10. PIB Setorial, Pesos e SWOT SELIX

### 10.1 Composição do PIB Brasileiro (2025, R$ 11,7 trilhões)

```
PIB BRASIL 2025 — R$ 11,7 trilhões
│
├── SERVIÇOS ──────────────────────── 73,0 %  (R$ 8,5 T)
│   ├── Administração pública + Saúde  15,1 %  neutro → pró (dívida pública menor)
│   ├── Serviços imobiliários           9,8 %  fortemente pró (crédito habitação)
│   ├── Serviços financeiros            7,8 %  CONTRA (NII comprimido)
│   ├── Comércio varejista              6,2 %  pró (crédito ao consumidor)
│   ├── TI / Telecom                    4,3 %  pró (CAPEX, valuation)
│   └── Demais serviços                29,8 %  pró geral
│
├── INDÚSTRIA ─────────────────────── 20,0 %  (R$ 2,3 T)
│   ├── Indústria de transformação     10,2 %  fortemente pró
│   ├── Construção civil                4,1 %  fortemente pró
│   ├── Energia elétrica / utilities    2,9 %  pró (CAPEX regulado)
│   └── Extrativa mineral               2,8 %  neutro (exportação/dólar)
│
└── AGROPECUÁRIA ──────────────────────  7,0 %  (R$ 0,8 T)
    ├── Grãos (soja, milho)              3,1 %  neutro (exportação)
    ├── Pecuária / proteína animal       2,2 %  neutro-pró (crédito rural)
    └── Hortifrutis + outros             1,7 %  pró (custeio interno)
```

*Fontes: IBGE SCN 2025, FGV IBRE, BCB.*

### 10.2 Impacto Setorial de -502 bps (Selic 14,50 % → 9,48 %)

| Setor | Peso PIB | Canal principal | Impacto estimado |
|-------|---------|----------------|-----------------|
| Indústria de transformação | 10,2 % | CAPEX + capital de giro | +1,8 pp crescimento |
| Construção civil | 4,1 % | Crédito imobiliário | +2,4 pp crescimento |
| Comércio varejista | 6,2 % | Crédito ao consumidor | +1,2 pp crescimento |
| TI / Startups | 4,3 % | Custo de capital / valuation | +15–25 % valuation |
| Energia / Utilities | 2,9 % | Custo de dívida, CAPEX regulado | -R$ 12 bi/ano custo |
| Agro (custeio interno) | 1,7 % | Crédito rural pré-custeio | +0,4 pp crescimento |
| Serviços financeiros | 7,8 % | Spread bancário, NII | -8 a -12 % lucro líquido |
| Adm. Pública / Tesouro | 15,1 % | Juros DPMFi (-R$ 341 bi/ano) | Superávit primário viável |

### 10.3 SWOT SELIX por Setor (Nota 1–3)

#### Indústria de Transformação + Construção Civil (peso 14,3 % PIB)

| | Item | Nota |
|-|------|------|
| **S** | Redução imediata de WACC em 3–5 pp | 3 |
| **S** | BNDES/FINAME mais competitivo vs. mercado | 3 |
| **W** | Câmbio: BRL potencialmente mais fraco eleva custo de insumos importados | 2 |
| **W** | Janela de incerteza de 10–16 meses durante convergência | 1 |
| **O** | WACC competitivo com México e Índia — atração de nearshoring | 3 |
| **O** | Demanda reprimida de 8 milhões de moradias (CBIC 2025) | 3 |
| **T** | Pressão de insumos dolarizados se BRL depreciar | 2 |
| **T** | Spread bancário pode compensar parte da queda da Selic | 2 |

#### Serviços Financeiros (peso 7,8 % PIB)

| | Item | Nota |
|-|------|------|
| **S** | Spread de 20–30 pp sobre Selic garante margem mesmo com juro menor | 2 |
| **S** | Maior volume de crédito compensa parte da compressão de NII | 2 |
| **W** | NII (Net Interest Income) cai com Selic menor — impacto direto | 3 |
| **W** | Portfólios de LFT (Selic-atrelados) perdem rentabilidade relativa | 3 |
| **O** | Migração de tesouraria soberana para crédito produtivo (maior spread) | 2 |
| **O** | Queda de juro empurra empresas a debêntures e IPO — fee income sobe | 2 |
| **T** | Fintechs ganham espaço competitivo com Selic menor | 2 |
| **T** | ROE de 31 % é insustentável com Selic < 10 % — compressão estrutural | 3 |

#### Agropecuária — custeio interno (peso 1,7 % PIB direto)

| | Item | Nota |
|-|------|------|
| **S** | Crédito de custeio e investimento mais barato | 2 |
| **S** | Cadeia processadora (frigoríficos, esmagamento) se beneficia | 2 |
| **W** | Exportadores são indiferentes — acessam dólar via tradings | 1 |
| **O** | CAPEX em agritech e automação viável com WACC < 10 % | 2 |
| **T** | Agro como hedge de inflação perde parte da atratividade relativa | 1 |

#### Setor Público / Tesouro Nacional (15,1 % via Adm. Pública)

| | Item | Nota |
|-|------|------|
| **S** | -R$ 341 bi/ano em despesas financeiras libera espaço fiscal | 3 |
| **S** | Investment Grade abre acesso a índices IG — custo de emissão -150–200 bps | 3 |
| **W** | 42 % da DPMFi é LFT — transição precisa ser gradual para evitar risco de rolagem | 3 |
| **O** | Janela para alongar dívida em pré-fixados durante queda da Selic | 3 |
| **T** | Queda de demanda por LFT pode pressionar taxa de curto prazo durante transição | 2 |

### 10.4 SWOT Macro — SELIX como Proposta de Política

| | Item | Nota |
|-|------|------|
| **S** | Modelo auditável, código aberto, prova Z3 reproducível | 3 |
| **S** | Alinhado com 5 prêmios Nobel de economia | 3 |
| **S** | Custo fiscal do status quo documentado em R$ 341 bi/ano | 3 |
| **W** | Sem mandato legal — BCB tem independência formal (Lei 179/2021) | 3 |
| **W** | Parâmetros (ROE, δ) precisam de atualização trimestral para manter validade | 2 |
| **W** | Prova Lean 4 incompleta — ponto fraco perante revisores de verificação formal | 2 |
| **O** | Momento político: debate fiscal aceso, pressão do setor produtivo organizado | 3 |
| **O** | Timing eleitoral 2026 — candidatos buscam agenda de crescimento com responsabilidade | 2 |
| **O** | Fluxo de capitais emergentes — Brasil precisa de IG para capturar alocação passiva | 3 |
| **T** | Lobby bancário (FEBRABAN) com acesso direto ao COPOM via ex-executivos | 3 |
| **T** | Comunicação técnica difícil para imprensa generalista e público | 2 |
| **T** | BCB pode adotar retórica SELIX sem alterar a substância da política | 2 |

---

## 11. Economia Política: Stakeholders, Posições e Estratégia de Convencimento

### 11.1 Mapa de Poder

```
        FORTEMENTE PRÓ-SELIX
               ▲
    CNI · SEBRAE · CBIC · Tesouro · Startups · Consumidores
               |
    Neutro ────┼──────────────────────────── Fortemente CONTRA
    (Agro      |   ZONA DE DISPUTA           FEBRABAN · ANBIMA
    exportador)|   FIESP industrial           Fundos Previdência
               |   CNA custeio               Tesouros Privados
               |   Sindicatos CUT/CSB         Carry trade externo
               ▼
        POTENCIALMENTE PRÓ (mobilizável)
    BCB (se adotar score voluntário) · Mídia econômica · Academia
```

### 11.2 Stakeholders CONTRA — Análise Detalhada

#### FEBRABAN + Grandes Bancos (Itaú, Bradesco, BB, Caixa, Santander)

**Interesse real:** Com Selic a 14,50 %, a tesouraria bancária rende 14,50 % em LFT
sem risco de crédito. Redução de 502 bps comprime NII estimado em R$ 85–110 bi/ano
no agregado do sistema.

**Argumento público:** "Redução precipitada gera inflação e fuga de capital."

**Poder de lobby:** Alto. FEBRABAN financia campanhas via setor financeiro e tem
acesso direto ao COPOM por meio de ex-executivos em cargos técnicos do BCB.

**Como SELIX convence:**
- Volume de crédito cresce com Selic menor: carteira total sai de R$ 6,2 T para
  estimados R$ 8,5 T (+37 %) — fee income e crédito privado compensam NII
- ROE de 18–22 % ainda seria o maior entre emergentes com IG
- Argumento Tirole: juro alto é risco sistêmico — inadimplência cresce com custo
  do crédito, corroendo qualidade da carteira
- Proposta: transição de 11 reuniões COPOM a 50 bps cada — sem cliff edge

#### ANBIMA + Fundos de Previdência Privada (ABRAPP)

**Interesse real:** Metas atuariais históricas de 6–8 % real, calibradas para era
de juro alto. Com SELIX, juro real = 5,0 % — abaixo das metas vigentes.

**Argumento público:** "Poupadores e aposentados serão penalizados."

**Como SELIX convence:**
- Juro real de 5,0 % ainda é o maior entre emergentes com IG (Tabela 1, Seção 2.3)
- Investment Grade aprecia câmbio: BRL mais forte valoriza patrimônio externo
- Risco alternativo: sem IG, reclassificação para junk destrói muito mais patrimônio
  do que redução de 200 bps no juro real
- Proposta: carência de 24 meses para revisão de metas atuariais — tempo suficiente
  para rebalancear portfólios em crédito privado e equity

#### Banco Central do Brasil (Institucional)

**Interesse real:** Preservação da autonomia formal (Lei 179/2021) e da narrativa
de credibilidade anti-inflacionária construída desde o Plano Real.

**Argumento público:** "Regras externas ferem a independência do BCB."

**Como SELIX convence:**
- SELIX não é mandato legal — é benchmark público transparente e voluntário
- Fed publica dot plot; BCE publica forward guidance — transparência reforça
  credibilidade, não a fere
- Kydland & Prescott (Nobel 2004) demonstram formalmente que regra > discrição
  em termos de credibilidade de longo prazo
- Proposta concreta: BCB publica SELIX score trimestral como item do Relatório de
  Inflação, sem vinculação legal à decisão do COPOM

#### Carry Trade Externo (JPMorgan, BlackRock, BNY — ~28 % da DPMFi)

**Interesse real:** Diferencial de juros Brasil-EUA de ~10 pp com Selic a 14,50 %.
Redução comprime o carry e pode induzir saída de posições.

**Argumento:** "Redução de juro provoca fuga de capital e desvalorização do BRL."

**Como SELIX convence:**
- Investment Grade abre acesso aos índices soberanos IG (JPMorgan GBI-EM IG,
  Bloomberg EM IG) — entrada de capital de longo prazo estruturalmente maior
  que a saída de carry de curto prazo
- Carry trade é dinheiro volátil; capital de pensões soberanas (long-only IG) é
  3–4x maior em volume e muito mais estável
- Referência empírica: México reduziu taxa equivalente de 11 % → 6 % em 2020–2021
  sem fuga de capital — o peso se apreciou 12 %

### 11.3 Stakeholders PRÓ — Como Mobilizar

| Ator | Interesse direto | Ação proposta |
|------|----------------|---------------|
| CNI | WACC industrial cai de ~18 % para ~13 % | Estudo comparativo Brasil vs. México vs. Índia; pauta legislativa via Câmara |
| SEBRAE | Inadimplência PME cai ~30 %; crédito de 25 % a.a. → 15 % a.a. | Campanha "cada ponto da Selic = R$ 2,3 bi a mais para PMEs" |
| Tesouro Nacional | -R$ 341 bi/ano em despesas financeiras | Nota técnica oficial; posicionar como instrumento de responsabilidade fiscal |
| CBIC | Demanda reprimida de 8 M moradias viabilizada | Calcular unidades habitacionais adicionais por ponto de Selic |
| Startups / Fintechs | Custo de capital e valuation | Estudo de mercado VC: rodadas viabilizadas com WACC < 10 % |
| Consumidores (IDEC) | Crédito pessoal de 40 % a.a. → 25 % a.a. | Campanha de base — maior visibilidade política |

### 11.4 Roadmap de Lobby Pró-SELIX

```
FASE 1 — Legitimação Técnica (meses 1–3)
  ├── Paper publicado em SSRN e arXiv (econ.GN)
  ├── Código aberto GitHub com Z3 reproducível em < 1 min
  ├── Apresentação em ANPEC / FEA-USP / FGV-EPGE
  └── Cobertura especializada: Valor Econômico, InfoMoney, Broadcast

FASE 2 — Mobilização Setorial (meses 3–6)
  ├── CNI adota SELIX como posição em audiência na Câmara
  ├── SEBRAE publica mapa de impacto por setor e por estado
  ├── CBIC calcula habitações adicionais viabilizadas
  └── Fintechs/VCs calculam valuation adicional de portfólio

FASE 3 — Arena Legislativa (meses 6–12)
  ├── PL propondo publicação do "SELIX Score" no Relatório de Inflação BCB
  ├── Audiência pública na CAE (Senado) — comparativo Fed dot plot / BCE
  ├── Relatório de auditoria TCU sobre custo fiscal do desvio SELIX
  └── Índice público mensal de "Aderência à Regra SELIX"

FASE 4 — Pressão Eleitoral 2026
  ├── Candidatos presidenciais adotam SELIX como âncora de proposta econômica
  ├── Debate público: "R$ 341 bi que poderiam ser hospitais, escolas, infraestrutura"
  └── Campanha digital com cálculo personalizado por setor / empresa / família
```

### 11.5 Matriz de Convencimento

| Stakeholder contra | Argumento deles | Contra-argumento SELIX | Concessão |
|-------------------|----------------|----------------------|-----------|
| FEBRABAN | Inflação vai subir | CDS cai → BRL aprecia → importados mais baratos | Transição gradual 11 reuniões |
| ANBIMA / Previdência | Rentabilidade cai | Juro real 5 % = maior entre IG emergentes | Carência 24 meses para rebalancear |
| BCB | Fere autonomia | SELIX é benchmark voluntário, não mandato | BCB publica score no Relatório de Inflação |
| Carry trade externo | Fuga de capital | IG atrai capital de longo prazo >> carry | Modelo de transição publicado antecipadamente |
| Mídia econômica | Populismo | Cinco Nobels + código aberto + Z3 provado | Paper em inglês no SSRN |

---

*Código-fonte, dados e provas formais disponíveis em:*  
*https://github.com/scoobiii/selix — licença MIT*
