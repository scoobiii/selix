import pytest

from src.selix.recovery.cvm_extract import extract_company

HEAD_DRE = (
    "CNPJ_CIA;DT_REFER;VERSAO;DENOM_CIA;CD_CVM;GRUPO_DFP;MOEDA;ESCALA_MOEDA;"
    "ORDEM_EXERC;DT_INI_EXERC;DT_FIM_EXERC;CD_CONTA;DS_CONTA;VL_CONTA;"
    "ST_CONTA_FIXA"
)
HEAD_BP = (
    "CNPJ_CIA;DT_REFER;VERSAO;DENOM_CIA;CD_CVM;GRUPO_DFP;MOEDA;ESCALA_MOEDA;"
    "ORDEM_EXERC;DT_FIM_EXERC;CD_CONTA;DS_CONTA;VL_CONTA;ST_CONTA_FIXA"
)
ULT, PEN = "ÚLTIMO", "PENÚLTIMO"


def dre(refer, ordem, ini, fim, conta, valor, versao=1, escala="MIL"):
    return (
        f"00.000.000/0001-00;{refer};{versao};EMPRESA TESTE;009512;"
        f"DF Consolidado - Demonstração do Resultado;REAL;{escala};{ordem};"
        f"{ini};{fim};{conta};conta;{valor}.0000000000;S"
    )


def bp(refer, ordem, fim, conta, valor, versao=1, escala="MIL"):
    return (
        f"00.000.000/0001-00;{refer};{versao};EMPRESA TESTE;009512;"
        f"DF Consolidado - Balanço;REAL;{escala};{ordem};"
        f"{fim};{conta};conta;{valor}.0000000000;S"
    )


def make_dir(tmp_path, dre_lines, bpa=(), bpp=()):
    for kind, head, lines in (
        ("DRE", HEAD_DRE, dre_lines),
        ("BPA", HEAD_BP, bpa),
        ("BPP", HEAD_BP, bpp),
    ):
        (tmp_path / f"itr_cia_aberta_{kind}_con_2026.csv").write_text(
            "\n".join([head, *lines]) + "\n", encoding="latin-1"
        )
    return tmp_path


@pytest.fixture
def data_dir(tmp_path):
    q1 = "2026-03-31"
    q2 = "2026-06-30"
    q3 = "2026-09-30"
    dre_lines = [
        dre(q1, ULT, "2026-01-01", q1, "3.01", 123686000),
        dre(q1, ULT, "2026-01-01", q1, "3.05", 41270000),
        dre(q1, ULT, "2026-01-01", q1, "3.06", 7866000),
        dre(q1, ULT, "2026-01-01", q1, "3.06.01", 1758000),
        dre(q1, ULT, "2026-01-01", q1, "3.06.02", 6108000),
        dre(q1, PEN, "2025-01-01", "2025-03-31", "3.01", 99999),
        dre(q2, ULT, "2026-04-01", q2, "3.01", 169530000),
        dre(q2, ULT, "2026-01-01", q2, "3.01", 293216000),
        dre(q3, ULT, "2026-01-01", q3, "3.01", 100, versao=1),
        dre(q3, ULT, "2026-01-01", q3, "3.01", 200, versao=2),
    ]
    bpa = [
        bp(q1, ULT, q1, "1.01.01", 34294000),
        bp(q1, ULT, q1, "1.01.02", 13306000),
    ]
    bpp = [
        bp(q1, ULT, q1, "2.01.04", 66447000),
        bp(q1, ULT, q1, "2.02.01", 305244000),
    ]
    return make_dir(tmp_path, dre_lines, bpa, bpp)


def test_q1_income_and_scale(data_dir):
    r = extract_company(data_dir, "009512", "2026-03-31")
    assert r["revenue"] == 123_686_000_000.0
    assert r["ebit"] == 41_270_000_000.0
    assert r["period"] == ("2026-01-01", "2026-03-31")


def test_ignores_penultimo(data_dir):
    r = extract_company(data_dir, "009512", "2026-03-31")
    assert r["revenue"] != 99_999_000.0


def test_prefers_ytd_over_quarter(data_dir):
    r = extract_company(data_dir, "009512", "2026-06-30")
    assert r["revenue"] == 293_216_000_000.0
    assert r["period"][0] == "2026-01-01"


def test_takes_latest_versao(data_dir):
    r = extract_company(data_dir, "009512", "2026-09-30")
    assert r["revenue"] == 200_000.0


def test_debt_and_cash(data_dir):
    r = extract_company(data_dir, "009512", "2026-03-31")
    assert r["gross_debt"] == (66_447_000 + 305_244_000) * 1000
    assert r["cash_total"] == (34_294_000 + 13_306_000) * 1000


def test_missing_account_is_none(data_dir):
    r = extract_company(data_dir, "009512", "2026-06-30")
    assert r["ebit"] is None
    assert r["gross_debt"] is None


def test_positive_financial_expense_warns(data_dir):
    r = extract_company(data_dir, "009512", "2026-03-31")
    assert len(r["warnings"]) == 1
    assert "variação cambial" in r["warnings"][0]


def test_cd_cvm_without_padding(data_dir):
    r = extract_company(data_dir, "9512", "2026-03-31")
    assert r["revenue"] == 123_686_000_000.0


def test_unknown_scale_raises(tmp_path):
    d = make_dir(
        tmp_path,
        [dre("2026-03-31", ULT, "2026-01-01", "2026-03-31", "3.01", 1,
             escala="MILHAO")],
    )
    with pytest.raises(ValueError):
        extract_company(d, "009512", "2026-03-31")
