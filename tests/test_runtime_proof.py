import time, hashlib

def test_runtime_timestamp():
    """
    Output depende do momento de execução.
    Impossível simular sem rodar.
    """
    ts = str(time.time_ns())
    h  = hashlib.sha256(ts.encode()).hexdigest()[:8]
    # Imprime para captura externa
    print(f"\nRUNTIME_HASH={h} TS={ts}")
    # Verifica que o hash é derivado do timestamp
    assert hashlib.sha256(ts.encode()).hexdigest()[:8] == h
