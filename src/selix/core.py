#!/usr/bin/env python3
import sys
import json
import requests
import time
from datetime import datetime
from typing import Optional
from functools import lru_cache

class SELIX:
    TETO_1_DIGITO = 9.99
    JURO_REAL_MAXIMO = 5.0
    FOLGA_ROE = 0.95
    RELACAO_GLOBAL = 1.0
    PREMIO_RISCO_BRASIL = 5.0  # Ajustado para refletir prêmio de risco real (T10)

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_selic_atual() -> Optional[float]:
        """Busca a Selic atual da API do BCB"""
        try:
            url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.11/dados?formato=json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return float(data[-1]["valor"])
        except Exception:
            pass
        return None

    @staticmethod
    @lru_cache(maxsize=1)
    def _get_divida_publica() -> Optional[float]:
        """Busca o estoque da dívida pública líquida do STN/BCB"""
        try:
            url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.14558/dados?formato=json"
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data:
                    return float(data[-1]["valor"])
        except Exception:
            pass
        return 6900.0

    @staticmethod
    def get_divisa_publica_bi() -> float:
        return SELIX._get_divida_publica() or 6900.0

    def __init__(self, inflacao=None, roe=None, selic_bacen=14.25):
        # T7: Médias de 6 pontos hardcoded (AGO/2026)
        # TODO: Substituir por chamada de API dinâmica
        self.inflacao = inflacao or 4.48  # IPCA-12 (6-point avg)
        self.roe = roe or 31.23           # ROE B3 (6-point avg)
        self.selic_bacen = selic_bacen
        self.teto_juro_real = self.inflacao + self.JURO_REAL_MAXIMO
        self.teto_roe = self.roe * self.FOLGA_ROE
        self.teto_global = (self.RELACAO_GLOBAL * self.inflacao) + self.PREMIO_RISCO_BRASIL

    def calcular_selix_continuo(self):
        return min(
            self.TETO_1_DIGITO,
            self.teto_juro_real,
            self.teto_roe,
            self.teto_global
        )

    @staticmethod
    def quantizar(valor, grid=0.25):
        return (int(valor / grid)) * grid

    def calcular_selix(self):
        teto_efetivo = self.calcular_selix_continuo()
        selix = self.quantizar(teto_efetivo)
        if selix - self.inflacao > self.JURO_REAL_MAXIMO:
            selix = self.quantizar(self.inflacao + self.JURO_REAL_MAXIMO)
        return min(selix, self.TETO_1_DIGITO)

    def economia_anual(self, divida_publica_bi: Optional[float] = None):
        selix = self.calcular_selix()
        diferencial = self.selic_bacen - selix
        if diferencial <= 0:
            return None
        dpl = divida_publica_bi or self.get_divisa_publica_bi()
        return round(dpl * (diferencial / 100), 2)

    def diagnosticar(self):
        selix = self.calcular_selix()
        economia = self.economia_anual()
        return {
            "selix_continuo": round(self.calcular_selix_continuo(), 2),
            "selix_ideal": selix,
            "selic_atual": self.selic_bacen,
            "diferencial": round(self.selic_bacen - selix, 2),
            "juro_real_atual": round(self.selic_bacen - self.inflacao, 2),
            "juro_real_selix": round(selix - self.inflacao, 2),
            "investment_grade": selix <= self.TETO_1_DIGITO,
            "convergencia_meses": abs(self.selic_bacen - selix) / 0.5,
            "economia_anual_bi": economia,
            "divida_publica_bi": self.get_divisa_publica_bi(),
        }


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--daemon":
        while True:
            selix = SELIX()
            eco = selix.economia_anual()
            dpl = SELIX.get_divisa_publica_bi()
            print(f"[{datetime.now().isoformat()}] Dívida: R$ {dpl:.2f} bi | Economia: R$ {eco:.2f} bi/ano")
            sys.stdout.flush()
            time.sleep(60)
    else:
        resultado = SELIX().diagnosticar()
        print(f"\n📊 SELIX IDEAL: {resultado['selix_ideal']}%")
        print(f"   Selic atual: {resultado['selic_atual']}%")
        print(f"   Diferencial: {resultado['diferencial']:.2f} p.p.")
        print(f"   Juro real atual: {resultado['juro_real_atual']:.2f}%")
        print(f"   Juro real SELIX: {resultado['juro_real_selix']:.2f}%")
        print(f"   Investment Grade: {'SIM' if resultado['investment_grade'] else 'NÃO'}")
        print(f"   💰 Economia anual: R$ {resultado['economia_anual_bi']:.2f} bi")
        print(f"   Convergência: {resultado['convergencia_meses']:.1f} meses")


if __name__ == "__main__":  # pragma: no cover
    main()
