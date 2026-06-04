// load_test.js - Teste de carga para API Selix
// k6 run tests/stress/load_test.js

import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// Métricas customizadas
const errorRate = new Rate('error_rate');
const responseTime = new Trend('response_time');
const requestsTotal = new Counter('requests_total');

// Configuração do teste (ajustável via variáveis de ambiente)
export const options = {
    // Cenário 1: Teste de fumaça (quick check)
    scenarios: {
        smoke: {
            executor: 'constant-vus',
            vus: 1,
            duration: '30s',
            startTime: '0s',
            tags: { test_type: 'smoke' },
        },
        // Cenário 2: Carga média (simula tráfego normal)
        average: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '1m', target: 10 },  // sobe para 10 usuários
                { duration: '2m', target: 10 },  // mantém 10 usuários
                { duration: '1m', target: 0 },   // desce para 0
            ],
            startTime: '30s',
            tags: { test_type: 'average' },
            env: { SCENARIO: 'average' }
        },
        // Cenário 3: Pico de estresse (simula Black Friday)
        stress: {
            executor: 'ramping-vus',
            startVUs: 0,
            stages: [
                { duration: '30s', target: 20 },
                { duration: '1m', target: 50 },
                { duration: '30s', target: 100 },
                { duration: '1m', target: 100 },
                { duration: '30s', target: 0 },
            ],
            startTime: '3m30s',
            tags: { test_type: 'stress' },
        },
    },
    thresholds: {
        'http_req_duration': ['p(95)<500', 'p(99)<1000'], // 95% < 500ms, 99% < 1s
        'error_rate': ['rate<0.05'], // menos de 5% de erro
        'response_time': ['avg<300'],
    },
};

// Configurações
const API_BASE = __ENV.API_BASE || 'http://localhost:5000';
const API_KEY = __ENV.SELIX_API_KEY || '10afec6a373e15a691f4698aea01f795257e4ae502090be8753399229e9effa9';

const HEADERS = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json',
};

// Endpoints a serem testados
const endpoints = [
    { name: 'health', path: '/v1/health', auth: false, method: 'GET' },
    { name: 'selic', path: '/v1/selic', auth: true, method: 'GET' },
    { name: 'energia_mistura', path: '/v1/energia/mistura', auth: true, method: 'GET' },
    { name: 'commodities', path: '/v1/commodities', auth: true, method: 'GET' },
    { name: 'empresas_rj', path: '/v1/empresas/rj', auth: true, method: 'GET' },
    { name: 'sentimento', path: '/v1/sentimento', auth: true, method: 'GET' },
    { name: 'alertas', path: '/v1/alertas/geral', auth: true, method: 'GET' },
];

// Função para fazer requisição com métricas
function makeRequest(endpoint) {
    const url = `${API_BASE}${endpoint.path}`;
    const headers = endpoint.auth ? HEADERS : { 'Content-Type': 'application/json' };
    
    const response = endpoint.method === 'GET' 
        ? http.get(url, { headers })
        : http.post(url, {}, { headers });
    
    const success = response.status >= 200 && response.status < 300;
    errorRate.add(!success);
    responseTime.add(response.timings.duration);
    requestsTotal.add(1);
    
    check(response, {
        [`${endpoint.name} status 2xx`]: (r) => r.status >= 200 && r.status < 300,
        [`${endpoint.name} response < 500ms`]: (r) => r.timings.duration < 500,
    });
    
    return response;
}

// Função principal do teste
export default function () {
    // Testa endpoints públicos
    for (const endpoint of endpoints) {
        if (!endpoint.auth) {
            makeRequest(endpoint);
        }
    }
    
    // Testa endpoints autenticados (simula um usuário real)
    for (const endpoint of endpoints) {
        if (endpoint.auth) {
            makeRequest(endpoint);
        }
    }
    
    // Simula pausa entre ações do usuário
    sleep(Math.random() * 2 + 0.5);
}

// Função de setup (roda uma vez antes dos testes)
export function setup() {
    console.log(`🚀 Iniciando teste de carga na API: ${API_BASE}`);
    console.log(`📊 Cenários: smoke (30s) → average (3m) → stress (2m)`);
    console.log(`🎯 Thresholds: p95<500ms, p99<1s, erro<5%`);
    
    // Teste rápido de conectividade
    const healthCheck = http.get(`${API_BASE}/v1/health`);
    if (healthCheck.status !== 200) {
        throw new Error(`API não está respondendo em ${API_BASE}`);
    }
    
    return { startTime: new Date().toISOString() };
}

// Função de teardown (roda uma vez após os testes)
export function teardown(data) {
    console.log(`\n✅ Teste concluído. Iniciado em: ${data.startTime}`);
    console.log(`📈 Relatório completo gerado ao final.`);
}
