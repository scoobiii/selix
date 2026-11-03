import http from 'k6/http';
import { check, sleep } from 'k6';

http.setResponseCallback(
  http.expectedStatuses(200, 401, 404, 503)
);

export const options = {
  stages: [
    { duration: '20s', target: 5 },
    { duration: '40s', target: 15 },
    { duration: '20s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<5000'],
    http_req_failed: ['rate<0.05'],
  },
};

const BASE_URL = 'http://127.0.0.1:5000';
const HEADERS = { 'X-API-Key': 'test_api_key_123' };

export default function () {
  let res = http.get(`${BASE_URL}/v1/health`);
  check(res, { 'health 200': (r) => r.status === 200 });

  res = http.get(`${BASE_URL}/v1/energia/mistura/80`);
  check(res, { 'mistura 200/503': (r) => r.status === 200 || r.status === 503 });

  res = http.get(`${BASE_URL}/v1/commodities`, { headers: HEADERS });
  check(res, { 'commodities 200/503': (r) => r.status === 200 || r.status === 503 });

  res = http.get(`${BASE_URL}/v1/selic`, { headers: HEADERS });
  check(res, { 'selic 200/503': (r) => r.status === 200 || r.status === 503 });

  res = http.get(`${BASE_URL}/v1/alertas/geral`, { headers: HEADERS });
  check(res, { 'alertas 200/404/503': (r) => [200, 404, 503].includes(r.status) });

  sleep(1);
}
