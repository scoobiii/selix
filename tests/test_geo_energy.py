import pytest
import sys
sys.path.insert(0, '/root/selix')
from confidence.geo_energy_risk import GeoEnergyRiskCalculator

class TestGeoEnergyRisk:
    def test_ttf_price_range(self):
        calc = GeoEnergyRiskCalculator()
        price = calc.get_ttf_price()
        assert 0 < price < 200
    
    def test_brent_price_range(self):
        calc = GeoEnergyRiskCalculator()
        price = calc.get_brent_price()
        assert 40 < price < 150
    
    def test_brazil_score_range(self):
        calc = GeoEnergyRiskCalculator()
        score = calc.calculate_brazil_risk_score()
        assert 0 <= score <= 1
    
    def test_rating_consistency(self):
        calc = GeoEnergyRiskCalculator()
        rating, _ = calc.get_rating_from_score(0.15)
        assert rating == "AAA"
        rating, _ = calc.get_rating_from_score(0.85)
        assert rating == "B"
    
    def test_investment_grade_logic(self):
        calc = GeoEnergyRiskCalculator()
        rating, score, _ = calc.save_investment_grade()
        assert rating in ["AAA", "AA", "A", "BBB", "BB", "B"]
        assert 40 <= score <= 95
