"""ROIC a partir de contas observadas do ITR (extract_company).

ROIC do período, sem anualizar. Capital investido = dívida bruta + PL - caixa
e aplicações, no fim do período (não é média). A anualização linear é uma
aproximação e vem em campo separado.
"""

from datetime import date
from typing import Optional


def effective_tax_rate(pretax_income, income_tax) -> Optional[float]:
    """income_tax como na DRE (negativo = despesa). None se LAIR <= 0 ou fora de 0..1."""
    if pretax_income is None or income_tax is None or pretax_income <= 0:
        return None
    rate = -income_tax / pretax_income
    return rate if 0 <= rate <= 1 else None


def nopat(ebit, tax_rate) -> Optional[float]:
    if ebit is None or tax_rate is None:
        return None
    return ebit * (1 - tax_rate)


def invested_capital(gross_debt, equity, cash_total) -> Optional[float]:
    if gross_debt is None or equity is None or cash_total is None:
        return None
    return gross_debt + equity - cash_total


def roic_period(nopat_value, capital) -> Optional[float]:
    if nopat_value is None or capital is None or capital <= 0:
        return None
    return nopat_value / capital


def months_in_period(period) -> Optional[int]:
    if period is None:
        return None
    ini, fim = (date.fromisoformat(x) for x in period)
    return (fim.year - ini.year) * 12 + fim.month - ini.month + 1


def annualize_linear(value: float, months: int) -> float:
    if months <= 0:
        raise ValueError("months deve ser positivo.")
    return value * 12 / months


def assess_roic(company: dict) -> dict:
    rate = effective_tax_rate(company.get("pretax_income"), company.get("income_tax"))
    n = nopat(company.get("ebit"), rate)
    cap = invested_capital(
        company.get("gross_debt"), company.get("equity"), company.get("cash_total")
    )
    cap_open = invested_capital(
        company.get("opening_gross_debt"), company.get("opening_equity"),
        company.get("opening_cash_total"),
    )
    cap_avg = None if cap is None or cap_open is None else (cap + cap_open) / 2
    r = roic_period(n, cap_avg if cap_avg is not None else cap)
    months = months_in_period(company.get("period"))
    return {
        "basis": "observado_itr_v1_bruto",
        "tax_rate": rate,
        "nopat": n,
        "invested_capital": cap,
        "invested_capital_open": cap_open,
        "invested_capital_avg": cap_avg,
        "capital_basis": "medio" if cap_avg is not None else "fechamento",
        "months": months,
        "roic_period": r,
        "roic_annualized_linear": (
            None if r is None or months is None else annualize_linear(r, months)
        ),
    }


def equity_unexplained(opening_equity, equity, net_income) -> Optional[float]:
    """PL final - PL inicial - lucro. Inclui dividendos, aportes e OCI."""
    if opening_equity is None or equity is None or net_income is None:
        return None
    return equity - opening_equity - net_income


def equity_flag(opening_equity, equity, net_income, threshold=0.25) -> Optional[bool]:
    """True se o resto passa de threshold x PL inicial (perimetro/aporte?)."""
    u = equity_unexplained(opening_equity, equity, net_income)
    if u is None or not opening_equity:
        return None
    return abs(u) / abs(opening_equity) > threshold
