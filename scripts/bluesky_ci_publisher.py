#!/usr/bin/env python3
"""Publish only a validated CI-generated SELIX official snapshot to Bluesky."""
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import json
import requests

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_PATH = ROOT / "public" / "selix-official.json"
API_BASE = "https://bsky.social/xrpc"

def load_snapshot():
    data = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
    if data.get("status") != "verified" or data.get("source", {}).get("series") != 432:
        raise ValueError("snapshot must be verified and sourced from BCB SGS 432")
    market, model = data["market"], data["model"]
    current, ideal = float(market["selic_atual"]), float(model["selic_ideal"])
    if abs(round(current - ideal, 2) - float(market["diferencial_pp"])) > 0.001:
        raise ValueError("snapshot differential does not reconcile")
    if not data.get("content_sha256") or not data["source"].get("observation_date"):
        raise ValueError("snapshot provenance/hash missing")
    return data

def main():
    handle, password = os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_APP_PASSWORD")
    if not handle or not password:
        raise SystemExit("Missing Bluesky credentials; publication blocked")
    try:
        data = load_snapshot()
    except Exception as exc:
        raise SystemExit(f"Invalid official snapshot; publication blocked: {exc}")
    market, model = data["market"], data["model"]
    post_text = (
        "SELIX — snapshot oficial\n\n"
        f"Selic observada: {market['selic_atual']:.2f}%\n"
        f"Selic ideal do modelo: {model['selic_ideal']:.2f}%\n"
        f"Diferencial calculado: {market['diferencial_pp']:.2f} p.p.\n"
        f"Observação BCB: {data['source']['observation_date']}\n"
        f"Snapshot SHA-256: {data['content_sha256']}\n\n"
        "Fonte: Banco Central do Brasil, SGS 432. Ferramenta de apoio à decisão; não substitui o COPOM."
    )
    session_resp = requests.post(f"{API_BASE}/com.atproto.server.createSession",
        json={"identifier": handle, "password": password}, timeout=20)
    session_resp.raise_for_status()
    session = session_resp.json()
    post_resp = requests.post(f"{API_BASE}/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {session['accessJwt']}"},
        json={"repo": session["did"], "collection": "app.bsky.feed.post",
              "record": {"$type": "app.bsky.feed.post", "text": post_text,
                         "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")}},
        timeout=20)
    post_resp.raise_for_status()
    print("Validated snapshot published successfully.")

if __name__ == "__main__":
    main()
