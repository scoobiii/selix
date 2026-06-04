#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# variable_load_test.py - Teste de carga com variáveis de mercado
# Versão: 1.0.0-GOS3
# Responsabilidade: Simular carga variável baseada em padrões de mercado

import os
import sys
import time
import json
import random
import threading
import requests
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configurações padrão (sobrescritas por variáveis de ambiente)
API_BASE = os.environ.get('API_BASE', 'http://localhost:5000')
API_KEY = os.environ.get('SELIX_API_KEY', '10afec6a373e15a691f4698aea01f795257e4ae502090be8753399229e9effa9')

HEADERS = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
}

# ========== PADRÕES DE MERCADO ==========
class MarketPatterns:
    """Define padrões de carga baseados em horários e eventos de mercado"""
    
    @staticmethod
    def get_load_factor() -> float:
        """Retorna fator de carga baseado no horário atual"""
        hour = datetime.now().hour
        # Padrão de mercado brasileiro
        if 9 <= hour <= 12:  # Manhã (abertura mercado)
            return 1.5
        elif 14 <= hour <= 17:  # Tarde (fechamento mercado)
            return 1.3
        elif 20 <= hour <= 22:  # Noite (pós-mercado)
            return 0.8
        elif 0 <= hour <= 5:  # Madrugada
            return 0.2
        else:
            return 1.0
    
    @staticmethod
    def get_spike_probability() -> float:
        """Probabilidade de pico de tráfego (ex: divulgação de dados)"""
        minute = datetime.now().minute
        # Simula divulgação de dados nos minutos 0, 15, 30, 45
        if minute in [0, 15, 30, 45]:
            return 0.3
        return 0.05
    
    @staticmethod
    def get_day_factor() -> float:
        """Fator baseado no dia da semana"""
        weekday = datetime.now().weekday()
        if weekday >= 5:  # Fim de semana
            return 0.4
        elif weekday == 0:  # Segunda-feira (volume maior)
            return 1.2
        elif weekday == 4:  # Sexta-feira (volume reduzido)
            return 0.8
        return 1.0

@dataclass
class TestResult:
    """Resultado de um teste individual"""
    endpoint: str
    success: bool
    status_code: int
    response_time_ms: float
    timestamp: str
    error: str = ""

