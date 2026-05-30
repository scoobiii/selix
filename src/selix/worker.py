"""Worker - Coleta dados das APIs externas e salva no banco"""
import time
from datetime import datetime
import sys
sys.path.append('/root/selix')

from src.selix.database import salvar_preco, obter_ultimo_preco
from agents.monitor.fontes_confiaveis import FontesConfi

def coletar_dados():
    print(f"[{datetime.now()}] Coletando dados...")
    f = FontesConfi()
    
    # Brent
    brent = f.brent_real()
    salvar_preco("brent", brent['preco'], brent['fonte'])
    print(f"  ✅ Brent: US$ {brent['preco']}")
    
    # Selic
    selic = f.selic_real()
    salvar_preco("selic", selic['selic'], selic['fonte'])
    print(f"  ✅ Selic: {selic['selic']}%")
    
    # GPA
    gpa = f.acao_real("PCAR3")
    salvar_preco("gpa", gpa['preco'], gpa['fonte'])
    print(f"  ✅ GPA: R$ {gpa['preco']}")
    
    # Raízen
    raizen = f.acao_real("RAIZ4")
    salvar_preco("raizen", raizen['preco'], raizen['fonte'])
    print(f"  ✅ Raízen: R$ {raizen['preco']}")

def main():
    print("🚀 Worker SELIX iniciado")
    print("⏱️  Coletando dados a cada 5 minutos")
    
    while True:
        try:
            coletar_dados()
        except Exception as e:
            print(f"❌ Erro: {e}")
        time.sleep(300)  # 5 minutos

if __name__ == "__main__":
    main()
