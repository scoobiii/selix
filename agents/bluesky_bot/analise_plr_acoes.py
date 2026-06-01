#!/usr/bin/env python3
"""
Análise de PLR, Conversão de Dívida e Governança Corporativa
Baseado no caso GPA (Pão de Açúcar)
"""

class AnalisePLRAcoes:
    def __init__(self):
        # Dados do GPA (exemplo)
        self.dados_empresa = {
            "nome": "GPA",
            "preco_acao_max": 105.00,
            "preco_atual": 2.60,
            "desvalorizacao": 97.5,
            "funcionarios": 45000,
            "terceirizados": 25000,
            "divida_total": 4.5e9,
            "lucro_anual": 1.2e9,
            "vendas_anuais": 35e9,
        }
    
    def calcular_plr_como_percentual(self, plr_por_funcionario=2000):
        """Calcula PLR como % do lucro e vendas"""
        
        total_funcionarios = (self.dados_empresa["funcionarios"] + 
                             self.dados_empresa["terceirizados"])
        
        plr_total = total_funcionarios * plr_por_funcionario
        
        # % do lucro
        perc_lucro = (plr_total / self.dados_empresa["lucro_anual"]) * 100
        
        # % das vendas
        perc_vendas = (plr_total / self.dados_empresa["vendas_anuais"]) * 100
        
        # % do serviço da dívida (assumindo juros 14.5% sobre dívida)
        servico_divida = self.dados_empresa["divida_total"] * 0.145
        perc_servico_divida = (plr_total / servico_divida) * 100
        
        return {
            "plr_total": plr_total,
            "perc_lucro": perc_lucro,
            "perc_vendas": perc_vendas,
            "perc_servico_divida": perc_servico_divida,
            "total_funcionarios": total_funcionarios
        }
    
    def calcular_conversao_divida_acoes(self, percentual_conversao=50):
        """Calcula impacto da conversão de dívida em ações para funcionários"""
        
        divida_convertida = self.dados_empresa["divida_total"] * (percentual_conversao / 100)
        
        acoes_circulacao = 500_000_000
        valor_empresa = self.dados_empresa["preco_atual"] * acoes_circulacao
        
        acoes_para_funcionarios = (divida_convertida / valor_empresa) * acoes_circulacao
        acoes_por_funcionario = acoes_para_funcionarios / self.dados_empresa["funcionarios"]
        
        participacao_percentual = (divida_convertida / valor_empresa) * 100
        assentos_conselho = int(participacao_percentual / 5)
        
        return {
            "divida_convertida": divida_convertida,
            "acoes_para_funcionarios": acoes_para_funcionarios,
            "acoes_por_funcionario": acoes_por_funcionario,
            "participacao_percentual": participacao_percentual,
            "assentos_conselho": max(1, assentos_conselho),
            "valor_acao_conversao": divida_convertida / acoes_para_funcionarios if acoes_para_funcionarios > 0 else 0
        }
    
    def gerar_relatorio(self):
        """Gera relatório completo"""
        
        plr = self.calcular_plr_como_percentual()
        conversao = self.calcular_conversao_divida_acoes()
        
        print("=" * 70)
        print("📊 ANÁLISE PLR E CONVERSÃO DE DÍVIDA")
        print("=" * 70)
        print(f"\n🏢 Empresa: {self.dados_empresa['nome']}")
        print(f"📉 Queda da ação: R$ {self.dados_empresa['preco_acao_max']} → R$ {self.dados_empresa['preco_atual']}")
        print(f"   Desvalorização: {self.dados_empresa['desvalorizacao']}%")
        
        print("\n" + "=" * 70)
        print("💰 PLR DE R$ 2.000 POR FUNCIONÁRIO")
        print("=" * 70)
        print(f"👥 Total beneficiados: {plr['total_funcionarios']:,}")
        print(f"💵 PLR total: R$ {plr['plr_total']/1e6:.1f} milhões")
        print(f"📊 Percentual do lucro anual: {plr['perc_lucro']:.2f}%")
        print(f"📊 Percentual das vendas: {plr['perc_vendas']:.3f}%")
        print(f"📊 Percentual do serviço da dívida: {plr['perc_servico_divida']:.2f}%")
        
        print("\n" + "=" * 70)
        print("🔄 CONVERSÃO DE 50% DA DÍVIDA EM AÇÕES")
        print("=" * 70)
        print(f"💸 Dívida convertida: R$ {conversao['divida_convertida']/1e9:.2f} bilhões")
        print(f"📈 Ações para funcionários: {conversao['acoes_para_funcionarios']/1e6:.1f} milhões")
        print(f"👷 Ações por funcionário: {conversao['acoes_por_funcionario']:.0f}")
        print(f"🎯 Participação no capital: {conversao['participacao_percentual']:.1f}%")
        print(f"🪑 Assentos no Conselho: {conversao['assentos_conselho']}")
        
        print("\n" + "=" * 70)
        print("⚖️ COMPARAÇÃO CRÍTICA")
        print("=" * 70)
        print(f"💰 PLR total: R$ {plr['plr_total']/1e6:.1f}M")
        print(f"💸 Serviço da dívida anual: R$ {self.dados_empresa['divida_total'] * 0.145 / 1e9:.2f}B")
        print(f"📉 PLR é apenas {plr['perc_servico_divida']:.1f}% do que se paga em juros")
        
        print("\n" + "=" * 70)
        print("🏛️ PROPOSTA TRAMPOFORTE")
        print("=" * 70)
        print("1. PLR tem prioridade sobre serviço da dívida")
        print("2. 50% da renegociação em ações para trabalhadores")
        print(f"3. {conversao['assentos_conselho']} assentos no Conselho para representantes")
        print("4. Veto a acordos que prejudiquem trabalhadores")
        
        return {"plr": plr, "conversao": conversao}

if __name__ == "__main__":
    analise = AnalisePLRAcoes()
    analise.gerar_relatorio()