class LoadTester:
    """Tester de carga com padrões de mercado"""
    
    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url
        self.headers = {'X-API-Key': api_key, 'Content-Type': 'application/json'}
        self.results: List[TestResult] = []
        self.lock = threading.Lock()
    
    endpoints = [
        ('GET', '/v1/health', False),
        ('GET', '/v1/selic', True),
        ('GET', '/v1/energia/mistura', True),
        ('GET', '/v1/commodities', True),
        ('GET', '/v1/empresas/rj', True),
        ('GET', '/v1/sentimento', True),
        ('GET', '/v1/alertas/geral', True),
        ('GET', '/v1/faq?q=selic', True),
    ]
    
    def make_request(self, method: str, path: str, use_auth: bool) -> TestResult:
        """Faz uma requisição e registra o resultado"""
        url = f"{self.base_url}{path}"
        headers = self.headers if use_auth else {'Content-Type': 'application/json'}
        
        start_time = time.time()
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=10)
            else:
                response = requests.post(url, headers=headers, timeout=10)
            
            response_time = (time.time() - start_time) * 1000
            
            return TestResult(
                endpoint=path,
                success=200 <= response.status_code < 300,
                status_code=response.status_code,
                response_time_ms=response_time,
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return TestResult(
                endpoint=path,
                success=False,
                status_code=0,
                response_time_ms=(time.time() - start_time) * 1000,
                timestamp=datetime.now().isoformat(),
                error=str(e)
            )
    
    def run_load_test(self, duration_seconds: int = 60, workers: int = 10):
        """Executa teste de carga com workers paralelos"""
        print(f"\n🚀 Iniciando teste de carga por {duration_seconds}s com {workers} workers")
        print(f"📍 API: {self.base_url}")
        print(f"📊 Padrão de mercado: fator={MarketPatterns.get_load_factor():.2f}, dia={MarketPatterns.get_day_factor():.2f}")
        print("-" * 60)
        
        end_time = time.time() + duration_seconds
        request_count = 0
        
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = []
            
            while time.time() < end_time:
                # Ajusta carga baseada em padrões de mercado
                load_factor = MarketPatterns.get_load_factor() * MarketPatterns.get_day_factor()
                current_workers = max(1, int(workers * load_factor))
                
                # Pico aleatório
                if random.random() < MarketPatterns.get_spike_probability():
                    current_workers = min(workers * 2, 50)
                    print(f"⚡ Pico de tráfego detectado! Workers: {current_workers}")
                
                # Dispara requisições
                for _ in range(current_workers):
                    method, path, auth = random.choice(self.endpoints)
                    future = executor.submit(self.make_request, method, path, auth)
                    futures.append(future)
                    request_count += 1
                
                time.sleep(0.1)  # Pequena pausa entre ciclos
            
            # Coleta resultados
            for future in as_completed(futures):
                result = future.result()
                with self.lock:
                    self.results.append(result)
    
    def print_report(self):
        """Imprime relatório detalhado"""
        if not self.results:
            print("Nenhum resultado para reportar")
            return
        
        total = len(self.results)
        successes = sum(1 for r in self.results if r.success)
        failures = total - successes
        
        # Estatísticas de tempo de resposta
        response_times = [r.response_time_ms for r in self.results if r.success]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            p95 = sorted(response_times)[int(len(response_times) * 0.95)]
            p99 = sorted(response_times)[int(len(response_times) * 0.99)]
            max_time = max(response_times)
        else:
            avg_time = p95 = p99 = max_time = 0
        
        print("\n" + "=" * 60)
        print("📊 RELATÓRIO DE TESTE DE CARGA")
        print("=" * 60)
        print(f"\n📈 RESUMO:")
        print(f"   Total requisições: {total}")
        print(f"   ✅ Sucessos: {successes} ({successes/total*100:.1f}%)")
        print(f"   ❌ Falhas: {failures} ({failures/total*100:.1f}%)")
        print(f"\n⏱️  TEMPO DE RESPOSTA (ms):")
        print(f"   Média: {avg_time:.2f} ms")
        print(f"   P95: {p95:.2f} ms")
        print(f"   P99: {p99:.2f} ms")
        print(f"   Máximo: {max_time:.2f} ms")
        
        # Estatísticas por endpoint
        print(f"\n📁 POR ENDPOINT:")
        endpoints_stats = {}
        for r in self.results:
            if r.endpoint not in endpoints_stats:
                endpoints_stats[r.endpoint] = {'total': 0, 'success': 0, 'times': []}
            endpoints_stats[r.endpoint]['total'] += 1
            if r.success:
                endpoints_stats[r.endpoint]['success'] += 1
                endpoints_stats[r.endpoint]['times'].append(r.response_time_ms)
        
        for endpoint, stats in endpoints_stats.items():
            success_rate = stats['success'] / stats['total'] * 100 if stats['total'] > 0 else 0
            avg = sum(stats['times']) / len(stats['times']) if stats['times'] else 0
            status = "✅" if success_rate > 95 else "⚠️" if success_rate > 80 else "❌"
            print(f"   {status} {endpoint}: {stats['success']}/{stats['total']} ({success_rate:.1f}%) - avg {avg:.1f}ms")
        
        # Verificação de thresholds
        print(f"\n🎯 THRESHOLDS:")
        thresholds_ok = True
        if successes/total < 0.95:
            print(f"   ❌ Taxa de sucesso ({successes/total*100:.1f}%) < 95%")
            thresholds_ok = False
        else:
            print(f"   ✅ Taxa de sucesso ({successes/total*100:.1f}%) >= 95%")
        
        if avg_time > 500:
            print(f"   ❌ Tempo médio ({avg_time:.0f}ms) > 500ms")
            thresholds_ok = False
        else:
            print(f"   ✅ Tempo médio ({avg_time:.0f}ms) <= 500ms")
        
        if p95 > 1000:
            print(f"   ❌ P95 ({p95:.0f}ms) > 1000ms")
            thresholds_ok = False
        else:
            print(f"   ✅ P95 ({p95:.0f}ms) <= 1000ms")
        
        print("\n" + "=" * 60)
        if thresholds_ok:
            print("🎉 TESTE APROVADO - Sistema dentro dos limites")
        else:
            print("⚠️ TESTE REPROVADO - Sistema fora dos limites esperados")
        print("=" * 60)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Teste de carga Selix')
    parser.add_argument('--duration', type=int, default=60, help='Duração em segundos')
    parser.add_argument('--workers', type=int, default=10, help='Número de workers')
    parser.add_argument('--base-url', type=str, default=API_BASE, help='URL da API')
    parser.add_argument('--api-key', type=str, default=API_KEY, help='Chave da API')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🔬 SELIX - TESTE DE CARGA COM PADRÕES DE MERCADO")
    print("=" * 60)
    print(f"⏰ Início: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tester = LoadTester(args.base_url, args.api_key)
    tester.run_load_test(duration_seconds=args.duration, workers=args.workers)
    tester.print_report()
    
    # Salva resultados
    with open('load_test_results.json', 'w') as f:
        json.dump([{
            'endpoint': r.endpoint,
            'success': r.success,
            'status_code': r.status_code,
            'response_time_ms': r.response_time_ms,
            'timestamp': r.timestamp,
            'error': r.error
        } for r in tester.results], f, indent=2)
    print(f"\n💾 Resultados salvos em load_test_results.json")

if __name__ == "__main__":
    main()
