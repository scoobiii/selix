from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="SELIX FastAPI", version="7.2.5")


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
    """O módulo DSGE é opcional; sua ausência não deve derrubar a API."""
    try:
        from scripts.dsge_kalman import estimate_rstar
    except ImportError:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "error": "dsge_model_unavailable",
            },
            headers={"Cache-Control": "no-store"},
        )

    try:
        return estimate_rstar()
    except Exception:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unavailable",
                "error": "dsge_model_execution_failed",
            },
            headers={"Cache-Control": "no-store"},
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)
