#!/usr/bin/env python3
"""
SELIX — roic.py (módulo separado, NÃO integrado ao core.py macro)

Escopo: comparar ROIC individual por empresa contra a Selic atual, e
cruzar com quem está em Recuperação Judicial (RJ).

⚠️ STATUS DOS DADOS — leia antes de usar em qualquer lugar público:

  EMPRESAS: os valores de ROIC abaixo são PLACEHOLDER, digitados à mão
  a partir de memória/estimativa pública, NÃO vêm de uma API real e
  NÃO foram auditados contra CVM (ITR/DFP) ou B3. Versões anteriores
  (v7.1/v7.2) tinham um comentário "# Simulação com dados conhecidos"
  em cima dessa mesma lista e ainda assim rotulavam a fonte como
  "B3/CVM" no README — isso é uma fonte fabricada, não citar como tal
  em qualquer lugar público até isso ser resolvido.

  RJ (Recuperação Judicial): a lista de empresas e o total "5000" têm
  a mesma origem — placeholder sem link para Serasa/BCB/CVM. Não usar
  o número 5000 em comunicação pública sem fonte.

  PRÓXIMO PASSO REAL: puxar ROIC calculado (EBIT / (Patrimônio+Dívida))
  via demonstrações da CVM (Portal de Dados Abertos CVM tem ITR/DFP em
  CSV, sem paywall) ou Fundamentus (scraping). yfinance é ruim pra B3 —
  campos 'ebit'/'bookValue'/'totalDebt' vêm frequentemente vazios ou
  desatualizados; NÃO usar silenciosamente (ver bug abaixo).

BUGS CORRIGIDOS EM RELAÇÃO ÀS VERSÕES ANTERIORES:

  1. "×100 duplicado": versões anteriores multiplicavam premio_risco
     por 100 depois de já vir em pontos percentuais (bug começou no
     embi_api, "consertos" seguintes só o reintroduziram em outro
     lugar). Este módulo não lida com premio_risco — está isolado do
     macro de propósito — mas o padrão fica documentado aqui como
     alerta para quem for integrar de volta ao core.py.

  2. "except: return 0" mascarando falha de API como ROIC zero: uma
     empresa com falha de rede/API entrava na média com ROIC=0%,
     puxando o setor pra baixo sem ninguém perceber. Corrigido abaixo
     — falha agora levanta exceção explícita ou retorna None, nunca
     0 silencioso.

  3. Filtro "bate a Selic" por MÉDIA DE SETOR em vez de por EMPRESA:
     isso classificava Raízen (RAIZ4, em RJ) como "batendo a Selic"
     só porque a média do setor energia é puxada por Petrobras/Prio3.
     Corrigido: o filtro abaixo é sempre por empresa individual.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Empresa:
    codigo: str
    setor: str
    roic: float  # % — PLACEHOLDER, ver aviso no topo do arquivo
    em_rj: bool


# PLACEHOLDER — não citar como "dados B3/CVM" até ter fonte real.
EMPRESAS: list[Empresa] = [
    Empresa("PETR4", "Energia",     18.5, em_rj=False),
    Empresa("PRIO3", "Energia",     17.2, em_rj=False),
    Empresa("RAIZ4", "Energia",      8.5, em_rj=True),
    Empresa("ABEV3", "Bebidas",     15.0, em_rj=False),
    Empresa("PCAR3", "Varejo",       6.2, em_rj=True),   # GPA / Pão de Açúcar
    Empresa("MGLU3", "Varejo",       5.8, em_rj=False),
    Empresa("VIIA3", "Varejo",       4.5, em_rj=True),
    Empresa("LREN3", "Varejo",       7.1, em_rj=False),
    Empresa("ITUB4", "Financeiro",  12.3, em_rj=False),
    Empresa("BBDC4", "Financeiro",  11.8, em_rj=False),
    Empresa("SANB11","Financeiro",  11.5, em_rj=False),
    Empresa("WEGE3", "Industria",   10.5, em_rj=False),
    Empresa("EMBR3", "Industria",    9.2, em_rj=False),
    Empresa("SUZB3", "Industria",   10.8, em_rj=False),
    Empresa("AMER3", "Varejo",       4.0, em_rj=True),   # Americanas
]

# Placeholder — mesmo aviso: sem fonte confirmada.
TOTAL_EMPRESAS_RJ_BRASIL_ESTIMADO: Optional[int] = None  # era "5000" sem fonte; zerado até confirmar


def get_empresas_que_batem_selic(selic_atual: float, empresas: list[Empresa] = EMPRESAS) -> list[Empresa]:
    """Filtro por EMPRESA individual (não por média de setor)."""
    return [e for e in empresas if e.roic > selic_atual]


def get_empresas_rj(empresas: list[Empresa] = EMPRESAS) -> list[Empresa]:
    return [e for e in empresas if e.em_rj]


def get_empresas_rj_que_batem_selic(selic_atual: float, empresas: list[Empresa] = EMPRESAS) -> list[Empresa]:
    """
    Checagem de sanidade: uma empresa não deveria aparecer nas duas listas
    ao mesmo tempo (RJ E batendo a Selic) — se aparecer, é sinal de dado
    inconsistente, não de "empresa excepcional".
    """
    return [e for e in empresas if e.em_rj and e.roic > selic_atual]


def roic_medio_ponderado_por_empresa(empresas: list[Empresa] = EMPRESAS) -> float:
    """Média simples do ROIC individual (sem inflar setor pequeno via peso arbitrário)."""
    if not empresas:
        raise ValueError("lista de empresas vazia")
    return round(sum(e.roic for e in empresas) / len(empresas), 2)


if __name__ == "__main__":
    SELIC_ATUAL = 14.25

    print("=" * 60)
    print("SELIX — roic.py (dados PLACEHOLDER, não citar como fonte B3/CVM)")
    print("=" * 60)

    batem = get_empresas_que_batem_selic(SELIC_ATUAL)
    print(f"\nEmpresas com ROIC > Selic ({SELIC_ATUAL}%): {len(batem)}")
    for e in batem:
        print(f"  {e.codigo:8s} {e.setor:12s} ROIC={e.roic}%")

    rj = get_empresas_rj()
    print(f"\nEmpresas em RJ (lista placeholder, N={len(rj)}):")
    for e in rj:
        print(f"  {e.codigo:8s} {e.setor:12s} ROIC={e.roic}%")

    inconsistentes = get_empresas_rj_que_batem_selic(SELIC_ATUAL)
    if inconsistentes:
        print(f"\n⚠️  INCONSISTÊNCIA: {len(inconsistentes)} empresa(s) em RJ E batendo a Selic — checar dado.")
    else:
        print("\n✅ Nenhuma empresa em RJ aparece batendo a Selic (esperado).")

    print(f"\nROIC médio (simples, por empresa): {roic_medio_ponderado_por_empresa()}%")
    print(f"Total de empresas em RJ no Brasil: {TOTAL_EMPRESAS_RJ_BRASIL_ESTIMADO} (sem fonte confirmada)")
