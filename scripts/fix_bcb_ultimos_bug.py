#!/usr/bin/env python3
"""
Corrige server_v5.py, server_v6.py e selix_energy_forecast.py para reusar
BCBProvider (já correto, usa dataInicial/dataFinal + rows[-1]) em vez de
duplicar chamadas com /ultimos/N (bug: pode retornar datas futuras).

Uso: python3 scripts/fix_bcb_ultimos_bug.py
"""

def patch_server_v5():
    path = "src/api/server_v5.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    old_inflacao = '''def get_inflacao_real():
    """Consulta IPCA-12 via API BCB SGS (série 13522)"""
    global INFLACAO
    try:
        import requests
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados/ultimos/1?formato=json"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            dados = resp.json()
            if dados and len(dados) > 0:
                INFLACAO = float(dados[0]["valor"])
                print(f"[Dados] IPCA atualizado: {INFLACAO}%")
                return INFLACAO
    except Exception as e:
        print(f"[Erro] Falha ao consultar BCB: {e}")
    return INFLACAO'''

    new_inflacao = '''def get_inflacao_real():
    """Consulta IPCA-12 via API BCB SGS (série 13522)"""
    global INFLACAO
    try:
        from src.providers.bcb_provider import BCBProvider
        r = BCBProvider()._fetch_sgs(13522)
        if r.get("success"):
            INFLACAO = r["rate"]
            print(f"[Dados] IPCA atualizado: {INFLACAO}%")
            return INFLACAO
    except Exception as e:
        print(f"[Erro] Falha ao consultar BCB: {e}")
    return INFLACAO'''

    old_selic = '''        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1178/dados/ultimos/1?formato=json"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            dados = resp.json()
            if dados and len(dados) > 0:
                SELIC_BCB = float(dados[0]["valor"])
                print(f"[Dados] Selic atualizada: {SELIC_BCB}%")
                return SELIC_BCB'''

    new_selic = '''        from src.providers.bcb_provider import BCBProvider
        r = BCBProvider()._fetch_sgs(1178)
        if r.get("success"):
            SELIC_BCB = r["rate"]
            print(f"[Dados] Selic atualizada: {SELIC_BCB}%")
            return SELIC_BCB'''

    if old_inflacao not in content:
        print(f"❌ Bloco get_inflacao_real não encontrado exatamente em {path} — revise manualmente.")
    else:
        content = content.replace(old_inflacao, new_inflacao)
        print(f"✅ get_inflacao_real corrigido em {path}")

    if old_selic not in content:
        print(f"❌ Bloco get_selic_real (URL) não encontrado exatamente em {path} — revise manualmente.")
    else:
        content = content.replace(old_selic, new_selic)
        print(f"✅ get_selic_real corrigido em {path}")

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def patch_server_v6():
    path = "src/api/server_v6.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    old = '''    try:
        import requests
        resp = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.13522/dados/ultimos/1?formato=json", timeout=10)
        if resp.status_code == 200: INFLACAO = float(resp.json()[0]["valor"])
        resp = requests.get("https://api.bcb.gov.br/dados/serie/bcdata.sgs.1178/dados/ultimos/1?formato=json", timeout=10)
        if resp.status_code == 200: SELIC_BCB = float(resp.json()[0]["valor"])
    except: pass'''

    new = '''    try:
        from src.providers.bcb_provider import BCBProvider
        provider = BCBProvider()
        r_infl = provider._fetch_sgs(13522)
        if r_infl.get("success"): INFLACAO = r_infl["rate"]
        r_selic = provider._fetch_sgs(1178)
        if r_selic.get("success"): SELIC_BCB = r_selic["rate"]
    except: pass'''

    if old not in content:
        print(f"❌ Bloco atualizar_dados não encontrado exatamente em {path} — revise manualmente.")
    else:
        content = content.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ atualizar_dados corrigido em {path}")


def patch_energy_forecast():
    path = "src/energy/selix_energy_forecast.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    old = '''    try:
        # API do BCB para preços de commodities (opcional)
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1376/dados/ultimos/12?formato=json"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            dados = resp.json()
            df_api = pd.DataFrame(dados)
            df_api["ds"] = pd.to_datetime(df_api["data"])
            df_api["y"] = pd.to_numeric(df_api["valor"])
            return df_api[["ds", "y"]]
    except:
        pass
    return None'''

    new = '''    try:
        # API do BCB para preços de commodities — intervalo explícito
        # (contorna bug do /ultimos/N que pode retornar datas futuras)
        from datetime import date, timedelta
        fim = date.today()
        ini = fim - timedelta(days=30)
        url = "https://api.bcb.gov.br/dados/serie/bcdata.sgs.1376/dados"
        params = {
            "formato": "json",
            "dataInicial": ini.strftime("%d/%m/%Y"),
            "dataFinal": fim.strftime("%d/%m/%Y"),
        }
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            dados = resp.json()
            df_api = pd.DataFrame(dados)
            df_api["ds"] = pd.to_datetime(df_api["data"])
            df_api["y"] = pd.to_numeric(df_api["valor"])
            return df_api[["ds", "y"]]
    except:
        pass
    return None'''

    if old not in content:
        print(f"❌ Bloco carregar_dados_api não encontrado exatamente em {path} — revise manualmente.")
    else:
        content = content.replace(old, new)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"✅ carregar_dados_api corrigido em {path}")


if __name__ == "__main__":
    patch_server_v5()
    patch_server_v6()
    patch_energy_forecast()
    print()
    print("Revise com: git diff src/api/server_v5.py src/api/server_v6.py src/energy/selix_energy_forecast.py")
