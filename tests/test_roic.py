#!/usr/bin/env python3
"""
Testes para roic.py — SELIX (módulo ROIC/RJ, dados placeholder).

Rodar: pytest test_roic.py -v
"""

import pytest
from src.selix.roic import (
    Empresa,
    EMPRESAS,
    get_empresas_que_batem_selic,
    get_empresas_rj,
    get_empresas_rj_que_batem_selic,
    roic_medio_ponderado_por_empresa,
)

SELIC_ATUAL = 14.25


class TestFiltroPorEmpresa:
    def test_filtro_e_por_empresa_nao_por_setor(self):
        """
        Regressão direta do bug do v7.1: RAIZ4 (ROIC=8.5%, em RJ) está
        no setor Energia (média puxada por PETR4=18.5%, PRIO3=17.2%).
        Se o filtro estivesse por setor, RAIZ4 apareceria batendo a
        Selic. Tem que ficar de fora.
        """
        batem = get_empresas_que_batem_selic(SELIC_ATUAL)
        codigos = [e.codigo for e in batem]
        assert "RAIZ4" not in codigos

    def test_apenas_petr4_prio3_abev3_batem_selic_atual(self):
        batem = get_empresas_que_batem_selic(SELIC_ATUAL)
        codigos = sorted(e.codigo for e in batem)
        assert codigos == ["ABEV3", "PETR4", "PRIO3"]

    def test_nenhuma_empresa_bate_selic_zero_empresas_input_vazio(self):
        assert get_empresas_que_batem_selic(SELIC_ATUAL, empresas=[]) == []


class TestSanidadeRJ:
    def test_nenhuma_empresa_rj_bate_a_selic(self):
        """
        Se isso falhar, é sinal de dado inconsistente (empresa em
        recuperação judicial com ROIC acima da Selic não faz sentido
        econômico) — não é "empresa excepcional", é bug de dado.
        """
        inconsistentes = get_empresas_rj_que_batem_selic(SELIC_ATUAL)
        assert inconsistentes == []

    def test_lista_rj_tem_as_4_empresas_conhecidas(self):
        rj = sorted(e.codigo for e in get_empresas_rj())
        assert rj == ["AMER3", "PCAR3", "RAIZ4", "VIIA3"]


class TestRoicMedio:
    def test_media_simples_nao_ponderada_por_setor_arbitrario(self):
        media = roic_medio_ponderado_por_empresa()
        assert media == pytest.approx(10.19, abs=0.01)

    def test_lista_vazia_levanta_erro(self):
        with pytest.raises(ValueError):
            roic_medio_ponderado_por_empresa(empresas=[])


class TestDadosSaoPlaceholder:
    """
    Trava de honestidade: garante que ninguém tira o aviso de
    'placeholder' do código sem querer, e commita como se fosse
    fonte real (foi exatamente o que aconteceu no README do v7.2).
    """
    def test_modulo_tem_aviso_de_placeholder_no_docstring(self):
        import src.selix.roic as roic
        assert "PLACEHOLDER" in roic.__doc__

    def test_total_rj_brasil_nao_tem_valor_fabricado(self):
        import src.selix.roic as roic
        assert roic.TOTAL_EMPRESAS_RJ_BRASIL_ESTIMADO is None, (
            "Se alguém colocou um número aqui, precisa vir com fonte "
            "(Serasa/BCB/CVM) linkada no commit, não só um int solto."
        )


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__, "-v"]))
