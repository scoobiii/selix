#!/usr/bin/env python3
"""
SELIX — ROIC real via CVM (Portal de Dados Abertos)

Fonte: CVM — https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS/

ROIC = EBIT / (Patrimônio Líquido + Dívida Bruta)
EBIT = Lucro Antes dos Juros e Impostos (resultado operacional)
"""

import requests
import pandas as pd
from typing import Optional, Dict
from io import StringIO
import os

CVM_BASE_URL = "https://dados.cvm.gov.br/dados/CIA_ABERTA/DOC/ITR/DADOS"

def _baixar_itr(ano: int = 2025) -> Optional[pd.DataFrame]:
    """Baixa o arquivo ITR da CVM para o ano especificado."""
    try:
        url = f"{CVM_BASE_URL}/itr_cia_aberta_{ano}.csv"
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            # Decodificar com encoding correto (latin1)
            df = pd.read_csv(StringIO(response.text), sep=';', encoding='latin1')
            return df
        else:
            return None
    except Exception as e:
        print(f"Erro ao baixar ITR da CVM: {e}")
        return None

def get_roic_por_codigo(codigo: str, ano: int = 2025) -> Optional[float]:
    """
    Busca ROIC de uma empresa específica na CVM.

    Args:
        codigo: código da empresa (ex: PETR4)
        ano: ano do ITR (ex: 2025)

    Returns:
        ROIC em porcentagem (ex: 18.5) ou None se não encontrado
    """
    df = _baixar_itr(ano)
    if df is None:
        return None

    # Filtrar a empresa pelo código
    empresa = df[df['CD_CVM'].astype(str).str.contains(codigo, na=False)]

    if empresa.empty:
        return None

    # Calcular ROIC
    # EBIT = Lucro Operacional
    ebit = empresa['VL_LUCRO_OPERACIONAL'].sum()
    # Patrimônio Líquido
    patrimonio = empresa['VL_PATRIMONIO_LIQUIDO'].sum()
    # Dívida Bruta
    divida = empresa['VL_DIVIDA_BRUTA'].sum()

    if (patrimonio + divida) == 0:
        return None

    roic = (ebit / (patrimonio + divida)) * 100
    return round(roic, 2)

def get_fonte_roic() -> str:
    return "CVM — Portal de Dados Abertos (ITR/DFP)"

if __name__ == "__main__":
    # Teste
    roic = get_roic_por_codigo("PETR4")
    print(f"ROIC PETR4: {roic}%")
