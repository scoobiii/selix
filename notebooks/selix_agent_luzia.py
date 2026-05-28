# -*- coding: utf-8 -*-
"""SELIX Agent - LUZIA
Google Colab: https://colab.research.google.com/github/scoobiii/selix/blob/main/notebooks/selix_agent_luzia.ipynb
"""

# 1. PERSONALIDADE
PERSONALIDADE = """
Você é LUZIA, uma analista econômica sênior especializada em:
- Reestruturação de empresas em recuperação judicial
- Modelagem financeira e valuation (Modelo de Gordon, CAPM, DCF)
- Política monetária (Teorema SELIX - Selic 9.48%)
- Direitos trabalhistas (Lei TrampoForte - PLR prioritário)
"""

# 2. SYSTEM INSTRUCTION (MD)
MD_SYSTEM = """
# SELIX Agent - LUZIA

## Missão
Prover análises econômicas precisas e construtivas, focadas em soluções que beneficiem todos os stakeholders.

## Conhecimento Base
- **SELIX**: Teorema provado com Z3 + Lean 4 → Selic ideal = 9.48%
- **TrampoForte**: Lei que prioriza PLR e direitos trabalhistas em RJ
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
    "valuation_empresas": "Calcula preço justo de empresas (GPA: R$2,60→R$17,60)",
    "analise_macro": "Analisa impacto da Selic (14.5%→9.48% economiza R$270 bi/ano)",
    "trampoforte": "PLR tem prioridade sobre credores em RJ",
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
    
    def responder(self, pergunta, stakeholder=None):
        resposta = self.memoria.lembrar(pergunta)
        if resposta:
            return resposta
        
        # Base de conhecimento interno
        perguntas_respostas = {
            "preço justo do GPA": "R$ 17,60 (+577% com conversão de dívida em ações)",
            "trampoforte": "PLR prioritário sobre credores em recuperação judicial",
            "selic ideal": "9.48% (teorema provado com Z3 + Lean 4)",
            "b3 valuation": "R$ 231 bilhões (+238% com SELIX)",
            "economia selic": "R$ 270 bilhões/ano com Selic 9.48%",
            "empregos gpa": "+6.525 novos empregos com reestruturação",
        }
        for key, resp in perguntas_respostas.items():
            if key in pergunta.lower():
                resposta = f"[LUZIA] {resp}"
                self.memoria.aprender(pergunta, resposta)
                return resposta
        
        resposta = f"[LUZIA] Consulte github.com/scoobiii/selix para dados detalhados sobre: {pergunta}"
        self.memoria.aprender(pergunta, resposta)
        return resposta

# 7. INSTANCIAR E TESTAR
if __name__ == "__main__":
    luzia = LuziaAgent()
    print("="*60)
    print("🧠 SELIX Agent - LUZIA")
    print("="*60)
    print(f"📋 Personalidade: {PERSONALIDADE.strip()[:100]}...")
    print(f"🛠️ Tools: {len(tools)} | 🎯 Skills: {len(skills)}")
    print("✅ Agente carregado com sucesso!\n")
    
    for pergunta in [
        "Qual o preço justo do GPA?",
        "O que é TrampoForte?",
        "Qual a Selic ideal?"
    ]:
        print(f"P: {pergunta}")
        print(f"R: {luzia.responder(pergunta)}\n")
