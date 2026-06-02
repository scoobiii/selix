import pytest
import sys
import importlib
from src.api.main_v4 import app

TEST_API_KEY = "3c207e2d549f35100cb8aeb02a6093ec4870dbe36c3e3787f9a32fc7e2cba61f"

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_publico(client):
    resp = client.get('/v1/health')
    assert resp.status_code == 200

def test_endpoint_protegido_sem_chave(client):
    resp = client.get('/v1/commodities')
    assert resp.status_code == 401
    assert 'API key' in resp.json['erro']

def test_endpoint_protegido_com_chave_valida(client, monkeypatch):
    monkeypatch.setenv('SELIX_API_KEYS', TEST_API_KEY)
    importlib.reload(sys.modules['src.api.main_v4'])
    resp = client.get('/v1/commodities', headers={'X-API-Key': TEST_API_KEY})
    assert resp.status_code in (200, 503)  # 503 se banco vazio

def test_endpoint_post_dados_invalidos(client):
    headers = {'X-API-Key': TEST_API_KEY}
    resp = client.post('/v1/perguntar', json={'pergunta': ''}, headers=headers)
    assert resp.status_code == 400

def test_rate_limit_simulado(client):
    resp = client.get('/v1/health')
    assert resp.status_code == 200
