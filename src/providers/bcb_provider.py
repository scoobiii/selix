#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coleta Selic no BCB (SGS). Sem número discricionário no código."""
import requests
from .base_provider import DataProvider

# 432 = Meta Selic Copom (% a.a.) — referência de "a Selic está em X%"
# 11  = Selic diária (over) — fallback
SGS_META = 432
SGS_DIARIA = 11


class BCBProvider(DataProvider):
    def get_brent(self) -> dict:
        return {"success": False, "source": "BCB"}

    def _fetch_sgs(self, codigo: int) -> dict:
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados/ultimo"
        resp = requests.get(url, params={"formato": "json"}, timeout=15)
        if resp.status_code != 200:
            return {"success": False, "source": "BCB", "http": resp.status_code, "serie": codigo}
        row = resp.json()[0]
        return {
            "success": True,
            "rate": float(row["valor"]),
            "data_bcb": row.get("data"),
            "serie": codigo,
            "source": f"BCB SGS {codigo}",
        }

    def get_selic(self) -> dict:
        try:
            r = self._fetch_sgs(SGS_META)
            if r.get("success"):
                return r
            r2 = self._fetch_sgs(SGS_DIARIA)
            if r2.get("success"):
                r2["nota"] = "fallback serie 11 (diaria); meta 432 falhou"
                return r2
            return r
        except Exception as e:
            return {"success": False, "source": "BCB", "error": str(e)}
