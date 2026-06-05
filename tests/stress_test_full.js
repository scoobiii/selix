/**
 * stress_test_full.js — Selix v5.0.0-GOS3
 * Stress test SEM expor chaves no código
 * 
 * Uso:
 *   k6 run -e BASE_URL=http://localhost:5000 tests/stress_test_full.js
 * 
 * A chave é lida do ambiente via -e SELIX_API_KEY=...
 * NUNCA hardcode de chave neste arquivo.
 */

import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';

// ── MÉTRICAS CUSTOMIZADAS ──────────────────────────────────────
const errorRate      = new Rate('errors');
const latencyHealth  = new Trend('latency_health',  true);
const latencyBrent   = new Trend('latency_brent',   true);
const latencySelic   = new Trend('latency_selic',   true);
const latencyPergunt = new Trend('latency_perguntar',true);
const http401Count   = new Counter('auth_errors_401');
const http503Count   = new Counter('service_unavailable_503');

// ── CONFIGURAÇÃO VIA VARIÁVEIS DE AMBIENTE ────────────────────
// Nunca hardcode de chave — sempre via -e KEY=valor
const BASE_URL = __ENV.BASE_URL || 'http://localhost:5000';
const API_KEY  = __ENV.SELIX_API_KEY || '';   // vazio = testa auth failure

// ── CENÁRIOS DE CARGA ─────────────────────────────────────────
export let options = {
  scenarios: {

    // Cenário 1: ramp-up gradual (carga normal)
    ramp_up: {
      executor:    'ramping-vus',
      startVUs:    0,
      stages: [
        { duration:'30s', target:10  },  // aquece
        { duration:'1m',  target:30  },  // carga normal
        { duration:'1m',  target:50  },  // carga alta
        { duration:'30s', target:0   },  // resfria
      ],
      gracefulRampDown: '15s',
    },

    // Cenário 2: spike test (pico súbito)
    spike: {
      executor:   'ramping-vus',
      startTime:  '3m30s',   // começa depois do ramp_up
      startVUs:   0,
      stages: [
        { duration:'10s', target:80  },  // spike
        { duration:'30s', target:80  },  // sustenta
        { duration:'10s', target:0   },  // cai
      ],
      gracefulRampDown: '10s',
    },
  },

  thresholds: {
    // API deve responder em <500ms p95
    'http_req_duration':           ['p(95)<500'],
    // Menos de 5% de erros (excluindo 401 e 503 esperados)
    'errors':                      ['rate<0.05'],
    // Endpoints críticos mais rígidos
    'latency_health':              ['p(99)<300'],
    'latency_brent':               ['p(95)<200'],
  },
};

// ── HEADERS ───────────────────────────────────────────────────
function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'X-API-Key':    API_KEY,
  };
}

// ── FUNÇÕES DE TESTE ──────────────────────────────────────────

function testHealth() {
  const r = http.get(`${BASE_URL}/v1/health`, { timeout:'5s' });
  latencyHealth.add(r.timings.duration);
  const ok = check(r, {
    'health 200':      res => res.status === 200,
    'health has status': res => {
      try { return JSON.parse(res.body).status === 'ok'; }
      catch { return false; }
    },
  });
  if (!ok) errorRate.add(1);
  else      errorRate.add(0);
}

function testBrentPublico() {
  // Endpoint público — sem chave — variação de Brent
  const brent = Math.floor(Math.random() * 70 + 50); // 50-120
  const r = http.get(`${BASE_URL}/v1/energia/mistura/${brent}`, { timeout:'5s' });
  latencyBrent.add(r.timings.duration);
  const ok = check(r, {
    'brent 200':      res => res.status === 200,
    'brent has etanol': res => {
      try { return JSON.parse(res.body).etanol !== undefined; }
      catch { return false; }
    },
  });
  if (!ok) errorRate.add(1);
  else      errorRate.add(0);
}

function testSelic() {
  const r = http.get(`${BASE_URL}/v1/selic`, {
    headers: authHeaders(),
    timeout: '5s',
  });
  latencySelic.add(r.timings.duration);

  if (r.status === 401) { http401Count.add(1); return; }
  if (r.status === 503) { http503Count.add(1); return; }

  const ok = check(r, {
    'selic 200 ou 503': res => res.status === 200 || res.status === 503,
  });
  if (!ok) errorRate.add(1);
  else      errorRate.add(0);
}

function testPerguntar() {
  const perguntas = [
    'Qual a Selic ideal?',
    'O que é o Selix?',
    'Como calcular a meta ótima?',
    'Qual o impacto do Brent na mistura?',
    'Quantas empresas estão em recuperação judicial?',
  ];
  const pergunta = perguntas[Math.floor(Math.random() * perguntas.length)];

  const r = http.post(
    `${BASE_URL}/v1/perguntar`,
    JSON.stringify({ pergunta }),
    { headers: authHeaders(), timeout:'10s' },
  );
  latencyPergunt.add(r.timings.duration);

  if (r.status === 401) { http401Count.add(1); return; }

  // Aceita 202 (assíncrono) OU 200 (síncrono legado)
  const ok = check(r, {
    'perguntar 202 ou 200': res => res.status === 202 || res.status === 200,
    'perguntar tem resposta': res => {
      try {
        const b = JSON.parse(res.body);
        return b.task_id !== undefined || b.resposta !== undefined;
      } catch { return false; }
    },
  });
  if (!ok) errorRate.add(1);
  else      errorRate.add(0);

  // Se 202, faz polling do resultado (simulação realista)
  if (r.status === 202) {
    try {
      const taskId = JSON.parse(r.body).task_id;
      if (taskId) {
        sleep(2);   // aguarda processamento
        const poll = http.get(
          `${BASE_URL}/v1/task/${taskId}`,
          { headers: authHeaders(), timeout:'5s' },
        );
        check(poll, {
          'task result 200 ou 404': res =>
            res.status === 200 || res.status === 404,
        });
      }
    } catch {}
  }
}

function testAdminSemChave() {
  // Verifica que admin rejeita sem X-Admin-Key
  const r = http.post(
    `${BASE_URL}/v1/admin/generate_key`,
    JSON.stringify({ client_name: 'hacker' }),
    { headers: { 'Content-Type': 'application/json' }, timeout:'3s' },
  );
  check(r, {
    'admin sem chave retorna 403': res => res.status === 403,
  });
  // 403 é comportamento correto — não conta como erro
}

// ── MAIN ──────────────────────────────────────────────────────
export default function () {
  group('public', () => {
    testHealth();
    testBrentPublico();
  });

  group('private', () => {
    testSelic();
    testPerguntar();
  });

  group('security', () => {
    testAdminSemChave();
  });

  // Pensa humano: pausa variável entre iterações
  sleep(Math.random() * 1.5 + 0.5);
}

// ── SETUP: verifica se API está de pé antes de iniciar ────────
export function setup() {
  const r = http.get(`${BASE_URL}/v1/health`, { timeout:'5s' });
  if (r.status !== 200) {
    throw new Error(
      `❌ API não está respondendo em ${BASE_URL}\n` +
      `   Status: ${r.status}\n` +
      `   Verifique: curl ${BASE_URL}/v1/health`
    );
  }
  console.log(`✅ API online em ${BASE_URL}`);
  if (!API_KEY) {
    console.warn('⚠️  SELIX_API_KEY não definida — endpoints privados retornarão 401');
  }
  return { base_url: BASE_URL };
}

// ── TEARDOWN: resumo final ────────────────────────────────────
export function teardown(data) {
  console.log(`\n✅ Stress test concluído — API: ${data.base_url}`);
}
