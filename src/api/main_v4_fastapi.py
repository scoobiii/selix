from fastapi import FastAPI
from fastapi.responses import JSONResponse

from scripts.dsge_kalman import estimate_rstar

app = FastAPI(title="SELIX FastAPI", version="7.2.4")


@app.get("/v1/health")
async def health_check():
    return {"status": "ok", "versao": app.version}


@app.get("/v1/selic/snapshot")
async def snapshot():
    """Retorna Selic CURRENT somente quando validada pelo SPI/BCB SGS 432."""
    try:
        from src.selix.spi import build_current_snapshot

        return build_current_snapshot()
    except Exception:
        # Falha fechada: nunca converte indisponibilidade em valor estimado/antigo.
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "error": "official_bcb_data_unavailable",
                "source": "BCB SGS 432",
                "provenance": "runtime:BCB SGS 432",
            },
            headers={"Cache-Control": "no-store"},
        )


@app.get("/v1/dsge/rstar")
async def dsge_rstar():
    # estimate_rstar() retorna um dicionário; FastAPI serializa automaticamente.
    return estimate_rstar()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
