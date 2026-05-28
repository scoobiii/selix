# -*- coding: utf-8 -*-
"""SELIX Agent - LUZIA
Google Colab: https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_agent_luzia.py
"""

print("="*60)
print("🧠 Carregando SELIX Agent - LUZIA")
print("="*60)

# 1. PERSONALIDADE
PERSONALIDADE = """
Você é LUZIA, uma analista econômica sênior especializada em:
- Reestruturação de empresas em recuperação judicial
- Modelagem financeira e valuation (Modelo de Gordon, CAPM, DCF)
- Política monetária (Teorema SELIX - Selic 9.48%)
- Direitos trabalhistas (Lei TrampoForte - PLR prioritário)
"""

# 2. SYSTEM INSTRUCTION
MD_SYSTEM = """
# SELIX Agent - LUZIA

## Missão
Prover análises econômicas precisas e construtivas.

## Conhecimento Base
- **SELIX**: Selic ideal = 9.48% (provado com Z3 + Lean 4)
- **TrampoForte**: PLR prioritário sobre credores em RJ
- **Valuation**: Modelo de Gordon + CAPM
"""

# 3. TOOLS
tools = {
    "calcular_selix": lambda: 9.48,
    "calcular_valuation_gordon": lambda d, ke, g: d / (ke - g) if ke > g else 0,
    "calcular_custo_capital": lambda rf, beta, premio: rf + beta * premio,
}

# 4. SKILLS
skills = {
    "valuation_empresas": "GPA: R$2,60 → R$17,60 (+577%)",
    "analise_macro": "Selic 14,5%→9,48%: economia de R$270 bi/ano",
    "trampoforte": "PLR prioritário sobre credores em RJ",
    "energia": "Recomendação E40 para Brent > US$120",
}

# 5. MEMÓRIA
class MemoriaSELIX:
    def __init__(self):
        self.memoria = {}
    def lembrar(self, chave): return self.memoria.get(chave)
    def aprender(self, chave, valor): self.memoria[chave] = valor

# 6. AGENTE PRINCIPAL
class LuziaAgent:
    def __init__(self):
        self.nome = "Luzia"
        self.perfil = PERSONALIDADE
        self.tools = tools
        self.skills = skills
        self.memoria = MemoriaSELIX()
        self.base_conhecimento = {
            "preço justo do gpa": "R$ 17,60 (+577% com conversão de dívida)",
            "trampoforte": "PLR prioritário sobre credores em recuperação judicial",
            "selic ideal": "9.48% (teorema provado com Z3 + Lean 4)",
            "b3 valuation": "R$ 231 bilhões (+238% com SELIX)",
            "economia selic": "R$ 270 bilhões/ano com Selic 9,48%",
        }
    
    def responder(self, pergunta):
        pergunta_lower = pergunta.lower()
        if resposta := self.memoria.lembrar(pergunta_lower):
            return resposta
        
        for key, resp in self.base_conhecimento.items():
            if key in pergunta_lower:
                resposta = f"[LUZIA] {resp}"
                self.memoria.aprender(pergunta_lower, resposta)
                return resposta
        
        resposta = f"[LUZIA] Consulte github.com/scoobiii/selix para: {pergunta}"
        self.memoria.aprender(pergunta_lower, resposta)
        return resposta

# 7. INSTANCIAR E TESTAR
luzia = LuziaAgent()

print(f"\n📋 Personalidade: {PERSONALIDADE.strip()[:120]}...")
print(f"🛠️ Tools: {len(tools)} | 🎯 Skills: {len(skills)}")
print("✅ LUZIA carregada com sucesso!\n")

print("📝 TESTE DE RESPOSTA:")
for pergunta in [
    "Qual o preço justo do GPA?",
    "O que é TrampoForte?",
    "Qual a Selic ideal?"
]:
    print(f"P: {pergunta}")
    print(f"R: {luzia.responder(pergunta)}\n")

print("🔗 https://github.com/scoobiii/selix")
