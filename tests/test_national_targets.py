"""Contract tests for long-term Brazil targets (no network access required)."""
import json
from pathlib import Path

TARGETS_PATH = Path(__file__).resolve().parents[1] / "data" / "national_targets_br.json"


def load_targets():
    return json.loads(TARGETS_PATH.read_text(encoding="utf-8"))


def test_contract_has_three_expected_indicators():
    data = load_targets()
    assert data["country"] == "BR"
    assert {item["id"] for item in data["indicators"]} == {
        "gdp_per_capita", "selic", "electricity_per_capita"
    }


def test_targets_are_marked_as_aspirational_not_forecasts():
    data = load_targets()
    assert data["status"] == "aspirational_targets_not_forecasts"
    for item in data["indicators"]:
        assert item["target"]["status"] in {
            "aspirational", "single_digit_policy_goal"
        }


def test_units_and_target_values_are_explicit():
    indicators = {item["id"]: item for item in load_targets()["indicators"]}
    assert indicators["gdp_per_capita"]["target"]["value"] == 130000
    assert indicators["gdp_per_capita"]["target"]["unit"] == "USD/person/year"
    assert indicators["selic"]["target"]["value"] == 9.99
    assert indicators["selic"]["target"]["unit"] == "percent_per_year"
    assert indicators["electricity_per_capita"]["target"]["value"] == 20000
    assert indicators["electricity_per_capita"]["target"]["unit"] == "kWh/person/year"


def test_unknown_observations_are_not_fabricated():
    indicators = {item["id"]: item for item in load_targets()["indicators"]}
    assert indicators["selic"]["baseline"]["value"] is None
    assert indicators["gdp_per_capita"]["baseline"]["year"] is None
    assert indicators["electricity_per_capita"]["baseline"]["year"] is None


def test_data_sources_are_present():
    for item in load_targets()["indicators"]:
        assert item["source"]["url"].startswith("https://")
        assert item["assumptions"]
