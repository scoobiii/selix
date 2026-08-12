#!/usr/bin/env python3
# verify_grok_runtime.py — verifica se o Grok tem runtime real
# Uso: python verify_grok_runtime.py RUNTIME_HASH TS
import hashlib, time, sys

if len(sys.argv) != 3:
    print("Uso: python verify_grok_runtime.py <HASH> <TS>")
    sys.exit(1)

hash_grok = sys.argv[1]
ts_grok   = sys.argv[2]

# 1. Hash é derivado do TS?
hash_esperado = hashlib.sha256(ts_grok.encode()).hexdigest()[:8]
hash_ok = hash_esperado == hash_grok

# 2. TS é temporalmente plausível?
ts_agora = time.time_ns()
diff_seg = (ts_agora - int(ts_grok)) / 1e9
ts_ok = 0 < diff_seg < 600  # até 10 min atrás

print(f"RUNTIME_HASH recebido : {hash_grok}")
print(f"RUNTIME_HASH esperado : {hash_esperado}")
print(f"Hash consistente      : {'✅' if hash_ok else '❌ ALUCINAÇÃO'}")
print(f"Timestamp diff        : {diff_seg:.0f}s atrás")
print(f"Timestamp plausível   : {'✅' if ts_ok else '❌ IMPOSSÍVEL'}")
print()
if hash_ok and ts_ok:
    print("✅ RUNTIME REAL — Grok tem sandbox de execução")
elif hash_ok and not ts_ok:
    print("⚠️  Hash consistente mas TS implausível — pode ter rodado antes")
else:
    print("❌ ALUCINAÇÃO — Grok inventou o resultado sem executar")
