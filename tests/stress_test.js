// k6 - Teste de estresse (pico súbito)
import http from 'k6/http';
import { check } from 'k6';

export const options = {
    scenarios: {
        stress: {
            executor: 'ramping-arrival-rate',
            startRate: 50,
            timeUnit: '1s',
            preAllocatedVUs: 100,
            maxVUs: 500,
            stages: [
                { duration: '30s', target: 200 },  // 200 req/segundo
                { duration: '1m', target: 500 },   // 500 req/segundo
                { duration: '30s', target: 0 },
            ],
        },
    },
    thresholds: {
        http_req_failed: ['rate<0.05'],  // Máximo 5% de falha
    },
};

const BASE_URL = 'http://localhost:5000';

export default function () {
    const res = http.get(`${BASE_URL}/v1/health`);
    check(res, { 'status is 200': (r) => r.status === 200 });
}
