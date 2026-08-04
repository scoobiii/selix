import json
import requests
from datetime import datetime
from typing import Optional, Dict, Any
from functools import lru_cache
#!/usr/bin/env python3

class SELIX:
    TETO_1_DIGITO = 9.99
    JURO_REAL_MAXIMO = 5.0
    FOLGA_ROE = 0.95
    RELACAO_GLOBAL = 1.39
    PREMIO_RISCO_BRASIL = 4.5

    def __init__(self, inflacao=None, roe=None, selic_bacen=14.50):
        self.inflacao = inflacao or 4.48
        self.roe = roe or 31.23
        self.selic_bacen = self._get_selic_atual() or selic_bacen
        self.teto_juro_real = self.inflacao + self.JURO_REAL_MAXIMO
        self.teto_roe = self.roe * self.FOLGA_ROE
        self.teto_global = (self.RELACAO_GLOBAL * self.inflacao) + self.PREMIO_RISCO_BRASIL

    def calcular_selix(self):
        teto_efetivo = min(
            self.TETO_1_DIGITO,
            self.teto_juro_real,
            self.teto_roe,
            self.teto_global
        )
        
        # Garantir que juro_real ≤ 5% (arredondar para BAIXO)
        selix = (int(teto_efetivo / 0.25)) * 0.25
        
        # Verificação de segurança do juro real
        if selix - self.inflacao > self.JURO_REAL_MAXIMO:
            selix = self.inflacao + self.JURO_REAL_MAXIMO
            selix = (int(selix / 0.25)) * 0.25
        
        return min(selix, 9.99)

    def diagnosticar(self):
        economia = self.economia_anual()
        selix = self.calcular_selix()
        return {
            "selix_ideal": selix,
            "selic_atual": self.selic_bacen,
            "diferencial": round(self.selic_bacen - selix, 2),
            "juro_real_atual": round(self.selic_bacen - self.inflacao, 2),
            "juro_real_selix": round(selix - self.inflacao, 2),
            "investment_grade": selix <= 9.99,
            "convergencia_meses": abs(self.selic_bacen - selix) / 0.5
        }


def main():
    print("="*60)
    print("SELIX v3.2 - Modelo Matemático (Corrigido)")
    print("="*60)
    selix = SELIX()
    resultado = selix.diagnosticar()
    print(f"\n📊 RESULTADO:")
    print(f"   SELIX IDEAL: {resultado['selix_ideal']}%")
    print(f"   Selic Bacen: {resultado['selic_atual']}%")
    print(f"   Diferença: {resultado['diferencial']} pontos")
    print(f"   Juro real SELIX: {resultado['juro_real_selix']}%")
    print(f"   Investment Grade: {'SIM' if resultado['investment_grade'] else 'NÃO'}")
    print(f"   Convergência: {resultado['convergencia_meses']:.1f} meses")


if __name__ == "__main__":  # pragma: no cover
    main()  # pragma: no cover

    # ============================================================
    # T8: Dados reais da dívida pública e economia
    # ============================================================

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
    def _get_estoque_divida(ano: int = 2026) -> float:
        """Retorna o estoque da dívida pública em R$ bilhões"""
        projecoes = {
            2023: 6100.0,
            2024: 6400.0,
            2025: 6700.0,
            2026: 6900.0,
            2027: 7200.0,
        }
        return projecoes.get(ano, 6900.0)

    @staticmethod
    def get_divisa_publica_bi() -> float:
        """Retorna a dívida pública líquida atualizada (R$ bi)"""
        return SELIX._get_divida_publica() or 6900.0

