"""Sensibilidade da despesa financeira a mudanças no custo da dívida.

Todos os valores monetários estão na mesma unidade informada pelo usuário.
Taxas são percentuais anuais (ex.: 15.0 = 15%).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class DebtExposure:
    gross_debt: float
    floating_debt: float
    current_debt_cost_pct: float
    repricing_share: float = 1.0
    tax_rate_pct: Optional[float] = None

    def validate(self) -> None:
        if self.gross_debt < 0 or self.floating_debt < 0:
            raise ValueError("Dívidas não podem ser negativas.")
        if self.floating_debt > self.gross_debt:
            raise ValueError("Dívida exposta não pode superar dívida bruta.")
        if not 0 <= self.repricing_share <= 1:
            raise ValueError("repricing_share deve estar entre 0 e 1.")
        if self.current_debt_cost_pct < 0:
            raise ValueError("Custo da dívida não pode ser negativo.")
        if self.tax_rate_pct is not None and not 0 <= self.tax_rate_pct <= 100:
            raise ValueError("tax_rate_pct deve estar entre 0 e 100.")


def simulate_rate_change(
    exposure: DebtExposure,
    new_debt_cost_pct: float,
) -> dict:
    """Estima economia anual em regime após repricing.

    Não presume que a Selic seja transmitida integralmente à dívida.
    O chamador informa o novo custo efetivo da dívida.
    """
    exposure.validate()

    if new_debt_cost_pct < 0:
        raise ValueError("Novo custo da dívida não pode ser negativo.")

    repriced_debt = (
        exposure.floating_debt * exposure.repricing_share
    )
    rate_delta = (
        exposure.current_debt_cost_pct - new_debt_cost_pct
    ) / 100.0

    gross_savings = repriced_debt * rate_delta

    tax_shield_adjustment = None
    if exposure.tax_rate_pct is not None:
        tax_shield_adjustment = gross_savings * (
            1 - exposure.tax_rate_pct / 100.0
        )

    return {
        "gross_debt": exposure.gross_debt,
        "floating_debt": exposure.floating_debt,
        "repriced_debt": repriced_debt,
        "current_debt_cost_pct": exposure.current_debt_cost_pct,
        "new_debt_cost_pct": new_debt_cost_pct,
        "rate_change_pp": round(
            new_debt_cost_pct - exposure.current_debt_cost_pct, 4
        ),
        "annual_gross_savings": round(gross_savings, 2),
        "annual_after_tax_savings": (
            None if tax_shield_adjustment is None
            else round(tax_shield_adjustment, 2)
        ),
        "assumption": "steady_state_full_year_after_repricing",
    }


def build_scenarios(
    exposure: DebtExposure,
    new_costs_pct: list[float],
) -> list[dict]:
    """Executa cenários sem alterar os dados originais."""
    return [
        simulate_rate_change(exposure, rate)
        for rate in new_costs_pct
    ]
