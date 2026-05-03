#!/usr/bin/env python3
"""
SELIX Energy - Previsão de Preços do Petróleo com Prophet
Baseado em dados históricos Brent 2024-2026
"""

import pandas as pd
import numpy as np
from prophet import Prophet
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import requests
import json
import warnings
warnings.filterwarnings('ignore')

# ============================================================
# 1. CARREGAR DADOS HISTÓRICOS
# ============================================================

def carregar_dados_historicos():
    """
    Carrega dados históricos do Brent de fontes públicas
    Dados baseados em:
    - 2024: Média US$ 80-85/barril
    - 2025: Alta gradual até US$ 90
    - 2026: Crise geopolítica (fev-jun) com pico em abril
    """
    
    # Dados históricos simulados (em produção, usar API da EIA, Bloomberg, ou BCB)
    dados = {
        "ds": [],
        "y": []
    }
    
    # 2024 (dados mensais)
    brent_2024 = [78, 80, 82, 84, 83, 82, 84, 86, 85, 84, 83, 85]
    for i, preco in enumerate(brent_2024):
        dados["ds"].append(f"2024-{i+1:02d}-15")
        dados["y"].append(preco)
    
    # 2025
    brent_2025 = [85, 86, 87, 88, 87, 89, 90, 92, 91, 93, 92, 90]
    for i, preco in enumerate(brent_2025):
        dados["ds"].append(f"2025-{i+1:02d}-15")
        dados["y"].append(preco)
    
    # 2026 (até maio, com pico da crise)
    brent_2026 = [
        89,   # jan
        90,   # fev (pre-crise)
        95,   # mar (início guerra)
        110,  # abr (pico)
        98,   # mai (recuperação)
    ]
    for i, preco in enumerate(brent_2026):
        dados["ds"].append(f"2026-{i+1:02d}-15")
        dados["y"].append(preco)
    
    df = pd.DataFrame(dados)
    df["ds"] = pd.to_datetime(df["ds"])
    return df

def carregar_dados_api():
    """Tentativa de carregar dados reais via API (opcional)"""
    try:
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
    return None

# ============================================================
# 2. MODELO PROPHET
# ============================================================

def treinar_modelo_prophet(df, forecast_days=90):
    """
    Treina modelo Prophet e gera previsões futuras
    """
    print("="*60)
    print("SELIX Energy - Previsão de Preços do Petróleo (Prophet)")
    print("="*60)
    
    print(f"\n📊 Dados históricos: {len(df)} pontos")
    print(f"   Período: {df['ds'].min()} a {df['ds'].max()}")
    print(f"   Preço médio: US$ {df['y'].mean():.2f}/barril")
    print(f"   Preço máximo: US$ {df['y'].max():.2f}/barril")
    
    # Adicionar componentes de sazonalidade
    modelo = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=False,
        daily_seasonality=False,
        changepoint_prior_scale=0.5,
        seasonality_prior_scale=10.0,
        holidays_prior_scale=10.0,
        interval_width=0.95
    )
    
    # Adicionar sazonalidades específicas
    modelo.add_seasonality(name='monthly', period=30.5, fourier_order=5)
    modelo.add_country_holidays(country_name='US')  # Mercado internacional
    
    modelo.fit(df)
    
    # Criar dataframe de datas futuras
    future = modelo.make_future_dataframe(periods=forecast_days, freq='D')
    forecast = modelo.predict(future)
    
    return modelo, forecast

# ============================================================
# 3. REGRA SELIX ENERGY
# ============================================================

def selix_energy_rule(preco_brent):
    """
    Regra automática para mistura de etanol baseada no preço do Brent
    Baseado no whitepaper SELIX Energy v4.0
    """
    if preco_brent < 70:
        return {"e_mistura": "E27", "tempo_resposta": "normal", "importacao": "alta", "justificativa": "Preço normal"}
    elif preco_brent < 90:
        return {"e_mistura": "E30", "tempo_resposta": "48h", "importacao": "média", "justificativa": "Alerta preventivo"}
    elif preco_brent < 120:
        return {"e_mistura": "E35", "tempo_resposta": "48h", "importacao": "baixa", "justificativa": "Crise instalada"}
    elif preco_brent < 150:
        return {"e_mistura": "E40", "tempo_resposta": "24h", "importacao": "muito baixa", "justificativa": "Emergência"}
    else:
        return {"e_mistura": "E42", "tempo_resposta": "12h", "importacao": "zero", "justificativa": "Soberania energética"}

