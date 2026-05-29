#!/usr/bin/env python3
import sys
sys.path.append('/root/selix/agents/bluesky_bot')
sys.path.append('/root/selix/agents/monitor')

from api_rj_integracao import monitor_rj
from post_seguro import postar_seguro

def publicar_relatorio_rj():
    texto = monitor_rj.gerar_relatorio_completo()
    print(f"📝 Texto: {len(texto)} caracteres")
    resultado = postar_seguro(texto)
    print(f"✅ Relatório RJ: {resultado.get('url')}")
    return resultado

if __name__ == "__main__":
    publicar_relatorio_rj()
