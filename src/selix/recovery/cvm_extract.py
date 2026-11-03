"""Extração de contas fixas do ITR da CVM (demonstrações consolidadas).

Formato verificado em itr_cia_aberta_{DRE,BPA,BPP}_con_2026.csv:
separador ';', encoding latin-1, ORDEM_EXERC = ÚLTIMO, VERSAO 1..3.
Valores em reais (ESCALA_MOEDA aplicada). Conta ausente = None, nunca 0.
Empresa identificada por CD_CVM (o ticker não está nesses arquivos).
"""

import csv
from pathlib import Path

ENCODING = "latin-1"
ESCALAS = {"UNIDADE": 1, "MIL": 1000}
ULTIMO = "ÚLTIMO"

INCOME_CODES = {
    "revenue": "3.01",
    "ebit": "3.05",
    "financial_result": "3.06",
    "financial_income": "3.06.01",
    "financial_expense": "3.06.02",
    "pretax_income": "3.07",
    "income_tax": "3.08",
    "net_income": "3.09",
}
ASSET_CODES = {"cash": "1.01.01", "short_term_investments": "1.01.02"}
LIABILITY_CODES = {
    "debt_current": "2.01.04",
    "debt_noncurrent": "2.02.01",
    "equity": "2.03",
    "lease_current": "2.01.04.03",
    "lease_noncurrent": "2.02.01.03",
}


def _read(path) -> list[dict]:
    with open(path, encoding=ENCODING, newline="") as f:
        return list(csv.DictReader(f, delimiter=";"))


def _select(rows, cd_cvm, dt_refer) -> list[dict]:
    cd = str(cd_cvm).zfill(6)
    sel = [
        r for r in rows
        if r["CD_CVM"] == cd
        and r["DT_REFER"] == dt_refer
        and r["ORDEM_EXERC"] == ULTIMO
    ]
    if not sel:
        return []
    versao = max(int(r["VERSAO"]) for r in sel)
    return [r for r in sel if int(r["VERSAO"]) == versao]


def _value(row) -> float:
    escala = row["ESCALA_MOEDA"]
    if escala not in ESCALAS:
        raise ValueError(f"ESCALA_MOEDA desconhecida: {escala!r}")
    return float(row["VL_CONTA"]) * ESCALAS[escala]


def income(rows, cd_cvm, dt_refer) -> dict:
    """DRE: usa o período acumulado (menor DT_INI_EXERC) do DT_REFER."""
    sel = _select(rows, cd_cvm, dt_refer)
    if not sel:
        return {"period": None, "interest_expense": None,
                **{k: None for k in INCOME_CODES}}
    ini = min(r["DT_INI_EXERC"] for r in sel)
    sel = [r for r in sel if r["DT_INI_EXERC"] == ini]
    by = {r["CD_CONTA"]: _value(r) for r in sel}
    out = {k: by.get(c) for k, c in INCOME_CODES.items()}
    out["period"] = (ini, sel[0]["DT_FIM_EXERC"])
    fin = [
        r for r in sel
        if r["CD_CONTA"] == "3.06.02.01"
        and r["DS_CONTA"].strip().lower() == "despesas financeiras"
    ]
    out["interest_expense"] = abs(_value(fin[0])) if fin else None
    return out


def balance(rows, cd_cvm, dt_refer, codes) -> dict:
    sel = [
        r for r in _select(rows, cd_cvm, dt_refer)
        if r["DT_FIM_EXERC"] == dt_refer
    ]
    by = {r["CD_CONTA"]: _value(r) for r in sel}
    return {k: by.get(c) for k, c in codes.items()}


def extract_company(data_dir, cd_cvm, dt_refer: str) -> dict:
    """dt_refer no formato AAAA-MM-DD (ex.: '2026-03-31')."""
    year = dt_refer[:4]
    d = Path(data_dir)

    def path(kind):
        return d / f"itr_cia_aberta_{kind}_con_{year}.csv"

    out = {"cd_cvm": str(cd_cvm).zfill(6), "dt_refer": dt_refer}
    out.update(income(_read(path("DRE")), cd_cvm, dt_refer))
    out.update(balance(_read(path("BPA")), cd_cvm, dt_refer, ASSET_CODES))
    out.update(balance(_read(path("BPP")), cd_cvm, dt_refer, LIABILITY_CODES))

    debts = [out["debt_current"], out["debt_noncurrent"]]
    out["gross_debt"] = None if None in debts else sum(debts)
    leases = [out["lease_current"], out["lease_noncurrent"]]
    out["lease_debt"] = None if None in leases else sum(leases)
    out["financial_debt"] = (
        None if out["gross_debt"] is None or out["lease_debt"] is None
        else out["gross_debt"] - out["lease_debt"]
    )
    cash = [out["cash"], out["short_term_investments"]]
    out["cash_total"] = None if None in cash else sum(cash)

    warnings = []
    fe = out["financial_expense"]
    if fe is not None and fe > 0:
        warnings.append(
            "3.06.02 positiva: inclui variação cambial; "
            "não usar como despesa de juros."
        )
    out["warnings"] = warnings
    return out
