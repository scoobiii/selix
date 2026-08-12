// k6 - Teste de carga para Selix API
// Executar: k6 run tests/load_test.js

import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
    stages: [
        { duration: '30s', target: 20 },
        { duration: '1m', target: 50 },
        { duration: '1m', target: 100 },
        { duration: '30s', target: 0 },
    ],
    thresholds: {
        http_req_duration: ['p(95)<500'],
        http_req_failed: ['rate<0.01'],
    },
};

const BASE_URL = 'http://localhost:5000';
const HEADERS = { 'X-API-Key': 'test_api_key_123' };

export default function () {
    let res = http.get(`${BASE_URL}/v1/health`);
    check(res, { 'health status 200': (r) => r.status === 200 });
    
    res = http.get(`${BASE_URL}/v1/energia/mistura`);
    check(res, { 'mistura status 200/503': (r) => r.status === 200 || r.status === 503 });
    
    res = http.get(`${BASE_URL}/v1/commodities`, { headers: HEADERS });
    check(res, { 'commodities status 200/503': (r) => r.status === 200 || r.status === 503 });
    
    res = http.get(`${BASE_URL}/v1/selic`, { headers: HEADERS });
    check(res, { 'selic status 200/503': (r) => r.status === 200 || r.status === 503 });
    
    res = http.get(`${BASE_URL}/v1/alertas/geral`, { headers: HEADERS });
    check(res, { 'alertas status 200/404/503': (r) => [200, 404, 503].includes(r.status) });
    
    sleep(1);
}