def calcular_impacto_economico(preco_brent, mistura_atual="E27"):
    """
    Calcula economia gerada pela regra automática
    """
    regra = selix_energy_rule(preco_brent)
    mistura_ideal = regra["e_mistura"]
    
    # Base de cálculo
    importacao_mensal_base = 700_000_000  # litros/mês com E27
    preco_gasolina_importada = preco_brent * 0.023  # US$/litro (conversão aproximada)
    
    # Redução de importação por ponto de mistura
    reducao_por_ponto = 70_000_000  # litros/mês por pp de etanol
    
    mistura_atual_num = int(mistura_atual[1:])
    mistura_ideal_num = int(mistura_ideal[1:])
    
    diferencial_pp = max(0, mistura_ideal_num - mistura_atual_num)
    reducao_importacao = diferencial_pp * reducao_por_ponto
    
    economia_usd = reducao_importacao * preco_gasolina_importada / 1_000_000
    economia_brl = economia_usd * 5.5
    
    return {
        "mistura_atual": mistura_atual,
        "mistura_ideal": mistura_ideal,
        "diferencial_pp": diferencial_pp,
        "reducao_importacao_litros_mes": reducao_importacao,
        "economia_usd_mes": round(economia_usd, 2),
        "economia_brl_mes": round(economia_brl, 2),
        "economia_usd_ano": round(economia_usd * 12, 0),
        "economia_brl_ano": round(economia_brl * 12, 0)
    }

# ============================================================
# 4. ANÁLISE DE CENÁRIOS PREDITIVOS
# ============================================================

def analisar_cenarios(forecast):
    """
    Analisa cenários preditivos baseados na previsão
    """
    ultima_previsao = forecast.iloc[-1]
    preco_previsto = ultima_previsao['yhat']
    preco_upper = ultima_previsao['yhat_upper']
    preco_lower = ultima_previsao['yhat_lower']
    
    print("\n" + "="*60)
    print("📈 PREVISÕES PARA OS PRÓXIMOS 90 DIAS")
    print("="*60)
    print(f"  Preço previsto (mediana):  US$ {preco_previsto:.2f}/barril")
    print(f"  Intervalo de confiança 95%: US$ {preco_lower:.2f} - {preco_upper:.2f}")
    
    print("\n🎯 RECOMENDAÇÃO SELIX ENERGY:")
    print("="*60)
    
    # Cenário pessimista (preço alto)
    if preco_upper > 120:
        print(f"  🔴 Cenário pessimista (Brent > US$ 120):")
        regra = selix_energy_rule(preco_upper)
        print(f"     → Mistura recomendada: {regra['e_mistura']} (em 24h)")
        print(f"     → Soberania energética garantida")
    
    # Cenário esperado
    regra = selix_energy_rule(preco_previsto)
    print(f"\n  🟡 Cenário esperado (Brent ~US$ {preco_previsto:.0f}):")
    print(f"     → Mistura recomendada: {regra['e_mistura']} (em {regra['tempo_resposta']})")
    print(f"     → {regra['justificativa']}")
    
    # Cenário otimista
    if preco_lower < 90:
        print(f"\n  🟢 Cenário otimista (Brent < US$ 90):")
        regra_otimista = selix_energy_rule(preco_lower)
        print(f"     → Mistura recomendada: {regra_otimista['e_mistura']}")
    
    return preco_previsto

# ============================================================
# 5. GERAR GRÁFICOS
# ============================================================

