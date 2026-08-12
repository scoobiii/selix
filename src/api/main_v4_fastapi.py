from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
import json
from datetime import datetime, timezone

# Importa as funções do seu core
from src.selix.config import SELIC_IDEAL, DIFERENCIAL
from scripts.dsge_kalman import estimate_rstar

app = FastAPI(title="SELIX FastAPI", version="v7.2.3")

@app.get("/v1/health")
async def health_check():
    return {"status": "ok", "versao": "4.0-fastapi", "db": "ok"}

@app.get("/v1/selic/snapshot")
async def snapshot():
    selic_atual = round(SELIC_IDEAL + DIFERENCIAL, 2)
    economia_bi = 414  # Placeholder, se quiser puxar do banco depois
    return {
        "selic_atual": selic_atual,
        "selic_ideal_quantizada": SELIC_IDEAL,
        "diferencial_pp": DIFERENCIAL,
        "economia_anual_bi": economia_bi,
        "fonte": "src.selix.config"
    }

@app.get("/v1/dsge/rstar")
async def dsge_rstar():
    # O estimate_rstar() retorna um dicionário, não uma string JSON. O FastAPI converte automaticamente.
    return estimate_rstar()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
