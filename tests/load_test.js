// k6 - Teste de carga para Selix API
// Executar: k6 run load_test.js

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 20 },   // Rampa para 20 usuários
        { duration: '1m', target: 50 },    // Rampa para 50 usuários
        { duration: '1m', target: 100 },   // Rampa para 100 usuários
        { duration: '30s', target: 0 },    // Desaceleração
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'],  // 95% das req < 500ms
        http_req_failed: ['rate<0.01'],    // Menos de 1% de falha
    },
};

const BASE_URL = 'http://localhost:5000';

export default function () {
    // 1. Health check
    let res = http.get(`${BASE_URL}/v1/health`);
    check(res, { 'health status 200': (r) => r.status === 200 });
    
    // 2. Energia mix
    res = http.get(`${BASE_URL}/v1/energia/mistura`);
    check(res, { 'mistura status 200/503': (r) => r.status === 200 || r.status === 503 });
    
    // 3. Commodities
    res = http.get(`${BASE_URL}/v1/commodities`);
    check(res, { 'commodities status 200/503': (r) => r.status === 200 || r.status === 503 });
    
    // 4. Selic
    res = http.get(`${BASE_URL}/v1/selic`);
    check(res, { 'selic status 200/503': (r) => r.status === 200 || r.status === 503 });
    
    // 5. Alertas
    res = http.get(`${BASE_URL}/v1/alertas/geral`);
    check(res, { 'alertas status 200': (r) => r.status === 200 });
    
    sleep(1);
}
