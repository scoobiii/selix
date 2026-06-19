#!/usr/bin/env python3
"""
Hospital Squad Dashboard — Timeline em Tempo Real
"""
from flask import Flask, render_template_string, jsonify
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path

app = Flask(__name__)
DB_PATH = "/root/selix/hospital_squad/hospital_squad.db"

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Hospital Squad NOC</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        .pulse { animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; } }
    </style>
</head>
<body class="bg-gray-900 text-white">
    <div class="container mx-auto p-6">
        <div class="flex justify-between items-center mb-8">
            <h1 class="text-3xl font-bold flex items-center gap-3">
                <i class="fas fa-hospital"></i>
                Hospital Squad NOC
            </h1>
            <div class="flex items-center gap-4">
                <div class="flex items-center gap-2 text-green-400 pulse">
                    <div class="w-3 h-3 bg-green-500 rounded-full"></div>
                    ONLINE
                </div>
                <button onclick="refreshData()" class="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded">
                    <i class="fas fa-sync-alt"></i> Atualizar
                </button>
            </div>
        </div>

        <!-- Stats Cards -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div class="bg-gray-800 rounded-xl p-6">                <h3 class="text-gray-400 text-sm">Auditorias Ativas</h3>
                <div id="active-audits" class="text-4xl font-bold text-blue-400">0</div>
            </div>
            <div class="bg-gray-800 rounded-xl p-6">
                <h3 class="text-gray-400 text-sm">Health Score Médio</h3>
                <div id="avg-score" class="text-4xl font-bold text-amber-400">0</div>
            </div>
            <div class="bg-gray-800 rounded-xl p-6">
                <h3 class="text-gray-400 text-sm">Issues Críticas</h3>
                <div id="critical-issues" class="text-4xl font-bold text-red-400">0</div>
            </div>
            <div class="bg-gray-800 rounded-xl p-6">
                <h3 class="text-gray-400 text-sm">Cobertura Média</h3>
                <div id="avg-coverage" class="text-4xl font-bold text-green-400">0%</div>
            </div>
        </div>

        <!-- Timeline -->
        <div class="bg-gray-800 rounded-xl p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4 flex items-center gap-2">
                <i class="fas fa-timeline"></i>
                Timeline ao Vivo
            </h2>
            <div id="timeline" class="space-y-4 max-h-96 overflow-y-auto">
                <!-- Preenchido via JS -->
            </div>
        </div>

        <!-- Agents Status -->
        <div class="bg-gray-800 rounded-xl p-6 mb-8">
            <h2 class="text-xl font-semibold mb-4">Status dos Agentes</h2>
            <div id="agents-status" class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
                <!-- Preenchido via JS -->
            </div>
        </div>

        <!-- Recent Reports -->
        <div class="bg-gray-800 rounded-xl p-6">
            <h2 class="text-xl font-semibold mb-4">Relatórios Recentes</h2>
            <div id="recent-reports" class="space-y-3">
                <!-- Preenchido via JS -->
            </div>
        </div>
    </div>

    <script>
        async function loadData() {
            try {
                const response = await fetch('/api/v1/dashboard');
                const data = await response.json();                
                updateStats(data.stats);
                updateTimeline(data.timeline);
                updateAgents(data.agents);
                updateReports(data.reports);
            } catch (error) {
                console.error('Erro ao carregar dados:', error);
            }
        }

        function updateStats(stats) {
            document.getElementById('active-audits').textContent = stats.active_audits || 0;
            document.getElementById('avg-score').textContent = Math.round(stats.avg_health_score) || 0;
            document.getElementById('critical-issues').textContent = stats.critical_issues || 0;
            document.getElementById('avg-coverage').textContent = Math.round(stats.avg_coverage) || 0;
        }

        function updateTimeline(events) {
            const timelineEl = document.getElementById('timeline');
            timelineEl.innerHTML = events.slice(0, 20).map(event => `
                <div class="flex gap-4 items-start p-3 bg-gray-700 rounded-lg">
                    <div class="w-3 h-3 rounded-full ${
                        event.severity === 'critical' ? 'bg-red-500' :
                        event.severity === 'high' ? 'bg-orange-500' :
                        event.severity === 'medium' ? 'bg-yellow-500' : 'bg-green-500'
                    } mt-1.5"></div>
                    <div class="flex-1">
                        <div class="flex justify-between">
                            <span class="font-medium">${event.agent}</span>
                            <span class="text-xs text-gray-500">${new Date(event.timestamp).toLocaleTimeString()}</span>
                        </div>
                        <div class="text-sm text-gray-300">${event.action}</div>
                        <div class="text-xs text-gray-500">${event.event_type}</div>
                    </div>
                </div>
            `).join('');
        }

        function updateAgents(agents) {
            const agentsEl = document.getElementById('agents-status');
            agentsEl.innerHTML = Object.entries(agents).map(([name, status]) => `
                <div class="flex flex-col items-center p-3 bg-gray-700 rounded-lg">
                    <div class="w-4 h-4 rounded-full ${
                        status.running ? 'bg-green-500' : 'bg-red-500'
                    } mb-2"></div>
                    <div class="text-xs text-center">${name}</div>
                    <div class="text-xs text-gray-500">${status.status}</div>
                </div>
            `).join('');
        }
        function updateReports(reports) {
            const reportsEl = document.getElementById('recent-reports');
            reportsEl.innerHTML = reports.slice(0, 5).map(report => `
                <div class="flex justify-between items-center p-3 bg-gray-700 rounded">
                    <div>
                        <div class="font-medium">${report.repo}</div>
                        <div class="text-sm text-gray-400">${report.client} • ${new Date(report.completed_at).toLocaleDateString()}</div>
                    </div>
                    <div class="text-right">
                        <div class="text-amber-400 font-bold">${report.health_score}</div>
                        <div class="text-xs text-gray-500">${report.coverage}% coverage</div>
                    </div>
                </div>
            `).join('');
        }

        function refreshData() {
            loadData();
        }

        // Atualizar a cada 5 segundos
        setInterval(loadData, 5000);
        loadData(); // Carregar imediatamente
    </script>
