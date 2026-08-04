#!/usr/bin/env python3
"""
SELIX v7.0 - Choques Exógenos (Oil/TTF)
"""

import requests
import os
from typing import Dict

class CommoditiesAPI:
    """Interface com APIs de commodities"""

    def __init__(self):
        self.eia_api_key = os.getenv('EIA_API_KEY', '')

    def get_oil_price(self) -> float:
        """Preço do petróleo (Brent) em US$/barril"""
        # Em produção: API da EIA ou Yahoo Finance
        try:
            url = "https://api.eia.gov/series?api_key={}&series_id=PET.RBRTE.M".format(self.eia_api_key)
            response = requests.get(url, timeout=5)
            data = response.json()
            return float(data["series"][0]["data"][0][1])
        except Exception:
            return 95.19  # fallback

    def get_ttf_price(self) -> float:
        """Preço do gás TTF em EUR/MWh"""
        # Em produção: API da EIA ou TTF
        return 40.0  # fallback

    def get_precos(self) -> Dict[str, float]:
        """Todos os preços"""
        return {
            "oil": self.get_oil_price(),
            "ttf": self.get_ttf_price(),
        }

    def ajuste_choque(self) -> float:
        """Ajuste no juro real devido a choques"""
        oil = self.get_oil_price()
        ttf = self.get_ttf_price()

        OIL_REF = 80.0
        TTF_REF = 40.0

        ajuste = 0.0
        if oil > OIL_REF:
            ajuste += (oil - OIL_REF) / OIL_REF * 0.5
        if ttf > TTF_REF:
            ajuste += (ttf - TTF_REF) / TTF_REF * 0.3

        return round(ajuste, 2)
