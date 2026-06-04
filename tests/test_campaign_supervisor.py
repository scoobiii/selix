#!/usr/bin/env python3
# tests/test_campaign_supervisor.py
# Testes para o campaign_supervisor (agendador de posts)

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch, MagicMock
from scripts.campaign_supervisor import get_campaign_day, run_campaign

def test_get_campaign_day_returns_1_to_30():
    """Verifica se o dia da campanha está sempre entre 1 e 30"""
    with patch('scripts.campaign_supervisor.date') as mock_date:
        mock_date.today.return_value = mock_date
        # Delta 0 -> dia 1
        mock_date.__sub__.return_value.days = 0
        assert get_campaign_day() == 1
        # Delta 29 -> dia 30
        mock_date.__sub__.return_value.days = 29
        assert get_campaign_day() == 30
        # Delta 30 -> dia 1 (reinicia)
        mock_date.__sub__.return_value.days = 30
        assert get_campaign_day() == 1

def test_run_campaign_calls_subprocess_with_correct_args():
    """Verifica se run_campaign chama subprocess com os argumentos certos"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        with patch('scripts.campaign_supervisor.get_campaign_day', return_value=5):
            run_campaign(modo="independente")  # modo independente (sem --thread)
        args = mock_run.call_args[0][0]
        assert '--day' in args
        assert '5' in args
        assert '--post' in args
        assert '--thread' not in args

def test_run_campaign_thread_mode():
    """Verifica modo thread (--thread)"""
    with patch('subprocess.run') as mock_run:
        mock_run.return_value.returncode = 0
        with patch('scripts.campaign_supervisor.get_campaign_day', return_value=10):
            run_campaign(modo="thread")
        args = mock_run.call_args[0][0]
        assert '--thread' in args

def test_run_campaign_handles_subprocess_error():
    """Se o subprocess falhar, a exceção não deve quebrar o supervisor"""
    with patch('subprocess.run', side_effect=Exception("comando falhou")):
        # Deve chamar mark_post_result(False) e não levantar exceção
        try:
            run_campaign()
        except Exception:
            pytest.fail("run_campaign levantou exceção inesperada")
