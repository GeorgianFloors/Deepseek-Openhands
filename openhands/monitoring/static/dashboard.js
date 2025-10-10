"""JavaScript for the OpenHands monitoring dashboard."""

class OpenHandsDashboard {
    constructor() {
        this.ws = null;
        this.isConnected = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        // Data storage
        this.activities = [];
        this.metrics = [];
        this.agentMetrics = {};
        this.statistics = {};
        
        // Charts
        this.resourceChart = null;
        this.toolUsageChart = null;
        this.detailedResourceChart = null;
        this.networkChart = null;
        
        this.init();
    }
    
    init() {
        this.connectWebSocket();
        this.setupCharts();
        this.setupEventListeners();
    }
    
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        try {
            this.ws = new WebSocket(wsUrl);
            
            this.ws.onopen = () => {
                console.log('Connected to OpenHands monitoring server');
                this.isConnected = true;
                this.reconnectAttempts = 0;
                this.updateConnectionStatus(true);
            };
            
            this.ws.onmessage = (event) => {
                this.handleMessage(JSON.parse(event.data));
            };
            
            this.ws.onclose = () => {
                console.log('Disconnected from OpenHands monitoring server');
                this.isConnected = false;
                this.updateConnectionStatus(false);
                this.attemptReconnect();
            };
            
            this.ws.onerror = (error) => {
                console.error('WebSocket error:', error);
            };
            
        } catch (error) {
            console.error('Failed to connect to WebSocket:', error);
            this.attemptReconnect();
        }
    }
    
    attemptReconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
            
            console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`);
            
            setTimeout(() => {
                this.connectWebSocket();
            }, delay);
        } else {
            console.error('Max reconnection attempts reached');
        }
    }
    
    handleMessage(message) {
        switch (message.type) {
            case 'initial_state':
                this.handleInitialState(message.data);
                break;
            case 'activity_update':
                this.handleActivityUpdate(message.data);
                break;
            case 'metrics_update':
                this.handleMetricsUpdate(message.data);
                break;
            default:
                console.log('Unknown message type:', message.type);
        }
    }
    
    handleInitialState(data) {
        this.activities = data.activities || [];
        this.metrics = data.metrics || [];
        this.agentMetrics = data.agent_metrics || {};
        this.statistics = data.statistics || {};
        
        this.updateDashboard();
    }
    
    handleActivityUpdate(activity) {
        // Add new activity to the beginning of the list
        this.activities.unshift(activity);
        
        // Keep only the last 50 activities
        if (this.activities.length > 50) {
            this.activities = this.activities.slice(0, 50);
        }
        
        this.updateActivitiesList();
    }
    
    handleMetricsUpdate(metric) {
        this.metrics.push(metric);
        
        // Keep only the last 100 metrics
        if (this.metrics.length > 100) {
            this.metrics = this.metrics.slice(-100);
        }
        
        this.updateMetricsDisplay();
        this.updateCharts();
    }
    
    updateDashboard() {
        this.updateMetricsDisplay();
        this.updateActivitiesList();
        this.updateAgentMetrics();
        this.updateCharts();
    }
    
    updateMetricsDisplay() {
        if (this.metrics.length > 0) {
            const latest = this.metrics[this.metrics.length - 1];
            
            document.getElementById('cpuUsage').textContent = `${latest.cpu_usage.toFixed(1)}%`;
            document.getElementById('memoryUsage').textContent = `${latest.memory_usage.toFixed(0)} MB`;
            document.getElementById('diskUsage').textContent = `${latest.disk_usage.toFixed(0)} MB`;
            document.getElementById('activeProcesses').textContent = latest.active_processes;
        }
        
        // Update statistics
        if (this.statistics.activities_completed > 0) {
            const successRate = (this.statistics.activities_completed / 
                (this.statistics.activities_completed + this.statistics.activities_failed)) * 100;
            
            document.getElementById('totalTasks').textContent = this.statistics.total_activities || 0;
            document.getElementById('successRate').textContent = `${successRate.toFixed(1)}%`;
            document.getElementById('avgResponse').textContent = `${(this.statistics.average_duration || 0).toFixed(2)}s`;
            document.getElementById('activeAgents').textContent = this.statistics.agents_monitored || 0;
        }
    }
    
    updateActivitiesList() {
        const container = document.getElementById('activitiesList');
        
        if (this.activities.length === 0) {
            container.innerHTML = `
                <div class="activity-item">
                    <div class="activity-header">
                        <span class="activity-name">No activities yet</span>
                        <span class="activity-type">SYSTEM</span>
                    </div>
                    <div class="activity-details">
                        Waiting for agent activities...
                    </div>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.activities.map(activity => `
            <div class="activity-item">
                <div class="activity-header">
                    <span class="activity-name">${this.escapeHtml(activity.name)}</span>
                    <span class="activity-type">${activity.type.toUpperCase()}</span>
                </div>
                <div class="activity-details">
                    <span class="status-${activity.status}">${activity.status.toUpperCase()}</span>
                    ${activity.duration ? ` • ${activity.duration.toFixed(2)}s` : ''}
                    • ${new Date(activity.timestamp).toLocaleTimeString()}
                </div>
                ${activity.metadata && Object.keys(activity.metadata).length > 0 ? 
                    `<div class="activity-details" style="margin-top: 5px; font-size: 0.8rem;">
                        ${JSON.stringify(activity.metadata)}
                    </div>` : ''
                }
            </div>
        `).join('');
    }
    
    updateAgentMetrics() {
        const container = document.getElementById('agentMetrics');
        
        if (Object.keys(this.agentMetrics).length === 0) {
            container.innerHTML = '<div class="agent-metric">No agent data yet</div>';
            return;
        }
        
        container.innerHTML = Object.entries(this.agentMetrics).map(([name, metrics]) => `
            <div class="agent-metric">
                <div style="font-weight: bold; color: #64ffda;">${this.escapeHtml(name)}</div>
                <div>Completed: ${metrics.tasks_completed}</div>
                <div>Failed: ${metrics.tasks_failed}</div>
                <div>Avg Time: ${metrics.average_response_time.toFixed(2)}s</div>
                <div>Tokens: ${metrics.token_usage}</div>
            </div>
        `).join('');
    }
    
    setupCharts() {
        // Resource usage chart
        this.resourceChart = new Chart(
            document.getElementById('resourceChart').getContext('2d'),
            {
                type: 'doughnut',
                data: {
                    labels: ['CPU', 'Memory', 'Disk'],
                    datasets: [{
                        data: [0, 0, 0],
                        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#ffffff' }
                        }
                    }
                }
            }
        );
        
        // Tool usage chart
        this.toolUsageChart = new Chart(
            document.getElementById('toolUsageChart').getContext('2d'),
            {
                type: 'bar',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Tool Usage',
                        data: [],
                        backgroundColor: '#64ffda'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#ffffff' }
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: { color: '#ffffff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        x: {
                            ticks: { color: '#ffffff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            }
        );
        
        // Detailed resource chart
        this.detailedResourceChart = new Chart(
            document.getElementById('detailedResourceChart').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'CPU %',
                            data: [],
                            borderColor: '#FF6384',
                            tension: 0.1
                        },
                        {
                            label: 'Memory MB',
                            data: [],
                            borderColor: '#36A2EB',
                            tension: 0.1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#ffffff' }
                        }
                    },
                    scales: {
                        y: {
                            ticks: { color: '#ffffff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        x: {
                            ticks: { color: '#ffffff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            }
        );
        
        // Network chart
        this.networkChart = new Chart(
            document.getElementById('networkChart').getContext('2d'),
            {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: 'Bytes Sent',
                            data: [],
                            borderColor: '#4CAF50',
                            tension: 0.1
                        },
                        {
                            label: 'Bytes Received',
                            data: [],
                            borderColor: '#2196F3',
                            tension: 0.1
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: { color: '#ffffff' }
                        }
                    },
                    scales: {
                        y: {
                            ticks: { color: '#ffffff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        },
                        x: {
                            ticks: { color: '#ffffff' },
                            grid: { color: 'rgba(255,255,255,0.1)' }
                        }
                    }
                }
            }
        );
    }
    
    updateCharts() {
        if (this.metrics.length === 0) return;
        
        // Update resource chart
        const latest = this.metrics[this.metrics.length - 1];
        this.resourceChart.data.datasets[0].data = [
            latest.cpu_usage,
            latest.memory_usage / 100, // Scale for visualization
            latest.disk_usage / 1000   // Scale for visualization
        ];
        this.resourceChart.update();
        
        // Update detailed resource chart (last 20 points)
        const recentMetrics = this.metrics.slice(-20);
        this.detailedResourceChart.data.labels = recentMetrics.map((_, i) => i);
        this.detailedResourceChart.data.datasets[0].data = recentMetrics.map(m => m.cpu_usage);
        this.detailedResourceChart.data.datasets[1].data = recentMetrics.map(m => m.memory_usage);
        this.detailedResourceChart.update();
        
        // Update network chart
        this.networkChart.data.labels = recentMetrics.map((_, i) => i);
        this.networkChart.data.datasets[0].data = recentMetrics.map(m => m.network_io.bytes_sent / 1024);
        this.networkChart.data.datasets[1].data = recentMetrics.map(m => m.network_io.bytes_recv / 1024);
        this.networkChart.update();
        
        // Update tool usage chart from agent metrics
        const toolUsage = {};
        Object.values(this.agentMetrics).forEach(metrics => {
            Object.entries(metrics.tool_usage || {}).forEach(([tool, count]) => {
                toolUsage[tool] = (toolUsage[tool] || 0) + count;
            });
        });
        
        const tools = Object.keys(toolUsage).slice(0, 10); // Top 10 tools
        this.toolUsageChart.data.labels = tools;
        this.toolUsageChart.data.datasets[0].data = tools.map(tool => toolUsage[tool]);
        this.toolUsageChart.update();
    }
    
    updateConnectionStatus(connected) {
        const statusElement = document.getElementById('connectionStatus');
        if (connected) {
            statusElement.textContent = 'Connected';
            statusElement.className = 'connection-status connected';
        } else {
            statusElement.textContent = 'Disconnected';
            statusElement.className = 'connection-status disconnected';
        }
    }
    
    setupEventListeners() {
        // Keep connection alive
        setInterval(() => {
            if (this.isConnected && this.ws) {
                this.ws.send('ping');
            }
        }, 30000);
        
        // Handle page visibility changes
        document.addEventListener('visibilitychange', () => {
            if (!document.hidden && !this.isConnected) {
                this.connectWebSocket();
            }
        });
    }
    
    escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
}

// Initialize dashboard when page loads
document.addEventListener('DOMContentLoaded', () => {
    new OpenHandsDashboard();
});