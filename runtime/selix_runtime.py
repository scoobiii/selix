#!/usr/bin/env python3
from router import route
from llm import llm_generate

def main():
    print("Selix Runtime (local-first, tools-first)")
    while True:
        pergunta = input("\n> ")
        if pergunta.lower() in ['exit', 'quit']:
            break
        
        rota = route(pergunta)
        
        if not rota.get('need_llm'):
            # Resposta direta sem LLM
            if rota['tool'] == 'brent':
                print(f"Brent: US${rota['data']['price']} (fonte: {rota['data']['source']}, há {rota['data']['age_hours']}h)")
            elif rota['tool'] == 'selic':
                print(f"Selic: {rota['data']['selic']}%")
            continue
        
        # LLM para síntese
        if 'data' in rota:
            prompt = f"Com base nos dados a seguir, responda: {pergunta}\n\nDados: {rota['data']}"
        else:
            prompt = pergunta
        
        resposta = llm_generate(prompt)
        print(resposta)

if __name__ == "__main__":
    main()
