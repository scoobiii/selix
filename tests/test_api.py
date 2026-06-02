import pytest
import requests
import os

BASE_URL = "http://localhost:5000"
API_KEY = os.getenv("SELIX_API_KEY", "")
if not API_KEY:
    # Tenta ler do arquivo de chave gerado
    import subprocess
    result = subprocess.run(["python", "/root/selix/scripts/generate_api_key.py", "api_test", "free", "1"], capture_output=True, text=True)
    for line in result.stdout.split("\n"):
        if "API Key:" in line:
            API_KEY = line.split(":")[1].strip()
            break

HEADERS = {"X-API-Key": API_KEY}

class TestAPI:
    def test_health(self):
        r = requests.get(f"{BASE_URL}/v1/health")
        assert r.status_code == 200

    def test_mistura_privado(self):
        r = requests.get(f"{BASE_URL}/v1/energia/mistura", headers=HEADERS)
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

    def test_precos_energeticos(self):
        r = requests.get(f"{BASE_URL}/v1/precos/energeticos", headers=HEADERS)
        assert r.status_code in (200, 503)

    def test_sentimento(self):
        r = requests.get(f"{BASE_URL}/v1/sentimento", headers=HEADERS)
        assert r.status_code in (200, 503)

    def test_alertas_geral(self):
        r = requests.get(f"{BASE_URL}/v1/alertas/geral", headers=HEADERS)
        assert r.status_code == 200

    def test_faq(self):
        r = requests.get(f"{BASE_URL}/v1/faq?q=selic", headers=HEADERS)
        assert r.status_code in (200, 404)

    def test_perguntar(self):
        payload = {"pergunta": "O que é Selix?"}
        r = requests.post(f"{BASE_URL}/v1/perguntar", json=payload, headers=HEADERS)
        assert r.status_code in (200, 400, 500)
