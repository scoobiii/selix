#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Coleta Selic no BCB (SGS) sem fallback de série para o caminho CURRENT."""
from datetime import date, datetime, timedelta
import math
import requests
from .base_provider import DataProvider

SGS_META = 432
SGS_DIARIA = 11


class BCBProvider(DataProvider):
    def get_brent(self) -> dict:
        return {"success": False, "source": "BCB"}

    def _fetch_sgs(self, codigo: int) -> dict:
        # /ultimos/N evita a janela dataInicial/dataFinal, que pode ser
        # rejeitada pelo SGS para séries diárias quando a janela excede 10 anos.
        # Na série 432, a data é a vigência da última alteração da meta; ela
        # pode legitimamente ser antiga enquanto a meta permanece inalterada.
        url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{codigo}/dados/ultimos/10"
        resp = requests.get(url, params={"formato": "json"}, timeout=20)
        resp.raise_for_status()
        rows = resp.json()
        if not isinstance(rows, list) or not rows:
            raise ValueError(f"BCB SGS {codigo} returned no observations")

        parsed = []
        for row in rows:
            if not isinstance(row, dict) or "data" not in row or "valor" not in row:
                raise ValueError(f"BCB SGS {codigo} returned an invalid observation")
            observed_on = datetime.strptime(row["data"], "%d/%m/%Y").date()
            rate = float(row["valor"])
            if not math.isfinite(rate) or not 0.0 < rate < 100.0:
                raise ValueError(f"BCB SGS {codigo} returned an invalid rate")
            if observed_on > date.today() + timedelta(days=1):
                raise ValueError(f"BCB SGS {codigo} returned a future observation")
            parsed.append((observed_on, rate))

        observed_on, rate = max(parsed, key=lambda item: item[0])
        return {
            "success": True,
            "rate": rate,
            "data_bcb": observed_on.strftime("%d/%m/%Y"),
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
}
