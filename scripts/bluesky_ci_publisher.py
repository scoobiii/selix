"""Publish a live SPI-validated Selic observation; never read a committed snapshot as CURRENT."""
import hashlib
import json
import os
from datetime import datetime, timezone
import requests

API_BASE = "https://bsky.social/xrpc"


def load_live_snapshot() -> dict:
    from src.selix.spi import build_current_snapshot, assert_current_provenance

    data = build_current_snapshot()
    assert_current_provenance(data)
    current = float(data["selic_atual"])
    ideal = float(data["selic_ideal"])
    if not (0.0 < current < 100.0 and 0.0 < ideal < 100.0):
        raise ValueError("Selic rates outside valid range")
    if abs(round(current - ideal, 2) - float(data["diferencial"])) > 0.001:
        raise ValueError("live snapshot differential does not reconcile")
    canonical = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    data["content_sha256"] = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return data


def main():
    handle, password = os.getenv("BLUESKY_USERNAME"), os.getenv("BLUESKY_APP_PASSWORD")
    if not handle or not password:
        raise SystemExit("Missing Bluesky credentials; publication blocked")

    try:
        data = load_live_snapshot()
    except Exception as exc:
        raise SystemExit(f"Invalid or unavailable live BCB observation; publication blocked: {exc}")

    post_text = (
        "SELIX — observação oficial consultada em runtime\n\n"
        f"Meta Selic BCB SGS 432: {data['selic_atual']:.2f}% a.a.\n"
        f"Data da observação BCB: {data['selic_atual_data_bcb']}\n"
        f"Consulta: {data['fetched_at']}\n"
        f"Selic ideal do modelo: {data['selic_ideal']:.2f}% a.a. (não é taxa oficial)\n"
        f"Diferencial do modelo: {data['diferencial']:.2f} p.p.\n"
        f"Proveniência: {data['provenance']}\n"
        f"SHA-256 do payload: {data['content_sha256']}\n"
        "Apoio à decisão; não substitui o COPOM."
    )
    if len(post_text) > 300:
        post_text = (
            f"SELIX | Selic BCB SGS 432: {data['selic_atual']:.2f}% a.a.; "
            f"observação {data['selic_atual_data_bcb']}. "
            f"Ideal do modelo: {data['selic_ideal']:.2f}% a.a. (não oficial). "
            "Dados consultados em runtime; não substitui o COPOM."
        )

    session_resp = requests.post(
        f"{API_BASE}/com.atproto.server.createSession",
        json={"identifier": handle, "password": password},
        timeout=20,
    )
    session_resp.raise_for_status()
    session = session_resp.json()
    post_resp = requests.post(
        f"{API_BASE}/com.atproto.repo.createRecord",
        headers={"Authorization": f"Bearer {session['accessJwt']}"},
        json={
            "repo": session["did"],
            "collection": "app.bsky.feed.post",
            "record": {
                "$type": "app.bsky.feed.post",
                "text": post_text,
                "createdAt": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            },
        },
        timeout=20,
    )
    post_resp.raise_for_status()
    print("Live SPI-validated observation published successfully.")


if __name__ == "__main__":
    main()
