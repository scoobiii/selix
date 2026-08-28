#!/usr/bin/env python3
"""Gate for CURRENT SELIC data.

Fails closed. It is intentionally impossible to pass this gate with a caller
supplied or fixture supplied SELIC. The market value must come from BCB SGS 432
at runtime.
"""
from src.selix.spi import build_current_snapshot, assert_current_provenance


def main() -> int:
    data = build_current_snapshot()
    assert_current_provenance(data)
    print("GATE: PASS")
    print(f"SELIC atual: {data['selic_atual']:.2f}%")
    print(f"SELIC ideal: {data['selic_ideal']:.2f}%")
    print(f"Diferencial: {data['diferencial']:.2f} p.p.")
    print(f"Fonte: {data['selic_atual_fonte']}")
    print(f"Data BCB: {data['selic_atual_data_bcb']}")
    print(f"Fetched: {data['fetched_at']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
