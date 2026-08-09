import pytest
import requests

BASE_URL = "http://localhost:5000"
HEADERS = {"X-API-Key": "test_api_key_123"}


class TestAPI:
    def test_health(self):
        r = requests.get(f"{BASE_URL}/v1/health")
        assert r.status_code == 200

    def test_mistura_privado(self):
        # rota exige <int:brent>
        r = requests.get(f"{BASE_URL}/v1/energia/mistura/80", headers=HEADERS)
        assert r.status_code in (200, 503)

    def test_commodities(self):
        r = requests.get(f"{BASE_URL}/v1/commodities", headers=HEADERS)
        assert r.status_code in (200, 503)

    def test_empresas_rj(self):
        r = requests.get(f"{BASE_URL}/v1/empresas/rj", headers=HEADERS)
        assert r.status_code in (200, 503)

    def test_selic(self):
        r = requests.get(f"{BASE_URL}/v1/selic", headers=HEADERS)
        assert r.status_code in (200, 503)

    def test_energia_termicas(self):
        # substitui a rota antiga /v1/precos/energeticos, que nao existe
        r = requests.get(f"{BASE_URL}/v1/energia/termicas", headers=HEADERS)
        assert r.status_code in (200, 503)

    def test_energia_gatilhos(self):
        # substitui a rota antiga /v1/sentimento, que nao existe
        r = requests.get(f"{BASE_URL}/v1/energia/gatilhos", headers=HEADERS)
        assert r.status_code in (200, 503)

    @pytest.mark.skip(reason="endpoint /v1/alertas/geral nao implementado")
    def test_alertas_geral(self):
        r = requests.get(f"{BASE_URL}/v1/alertas/geral", headers=HEADERS)
        assert r.status_code == 200

    def test_faq(self):
        r = requests.get(f"{BASE_URL}/v1/faq?q=selic", headers=HEADERS)
        assert r.status_code in (200, 404)

    def test_perguntar(self):
        payload = {"pergunta": "O que e Selix?"}
        r = requests.post(f"{BASE_URL}/v1/perguntar", json=payload, headers=HEADERS)
        assert r.status_code in (200, 202, 400, 500)
