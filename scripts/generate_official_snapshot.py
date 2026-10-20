#!/usr/bin/env python3
"""Compatibility wrapper for the historical-only snapshot generator."""
from __future__ import annotations

import json

from scripts.build_official_snapshot import build_snapshot, write_snapshot


def main() -> int:
    snapshot = build_snapshot()
    write_snapshot(snapshot)
    print(json.dumps({
        "status": snapshot["status"],
        "is_current": snapshot["is_current"],
        "source": snapshot["source"],
        "content_sha256": snapshot["content_sha256"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
