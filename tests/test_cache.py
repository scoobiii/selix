import pytest
from unittest.mock import patch, MagicMock

def test_redis_connection():
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379, decode_responses=True)
        r.set('test_key', 'test_value')
        assert r.get('test_key') == 'test_value'
        r.delete('test_key')
    except ImportError:
        pytest.skip("Redis não instalado")
    except ConnectionError:
        pytest.skip("Redis não está rodando")

def test_cache_decorator():
    # Testar cache de resultados
    pass