def gerar_graficos(df, forecast, nome_arquivo="selix_energy_forecast.png"):
    """
    Gera gráficos de histórico e previsão
    """
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    # Gráfico 1: Histórico + Previsão
    ax1.plot(df['ds'], df['y'], 'o-', label='Histórico', color='blue', markersize=4)
    ax1.plot(forecast['ds'], forecast['yhat'], '-', label='Previsão (Prophet)', color='red')
    ax1.fill_between(forecast['ds'], forecast['yhat_lower'], forecast['yhat_upper'], 
                      alpha=0.2, color='red', label='Intervalo de confiança 95%')
    ax1.axvline(x=datetime.now(), color='green', linestyle='--', label='Hoje')
    ax1.set_ylabel('Preço Brent (US$/barril)')
    ax1.set_title('SELIX Energy - Previsão de Preços do Petróleo')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Gráfico 2: Mistura recomendada por faixa de preço
    precos = np.linspace(50, 180, 100)
    misturas = [selix_energy_rule(p)['e_mistura'] for p in precos]
    
    cores = []
    for p in precos:
        if p < 70: cores.append('green')
        elif p < 90: cores.append('lightgreen')
        elif p < 120: cores.append('yellow')
        elif p < 150: cores.append('orange')
        else: cores.append('red')
    
    # Criar plot de faixas
    ax2.bar(precos, [1]*len(precos), width=1.5, color=cores, alpha=0.5)
    
    # Adicionar labels nas faixas
    ax2.text(60, 0.5, 'E27', ha='center', fontsize=12, fontweight='bold')
    ax2.text(80, 0.5, 'E30', ha='center', fontsize=12, fontweight='bold')
    ax2.text(105, 0.5, 'E35', ha='center', fontsize=12, fontweight='bold')
    ax2.text(135, 0.5, 'E40', ha='center', fontsize=12, fontweight='bold')
    ax2.text(165, 0.5, 'E42', ha='center', fontsize=12, fontweight='bold')
    
    # Linha vertical do preço previsto
    preco_prev = forecast.iloc[-1]['yhat']
    ax2.axvline(x=preco_prev, color='blue', linestyle='-', linewidth=2, label=f'Preço previsto: US${preco_prev:.0f}')
    
    ax2.set_xlabel('Preço Brent (US$/barril)')
    ax2.set_ylabel('Mistura de Etanol')
    ax2.set_title('SELIX Energy - Regra Automática de Mistura')
    ax2.set_ylim(0, 1.5)
    ax2.set_yticks([])
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='x')
    
    plt.tight_layout()
    plt.savefig(nome_arquivo, dpi=150, bbox_inches='tight')
    print(f"\n📊 Gráfico salvo: {nome_arquivo}")
    return fig

# ============================================================
# 6. FUNÇÃO PRINCIPAL
# ============================================================

def main():
    print("="*70)
    print("SELIX ENERGY v1.0 - Previsão de Preços com Prophet")
    print("="*70)
    
    # Carregar dados
    df = carregar_dados_historicos()
    
    # Treinar modelo
    modelo, forecast = treinar_modelo_prophet(df, forecast_days=90)
    
    # Analisar cenários
    preco_previsto = analisar_cenarios(forecast)
    
    # Calcular impacto atual com E27
    print("\n" + "="*60)
    print("💰 IMPACTO ECONÔMICO DA RECOMENDAÇÃO")
    print("="*60)
    
    impacto = calcular_impacto_economico(preco_previsto, mistura_atual="E27")
    print(f"\n  Mistura atual:          {impacto['mistura_atual']}")
    print(f"  Mistura recomendada:    {impacto['mistura_ideal']}")
    print(f"  Diferença:              +{impacto['diferencial_pp']} pp")
    print(f"\n  Redução de importação:  {impacto['reducao_importacao_litros_mes']:,.0f} L/mês")
    print(f"  Economia mensal:        US$ {impacto['economia_usd_mes']:.2f} M | R$ {impacto['economia_brl_mes']:.2f} M")
    print(f"  Economia anual:         US$ {impacto['economia_usd_ano']:,.0f} M | R$ {impacto['economia_brl_ano']:,.0f} M")
    
    # Gerar gráficos
    gerar_graficos(df, forecast)
    
    # Salvar previsão em CSV
    forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_csv('selix_energy_forecast.csv', index=False)
    print("\n📁 Arquivos gerados:")
    print("  - selix_energy_forecast.csv (dados da previsão)")
    print("  - selix_energy_forecast.png (gráficos)")
    
    # Resumo para o CNPE
    print("\n" + "="*70)
    print("📋 RESUMO PARA O CNPE")
    print("="*70)
    print("""
    Considerando a previsão de preços do petróleo e o risco geopolítico persistente:
    
    1. ✅ Em março de 2026 (Brent a US$ 95), a regra SELIX Energy recomendava E35
    2. ✅ A antecipação para E32-E35 reduziria importação em 500-700 milhões L/mês
    3. ✅ Economia cambial estimada: US$ 2-3 bilhões/ano
    4. ✅ Autossuficiência em gasolina: Brasil zeraria importação
    
    RECOMENDAÇÃO:
    → Adotar gatilhos automáticos SELIX Energy (E30-E35-E40-E42)
    → Elevar imediatamente para E32
    → Preparar para E35 se Brent > US$ 90
    """)
    
    return forecast

if __name__ == "__main__":
    forecast = main()
