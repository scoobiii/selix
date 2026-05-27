#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SELIX Bluesky DM Agent v4.2
Fix crítico: chat.bsky.convo requer proxy para did:web:api.bsky.chat
"""

import os
import sys
import time
import logging
from atproto import Client, models
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("selix-bot")

POLLING_INTERVAL = 30
MAX_CACHE        = 10_000


def calcular_selix(ipca=4.48, roe=31.23, selic_bcb=14.50,
                   r_star=3.50, phi=1.39, delta=4.50):
    s_star = max(r_star * phi + delta, min(9.99, roe * 0.95, ipca + 5.0))
    desvio = round(selic_bcb - s_star, 2)
    score  = max(0.0, round(10 - 2 * max(0, desvio), 1))
    custo  = int(round(6.8 * max(0, desvio) / 100 * 1_000))
    return dict(s_star=round(s_star, 2), selic=selic_bcb,
                desvio=desvio, score=score, custo_bi=custo, ig=s_star <= 9.99)


def montar_dm(r):
    rating = ("🟢 ÓTIMO"   if r["score"] >= 9 else
              "🟡 BOM"     if r["score"] >= 7 else
              "🟠 ATENÇÃO" if r["score"] >= 5 else
              "🔴 CRÍTICO" if r["score"] >= 3 else
              "🚨 EMERGÊNCIA")
    ig = "✅ Investment Grade possível" if r["ig"] else "❌ IG bloqueado"
    return (
        f"📊 SELIX — Taxa Selic Ótima\n"
        f"{'─'*30}\n"
        f"🎯 s* (ótima):   {r['s_star']}%\n"
        f"📉 Selic BCB:    {r['selic']}%\n"
        f"⚠️  Desvio:      +{r['desvio']} pp\n"
        f"💸 Custo:        R$ {r['custo_bi']} bi/ano\n"
        f"{'─'*30}\n"
        f"📈 Score {r['score']}/10 — {rating}\n"
        f"{ig}\n"
        f"🌾 Etanol E32 (Brent >US$100)\n"
        f"🔬 Z3 SMT + Lean 4 provado\n"
        f"🔗 github.com/scoobiii/selix"
    )


def main():
    load_dotenv()
    username = os.getenv("BLUESKY_USERNAME")
    password = os.getenv("BLUESKY_APP_PASSWORD")

    if not username or not password:
        log.error("Configure BLUESKY_USERNAME e BLUESKY_APP_PASSWORD no .env")
        sys.exit(1)

    client = Client()
    client.login(username, password)
    log.info(f"✅ Conectado: @{client.me.handle} ({client.me.display_name})")

    # FIX: proxy obrigatório para chat.bsky.convo.*
    # Sem isso: HTTP 501 em todos os endpoints de DM
    dm = client.with_bsky_chat_proxy().chat.bsky.convo
    log.info("✅ Proxy chat configurado → did:web:api.bsky.chat")

    respondidas = set()
    total = 0
    log.info(f"🔄 Polling a cada {POLLING_INTERVAL}s — Ctrl+C para parar")

    while True:
        try:
            convos = dm.list_convos({"limit": 20}).convos or []

            for convo in convos:
                msgs = dm.get_messages({"convoId": convo.id, "limit": 10}).messages or []

                for msg in msgs:
                    if msg.id in respondidas:
                        continue
                    if not hasattr(msg, "sender") or not hasattr(msg, "text"):
                        respondidas.add(msg.id)
                        continue
                    if msg.sender.did == client.me.did:
                        respondidas.add(msg.id)
                        continue
                    texto = (msg.text or "").strip()
                    if not texto:
                        respondidas.add(msg.id)
                        continue

                    selix = calcular_selix()
                    try:
                        dm.send_message(
                            models.ChatBskyConvoSendMessage.Data(
                                convo_id=convo.id,
                                message=models.ChatBskyConvoDefs.MessageInput(
                                    text=montar_dm(selix)
                                ),
                            )
                        )
                        total += 1
                        handle = getattr(msg.sender, "handle", msg.sender.did[:12])
                        log.info(
                            f"📨 @{handle}: {texto[:50]!r} → enviado "
                            f"s*={selix['s_star']}% score={selix['score']} [#{total}]"
                        )
                    except Exception as e:
                        log.warning(f"send_message falhou ({convo.id}): {e}")

                    respondidas.add(msg.id)
                    if len(respondidas) > MAX_CACHE:
                        respondidas = set(list(respondidas)[-5_000:])

        except KeyboardInterrupt:
            log.info(f"\n🛑 Encerrado — {total} DMs enviadas.")
            break
        except Exception as e:
            log.error(f"Loop: {e}")

        time.sleep(POLLING_INTERVAL)


if __name__ == "__main__":
    main()
