#!/usr/bin/env python3
import sqlite3
import random
import datetime
import os

TEST_DB_PATH = "/root/selix/test_selix.db"
PROD_DB_PATH = "/root/selix/selix.db"
NUM_VALID = 20
NUM_INVALID = 10

def create_test_db():
    conn = sqlite3.connect(TEST_DB_PATH)
    if os.path.exists(PROD_DB_PATH):
        prod_conn = sqlite3.connect(PROD_DB_PATH)
        prod_conn.backup(conn)
        prod_conn.close()
    else:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS commodities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT,
                preco_usd REAL,
                unidade TEXT,
                fonte TEXT,
                criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    conn.commit()
    conn.close()

def generate_valid_brent():
    price = round(random.uniform(50, 150), 2)
    ts = datetime.datetime.now() - datetime.timedelta(hours=random.randint(0, 72))
    return ('Brent', price, 'USD/bbl', 'valid_source', ts.isoformat())

def generate_inconsistent_brent():
    error_type = random.choice([
        'negative_price', 'zero_price', 'null_price', 'outlier_high', 'outlier_low',
        'future_timestamp', 'old_timestamp', 'unknown_source'
    ])
    if error_type == 'negative_price':
        price = -random.uniform(1, 100)
    elif error_type == 'zero_price':
        price = 0.0
    elif error_type == 'null_price':
        price = None
    elif error_type == 'outlier_high':
        price = random.uniform(300, 1000)
    elif error_type == 'outlier_low':
        price = random.uniform(-100, 0)
    else:
        price = random.uniform(50, 150)

    if error_type == 'future_timestamp':
        ts = datetime.datetime.now() + datetime.timedelta(days=random.randint(1, 30))
    elif error_type == 'old_timestamp':
        ts = datetime.datetime.now() - datetime.timedelta(days=random.randint(365, 730))
    else:
        ts = datetime.datetime.now() - datetime.timedelta(hours=random.randint(0, 72))

    fonte = 'unknown_source' if error_type == 'unknown_source' else 'inconsistent_source'
    return ('Brent', price, 'USD/bbl', fonte, ts.isoformat())

def insert_data(conn, data):
    cur = conn.cursor()
    for row in data:
        try:
            cur.execute("INSERT INTO commodities (nome, preco_usd, unidade, fonte, criado_em) VALUES (?,?,?,?,?)", row)
        except Exception as e:
            print(f"⚠️ Erro ao inserir: {row[:2]} -> {e}")

def main():
    print("🧪 Gerando dataset de teste...")
    create_test_db()
    conn = sqlite3.connect(TEST_DB_PATH)
    conn.execute("DELETE FROM commodities")
    conn.commit()

    valid_data = [generate_valid_brent() for _ in range(NUM_VALID)]
    invalid_data = [generate_inconsistent_brent() for _ in range(NUM_INVALID)]

    insert_data(conn, valid_data)
    insert_data(conn, invalid_data)

    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM commodities WHERE preco_usd < 0 OR preco_usd > 300 OR preco_usd IS NULL")
    invalid_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM commodities")
    total = cur.fetchone()[0]
    print(f"📊 Total registros: {total}")
    print(f"⚠️ Registros com preço inválido: {invalid_count}")
    conn.close()
    print(f"✅ Dataset criado em {TEST_DB_PATH}")

if __name__ == "__main__":
    main()
