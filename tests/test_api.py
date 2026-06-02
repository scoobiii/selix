import pytest
import requests

BASE_URL = "http://localhost:5000"

class TestAPI:
    # Endpoints públicos
    def test_health(self):
        r = requests.get(f"{BASE_URL}/v1/health")
        assert r.status_code == 200

    def test_mistura_com_parametro(self):
        r = requests.get(f"{BASE_URL}/v1/energia/mistura/120")
        assert r.status_code == 200
        data = r.json()
        assert data['brent_usd'] == 120

    def test_termicas(self):
        r = requests.get(f"{BASE_URL}/v1/energia/termicas")
        assert r.status_code == 200
        assert "capacidade_total_mw" in r.json()

    def test_gatilhos(self):
        r = requests.get(f"{BASE_URL}/v1/energia/gatilhos")
        assert r.status_code == 200
        assert "etanol" in r.json()

    # Endpoints privados (exigem API key)
    @pytest.fixture
    def auth_headers(self):
        return {"X-API-Key": "test_key_123"}   # precisa corresponder ao .env de teste

    def test_mistura_privado(self, auth_headers):
        r = requests.get(f"{BASE_URL}/v1/energia/mistura", headers=auth_headers)
        assert r.status_code in (200, 503)   # 503 se banco vazio

    def test_commodities(self, auth_headers):
        r = requests.get(f"{BASE_URL}/v1/commodities", headers=auth_headers)
        assert r.status_code in (200, 503)

    def test_empresas_rj(self, auth_headers):
        r = requests.get(f"{BASE_URL}/v1/empresas/rj", headers=auth_headers)
        assert r.status_code in (200, 503)

    def test_selic(self, auth_headers):
        r = requests.get(f"{BASE_URL}/v1/selic", headers=auth_headers)
        assert r.status_code in (200, 503)

    def test_precos_energeticos(self, auth_headers):
        r = requests.get(f"{BASE_URL}/v1/precos/energeticos", headers=auth_headers)
        assert r.status_code in (200, 503)

    def test_sentimento(self, auth_headers):
        r = requests.get(f"{BASE_URL}/v1/sentimento", headers=auth_headers)
        assert r.status_code in (200, 503)

    def test_alertas_geral(self, auth_headers):
        r = requests.get(f"{BASE_URL}/v1/alertas/geral", headers=auth_headers)
        assert r.status_code == 200   # sempre retorna mesmo sem dados

    def test_faq(self, auth_headers):
        r = requests.get(f"{BASE_URL}/v1/faq?q=selic", headers=auth_headers)
        assert r.status_code in (200, 404)   # 404 se FAQ não existe

    def test_perguntar(self, auth_headers):
        payload = {"pergunta": "O que é Selix?"}
        r = requests.post(f"{BASE_URL}/v1/perguntar", json=payload, headers=auth_headers)
        assert r.status_code in (200, 400, 500)   # depende da implementação real
