# tests/conftest.py
import subprocess
import time
import pytest
import requests
import os
import signal

@pytest.fixture(scope="session", autouse=True)
def start_api():
    """Inicia a API em background antes de todos os testes e a encerra no final."""
    # Mata processos antigos
    subprocess.run("pkill -f 'main_v4' || true", shell=True)
    # Inicia a API
    env = os.environ.copy()
    env["PYTHONPATH"] = "/root/selix"
    env["REQUESTS_CA_BUNDLE"] = "/root/selix/venv/lib/python3.13/site-packages/certifi/cacert.pem"
    proc = subprocess.Popen(
        ["python", "-m", "src.api.main_v4"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        preexec_fn=os.setsid
    )
    # Aguarda a API ficar disponível
    for _ in range(30):
        try:
            r = requests.get("http://localhost:5000/v1/health")
            if r.status_code == 200:
                break
        except:
            pass
        time.sleep(1)
    else:
        raise RuntimeError("API não iniciou a tempo")

    yield

    # Encerra a API e seus filhos
    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    proc.wait()
