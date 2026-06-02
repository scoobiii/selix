#!/usr/bin/env python3
"""
responder_inteligente.py — SELIX v4.0
- Cache de sessão Bluesky
- Respostas humanizadas com thread automática
- CC a stakeholders por segmento
"""

import sqlite3, time, os, json
from datetime import date, datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from atproto import Client, models

load_dotenv('/root/selix/.env')

DB_PATH             = "/root/selix/selix.db"
SESSION_FILE        = "/root/selix/.bluesky_session.json"
MAX_REPLIES_PER_RUN = 3
PAUSE_BETWEEN       = 8
SESSION_TTL         = 3600

def get_client() -> Client:
    client = Client()
    sp = Path(SESSION_FILE)
    if sp.exists() and (time.time() - sp.stat().st_mtime) < SESSION_TTL:
        try:
            client.login(session_string=sp.read_text().strip())
            print("✅ Sessão reutilizada")
            return client
        except Exception as e:
            print(f"⚠️  Sessão inválida: {e}")
    client.login(os.getenv('BLUESKY_USERNAME'), os.getenv('BLUESKY_APP_PASSWORD'))
    sp.write_text(client.export_session_string())
    print("🔑 Login realizado e sessão salva.")
    return client

def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS notificacoes_respondidas (uri TEXT PRIMARY KEY, respondido_em TIMESTAMP)")
    conn.commit()
    return conn

def ja_respondida(conn, uri):
    return conn.execute("SELECT 1 FROM notificacoes_respondidas WHERE uri=?", (uri,)).fetchone() is not None

def marcar_respondida(conn, uri):
    conn.execute("INSERT OR IGNORE INTO notificacoes_respondidas VALUES (?,?)", (uri, datetime.now(timezone.utc).isoformat()))
    conn.commit()

def buscar_resposta(conn, pergunta: str) -> dict:
    p = pergunta.lower()
    row = conn.execute(
        "SELECT id, resposta, segmento, thread_json, cc_handles FROM respostas_banco WHERE ? LIKE '%' || dor_keyword || '%'", (p,)
    ).fetchone()
    if not row:
        row = conn.execute(
            "SELECT id, resposta, segmento, thread_json, cc_handles FROM respostas_banco WHERE dor_keyword='default' LIMIT 1"
        ).fetchone()
    if row:
        rid, resposta, segmento, thread_json, cc_handles = row
        conn.execute("UPDATE respostas_banco SET uso_count=uso_count+1, ultimo_uso=? WHERE id=?", (date.today().isoformat(), rid))
        conn.commit()
        return {
            "resposta":    resposta,
            "segmento":    segmento,
            "thread_json": json.loads(thread_json) if thread_json else None,
            "cc_handles":  cc_handles or "",
        }
    return {"resposta": "🤖 SELIX: Selic ideal = 9,25%. github.com/scoobiii/selix #Selix", "segmento": "geral", "thread_json": None, "cc_handles": ""}

def registrar_post(conn, conteudo: str):
    conn.execute("INSERT INTO posts (conteudo, tipo, synthetic, publicado_em) VALUES (?, 'opiniao', 0, ?)", (conteudo, datetime.now(timezone.utc).isoformat()))
    conn.commit()

def enviar_post_simples(client, texto, reply_ref=None):
    try:
        r = client.send_post(texto, reply_to=reply_ref)
        return r.uri, r.cid
    except Exception as e:
        print(f"  ❌ Erro ao postar: {e}")
        return None, None

def enviar_thread(client, partes, reply_ref=None) -> bool:
    root_ref   = reply_ref
    parent_ref = reply_ref
    for i, parte in enumerate(partes):
        print(f"  📤 Parte {i+1}/{len(partes)}: {parte[:60]}…")
        uri, cid = enviar_post_simples(client, parte, parent_ref)
        if not uri:
            return False
        strong = models.ComAtprotoRepoStrongRef.Main(uri=uri, cid=cid)
        if i == 0 and not root_ref:
            root_ref = models.AppBskyFeedPost.ReplyRef(parent=strong, root=strong)
        parent_ref = models.AppBskyFeedPost.ReplyRef(
            parent=strong,
            root=root_ref.root if root_ref else strong,
        )
        if i < len(partes) - 1:
            time.sleep(PAUSE_BETWEEN)
    return True

def montar_reply_ref(post):
    strong = models.ComAtprotoRepoStrongRef.Main(uri=post.uri, cid=post.cid)
    return models.AppBskyFeedPost.ReplyRef(parent=strong, root=strong)

def responder_mencoes(client: Client):
    conn = get_conn()
    try:
        notifs = client.app.bsky.notification.list_notifications()
    except Exception as e:
        print(f"❌ Erro ao buscar notificações: {e}")
        conn.close()
        return

    reply_count = 0
    for notif in notifs.notifications:
        if reply_count >= MAX_REPLIES_PER_RUN:
            break
        if notif.reason != 'mention':
            continue
        if ja_respondida(conn, notif.uri):
            continue
        try:
            post     = client.app.bsky.feed.get_post_thread(uri=notif.uri).thread.post
            pergunta = post.text.replace(os.getenv('BLUESKY_USERNAME', ''), '').strip()
        except Exception as e:
            print(f"⚠️  Erro ao ler post: {e}")
            continue

        dados     = buscar_resposta(conn, pergunta)
        reply_ref = montar_reply_ref(post)
        partes    = dados["thread_json"]
        cc        = dados["cc_handles"]
        segmento  = dados["segmento"]
        prefixo   = f"@{post.author.handle} "

        if partes:
            partes = list(partes)
            partes[0] = prefixo + partes[0]
            if cc:
                cc_txt = "\n" + " ".join(f"@{h.strip()}" for h in cc.split(",") if h.strip())
                partes[-1] = partes[-1] + cc_txt
            ok = enviar_thread(client, partes, reply_ref)
            texto_log = partes[0]
        else:
            texto = prefixo + dados["resposta"]
            if cc:
                texto += " " + " ".join(f"@{h.strip()}" for h in cc.split(",") if h.strip())
            _, _ = enviar_post_simples(client, texto, reply_ref)
            ok = True
            texto_log = texto

        if ok:
            marcar_respondida(conn, notif.uri)
            registrar_post(conn, texto_log)
            print(f"✅ @{post.author.handle} | segmento: {segmento} | partes: {len(partes) if partes else 1}")
            reply_count += 1

    conn.close()
    print(f"📊 Respostas enviadas: {reply_count}/{MAX_REPLIES_PER_RUN}")

if __name__ == "__main__":
    client = get_client()
    responder_mencoes(client)
