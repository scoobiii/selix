"""
Configuração de autoridades para alertas SELIX
"""

AUTORIDADES = {
    # Decisores Executivos
    "executivos": {
        "alexandre_silveira": {
            "nome": "Alexandre Silveira",
            "bluesky": "@mme.bsky.social",  # Ministério de Minas e Energia
            "cargo": "Ministro de Minas e Energia",
            "prioridade": 1
        },
        "rodolfo_saboia": {
            "nome": "Rodolfo Saboia",
            "bluesky": "@anp.bsky.social",  # ANP
            "cargo": "Diretor-Geral da ANP",
            "prioridade": 1
        },
        "cnpe": {
            "nome": "CNPE",
            "bluesky": "@cnpe.bsky.social",  # Conselho Nacional de Política Energética
            "cargo": "Conselho Nacional de Política Energética",
            "prioridade": 1
        },
        "lula": {
            "nome": "Presidente Lula",
            "bluesky": "@lula.bsky.social",
            "cargo": "Presidente da República",
            "prioridade": 2
        }
    },
    
    # Decisores Legislativos
    "legislativos": {
        "joaquim_passarinho": {
            "nome": "Joaquim Passarinho",
            "bluesky": "@depjoaquimp.bsky.social",
            "cargo": "Presidente da CME - Câmara dos Deputados",
            "prioridade": 1
        },
        "pazuello": {
            "nome": "General Pazuello",
            "bluesky": "@genpazuello.bsky.social",
            "cargo": "Vice-presidente da CME",
            "prioridade": 2
        },
        "camara_deputados": {
            "nome": "Câmara dos Deputados",
            "bluesky": "@camaradeputados.bsky.social",
            "cargo": "Comissão de Minas e Energia",
            "prioridade": 1
        }
    }
}

# Template por tipo de autoridade
TEMPLATES = {
    "tecnico": """
🚨 ALERTA SELIX - CRISE ENERGÉTICA

📊 DADOS TÉCNICOS:
• Brent spot: US$ {brent}
• Risco Geopolítico: {gpr}/100 (ALERTA)
• Previsão 1 mês: US$ {previsao}

🔴 RECOMENDAÇÃO:
→ ELEVAR MISTURA PARA E40 AGORA
→ Tempo resposta: 24h
→ Economia anual: US$ {economia} bilhões

🔗 github.com/scoobiii/selix
#SELIX #Energia #Brasil #Crise
""",

    "impacto": """
🚨 CRISE ENERGÉTICA - AÇÃO URGENTE NECESSÁRIA

📊 IMPACTO ECONÔMICO:
• Economia anual: US$ 30.2 bilhões
• Proteção ao consumidor: E40 na gasolina
• Redução dependência petróleo importado

🏛️ SOLICITAÇÃO:
• Convocar audiência pública urgente
• Implementar E40 imediatamente
• Ativar gatilhos automáticos

🔗 github.com/scoobiii/selix
#SELIX #TransiçãoEnergética #Brasil
""",

    "curto": """
🚨 ALERTA: Brent US$ {brent} | GPR {gpr}

→ RECOMENDAÇÃO SELIX: E40 AGORA
→ Economia: US$ 30.2 bi/ano
→ Ação: 24h

🔗 github.com/scoobiii/selix
#SELIX #Etanol #Emergência
"""
}

def get_mentions(tipo="todos"):
    """Retorna menções formatadas para Bluesky"""
    if tipo == "executivos":
        autoridades = AUTORIDADES["executivos"]
    elif tipo == "legislativos":
        autoridades = AUTORIDADES["legislativos"]
    else:
        # Todos + adicionais
        autoridades = {}
        autoridades.update(AUTORIDADES["executivos"])
        autoridades.update(AUTORIDADES["legislativos"])
    
    # Adicionar mídia especializada
    if tipo == "todos":
        autoridades["midia_energia"] = {
            "nome": "Mídia Especializada",
            "bluesky": "@energia.bsky.social @economia.bsky.social",
            "cargo": "Imprensa",
            "prioridade": 3
        }
    
    mencoes = []
    for key, auth in autoridades.items():
        if auth.get("bluesky"):
            mencoes.append(auth["bluesky"])
    
    return " ".join(mencoes) + " "

def gerar_post_tecnico(dados, tipo="tecnico"):
    """Gera post com menções às autoridades"""
    mencoes = get_mentions("executivos")
    template = TEMPLATES.get(tipo, TEMPLATES["tecnico"])
    
    conteudo = template.format(**dados)
    
    # Inserir menções no início
    post_completo = f"{mencoes}\n\n{conteudo}"
    
    # Limitar a 300 caracteres
    if len(post_completo) > 300:
        post_completo = post_completo[:297] + "..."
    
    return post_completo
