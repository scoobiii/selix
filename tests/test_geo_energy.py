#!/usr/bin/env python3
import pytest
import sys
sys.path.insert(0, '/root/selix')
from confidence.geo_energy_risk import GeoEnergyRiskCalculator

class TestGeoEnergyRisk:

    @pytest.fixture
    def calc(self):
        return GeoEnergyRiskCalculator()

    def test_ttf_price(self, calc):
        price = calc.get_ttf_price()
        assert 0 < price < 200

    def test_hh_price(self, calc):
        price = calc.get_hh_price()
        assert 0 < price < 20

    def test_jkm_price(self, calc):
        price = calc.get_jkm_price()
        assert price == 12.0

    def test_brent_price(self, calc):
        price = calc.get_brent_price()
        assert 40 < price < 150

    def test_brazil_mix(self, calc):
        mix = calc.get_brazil_mix()
        assert 'hidro' in mix
        assert mix['hidro'] == 0.65

    def test_brazil_risk_score(self, calc):
        score = calc.calculate_brazil_risk_score()
        assert 0 <= score <= 1

    def test_rating_from_score(self, calc):
        rating, score = calc.get_rating_from_score(0.15)
        assert rating == "AAA"
        rating, score = calc.get_rating_from_score(0.85)
        assert rating == "B"

    def test_update_prices(self, calc):
        calc.update_prices()
        # Verifica se inseriu pelo menos um registro
        with calc.conn as conn:
            cur = conn.execute("SELECT COUNT(*) FROM precos_energia_global")
            count = cur.fetchone()[0]
            assert count > 0

    def test_save_risk_rating(self, calc):
        score, rating = calc.save_risk_rating()
        assert rating in ["AAA","AA","A","BBB","BB","B"]
