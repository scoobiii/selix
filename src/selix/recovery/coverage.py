"""Cobertura de juros e dívida líquida.

A despesa de juros é informada pelo chamador, no MESMO período do EBIT.
Não usar a conta 3.06.02 da CVM: ela inclui variação cambial.
"""

from typing import Optional


def interest_coverage(ebit: float, interest_expense: float) -> Optional[float]:
    """EBIT / despesa de juros (valor positivo). None se não houver despesa."""
    if interest_expense < 0:
        raise ValueError("Informe a despesa de juros como valor positivo.")
    if interest_expense == 0:
        return None
    return ebit / interest_expense


def net_debt(gross_debt: Optional[float], cash_total: Optional[float]) -> Optional[float]:
    """Dívida bruta menos caixa e aplicações. None se algum dado faltar."""
    if gross_debt is None or cash_total is None:
        return None
    if gross_debt < 0 or cash_total < 0:
        raise ValueError("Dívida e caixa não podem ser negativos.")
    return gross_debt - cash_total


def coverage_after_savings(
    ebit: float, interest_expense: float, annual_gross_savings: float
) -> Optional[float]:
    """Cobertura após a economia do repricing (mesmo período do EBIT)."""
    return interest_coverage(ebit, max(0.0, interest_expense - annual_gross_savings))
