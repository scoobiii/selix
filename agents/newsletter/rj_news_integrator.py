#!/usr/bin/env python3
import sys
sys.path.append('/root/selix/agents/monitor')
from api_rj_integracao import monitor_rj

class RJNewsIntegrator:
    def __init__(self):
        self.monitor = monitor_rj
    
    def gerar_secao_rj(self) -> str:
        empresas = self.monitor.obter_todas_empresas()
        texto = "## ⚖️ EMPRESAS EM RECUPERAÇÃO JUDICIAL\n\n"
        texto += "| Empresa | Código | Preço | SELIX | Potencial |\n"
        texto += "|---------|--------|-------|-------|-----------|\n"
        
        for emp in empresas[:8]:
            texto += f"| {emp['nome']} | {emp['codigo']} | R$ {emp['preco_atual']} | R$ {emp['preco_selix']} | +{emp['potencial']}% |\n"
        
        return texto

if __name__ == "__main__":
    integ = RJNewsIntegrator()
    print(integ.gerar_secao_rj())