</body>
</html>
'''

@app.route('/')
def dashboard():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/v1/dashboard')
def get_dashboard_data():
    """API endpoint para dados do dashboard"""
    conn = sqlite3.connect(DB_PATH)
    
    # Stats
    stats = {}
    
    # Auditorias ativas (últimas 24h)
    cutoff = (datetime.now() - timedelta(hours=24)).isoformat()
    active_audits = conn.execute("""
        SELECT COUNT(DISTINCT audit_id) FROM events 
        WHERE timestamp > ? AND event_type = 'audit_start'
    """, (cutoff,)).fetchone()[0]
    stats['active_audits'] = active_audits
    
    # Health scores dos relatórios    reports = list(Path("/root/selix/logs").glob("audit_*.json"))
    scores = []
    coverages = []
    
    for report_path in reports[-10:]:  # Últimos 10
        try:
            with open(report_path) as f:
                data = json.load(f)
                scores.append(data.get('health_score', 0))
                if 'results_by_agent' in data:
                    for agent_results in data['results_by_agent'].values():
                        if 'final_coverage' in agent_results:
                            coverages.append(agent_results['final_coverage'])
        except:
            continue
    
    stats['avg_health_score'] = sum(scores) / len(scores) if scores else 0
    stats['avg_coverage'] = sum(coverages) / len(coverages) if coverages else 0
    
    # Issues críticas (últimas 24h)
    critical_issues = conn.execute("""
        SELECT COUNT(*) FROM events 
        WHERE timestamp > ? AND severity = 'critical'
    """, (cutoff,)).fetchone()[0]
    stats['critical_issues'] = critical_issues
    
    # Timeline (últimos 50 eventos)
    timeline = conn.execute("""
        SELECT * FROM events 
        ORDER BY timestamp DESC 
        LIMIT 50
    """).fetchall()
    
    columns = [d[0] for d in conn.execute("PRAGMA table_info(events)").description]
    timeline = [dict(zip(columns, row)) for row in timeline]
    
    # Status dos agentes (últimos eventos por agente)
    agent_status = {}
    for event in timeline:
        agent = event['agent']
        if agent not in agent_status:
            agent_status[agent] = {
                'running': True,
                'status': 'active',
                'last_event': event['timestamp']
            }
    
    # Relatórios recentes
    recent_reports = []
    for report_path in reports[-5:]:        try:
            with open(report_path) as f:
                data = json.load(f)
                recent_reports.append({
                    'repo': data.get('repo_path', 'unknown'),
                    'client': data.get('client_id', 'default'),
                    'health_score': data.get('health_score', 0),
                    'coverage': data.get('results_by_agent', {}).get('QA', {}).get('final_coverage', 0),
                    'completed_at': data.get('completed_at', ''),
                    'audit_id': data.get('audit_id', '')[:8]
                })
        except:
            continue
    
    conn.close()
    
    return jsonify({
        'stats': stats,
        'timeline': timeline,
        'agents': agent_status,
        'reports': recent_reports
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=False)
