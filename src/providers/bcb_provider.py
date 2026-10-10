#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coleta Selic no BCB (SGS) sem fallback de série para o caminho CURRENT."""
from datetime import date, timedelta
import requests
from .base_provider import DataProvider

SGS_META = 432
SGS_DIARIA = 11


class BCBProvider(DataProvider):
    def get_brent(self) -> dict:
        return {"success": False, "source": "BCB"}

    def _fetch_sgs(self, codigo: int) -> dict:
        fim = date.today()
        ini = fim - timedelta(days=30)
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados"
        params = {
            "formato": "json",
            "dataInicial": ini.strftime("%d/%m/%Y"),
            "dataFinal": fim.strftime("%d/%m/%Y"),
        }
        resp = requests.get(url, params=params, timeout=20)
        if resp.status_code != 200:
            return {
                "success": False,
                "source": "BCB",
                "http": resp.status_code,
                "serie": codigo,
            }
        rows = resp.json()
        if not rows:
            return {"success": False, "source": "BCB", "serie": codigo, "error": "empty"}
        row = rows[-1]
        return {
            "success": True,
            "rate": float(row["valor"]),
            "data_bcb": row.get("data"),
            "serie": codigo,
            "source": f"BCB SGS {codigo}",
        }

    def get_selic_meta(self) -> dict:
        """Caminho estrito para Selic CURRENT: somente SGS 432."""
        try:
            return self._fetch_sgs(SGS_META)
        except Exception as e:
            return {"success": False, "source": "BCB", "serie": SGS_META, "error": str(e)}

    def get_selic(self) -> dict:
        """Compatibilidade legada; mantém fallback da série diária 11.

        CURRENT não deve usar este método: use `get_selic_meta()`.
        """
        r = self.get_selic_meta()
        if r.get("success"):
            return r
        try:
            r2 = self._fetch_sgs(SGS_DIARIA)
            if r2.get("success"):
                r2["nota"] = "fallback serie 11; meta 432 falhou"
                return r2
            return r
        except Exception as e:
            return {"success": False, "source": "BCB", "error": str(e)}
