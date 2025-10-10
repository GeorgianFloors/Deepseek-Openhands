#!/usr/bin/env python3
"""
OpenHands on Port 7777 - Simple Demo Server
Just run: python openhands_7777_fixed.py
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import psutil
from datetime import datetime
import uuid
import threading
from typing import Dict, List, Optional, Any
from collections import deque

class SimpleMonitor:
    def __init__(self):
        self.activities = {}
        self._lock = threading.RLock()
        print("🔍 Simple monitoring system started")
    
    def start_activity(self, name: str, metadata: Dict = None):
        activity_id = str(uuid.uuid4())
        activity = {
            'id': activity_id,
            'name': name,
            'start_time': datetime.now(),
            'status': 'started',
            'metadata': metadata or {}
        }
        with self._lock:
            self.activities[activity_id] = activity
        return activity_id
    
    def end_activity(self, activity_id: str, status: str = 'completed'):
        with self._lock:
            if activity_id in self.activities:
                self.activities[activity_id]['status'] = status
                self.activities[activity_id]['end_time'] = datetime.now()
    
    def get_stats(self):
        with self._lock:
            total = len(self.activities)
            completed = len([a for a in self.activities.values() if a['status'] == 'completed'])
            active = len([a for a in self.activities.values() if a['status'] == 'started'])
            
            return {
                'total_activities': total,
                'completed_activities': completed,
                'active_activities': active,
                'cpu_usage': psutil.cpu_percent(),
                'memory_usage': psutil.virtual_memory().percent
            }

# Create monitor instance
monitor = SimpleMonitor()

# Create FastAPI app
app = FastAPI(title="OpenHands on Port 7777")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>OpenHands on Port 7777</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #0f0f23; color: white; }
            .container { max-width: 800px; margin: 0 auto; }
            .card { background: #1a1a2e; padding: 20px; margin: 20px 0; border-radius: 10px; border: 1px solid #2d2d4d; }
            .btn { background: #64ffda; color: #0f0f23; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; margin: 5px; }
            .status { color: #64ffda; font-weight: bold; }
            .monitor { background: #16213e; padding: 15px; border-radius: 5px; margin: 10px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 OpenHands Demo Server</h1>
            <p class="status">Running on port <strong>7777</strong></p>
            
            <div class="card">
                <h2>📊 Live Monitoring</h2>
                <div class="monitor" id="stats">
                    Loading monitoring statistics...
                </div>
                <button class="btn" onclick="refreshStats()">Refresh Stats</button>
                <button class="btn" onclick="testAgent()">Test Agent</button>
            </div>
            
            <div class="card">
                <h2>🔧 API Endpoints</h2>
                <ul>
                    <li><strong>GET /</strong> - This dashboard</li>
                    <li><strong>GET /health</strong> - Health check</li>
                    <li><strong>GET /monitoring/stats</strong> - Monitoring statistics</li>
                    <li><strong>POST /agent/execute</strong> - Execute agent task</li>
                </ul>
            </div>
        </div>
        
        <script>
        async function refreshStats() {
            const response = await fetch('/monitoring/stats');
            const data = await response.json();
            document.getElementById('stats').innerHTML = `
                <strong>Activities:</strong> ${data.total_activities} total, ${data.completed_activities} completed, ${data.active_activities} active<br>
                <strong>System:</strong> CPU: ${data.cpu_usage.toFixed(1)}%, Memory: ${data.memory_usage.toFixed(1)}%
            `;
        }
        
        async function testAgent() {
            const response = await fetch('/agent/execute', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({task: 'Test the monitoring system'})
            });
            const result = await response.json();
            alert('Agent executed: ' + result.result);
            refreshStats();
        }
        
        refreshStats();
        </script>
    </body>
    </html>
    """

@app.get("/health")
async def health():
    return {"status": "healthy", "port": 7777, "timestamp": datetime.now().isoformat()}

@app.get("/monitoring/stats")
async def monitoring_stats():
    return monitor.get_stats()

@app.post("/agent/execute")
async def execute_agent(task_data: Dict[str, Any]):
    activity_id = monitor.start_activity("Agent Execution", {"task": task_data.get('task', 'Unknown')})
    
    # Simulate agent work
    await asyncio.sleep(1)
    
    monitor.end_activity(activity_id, "completed")
    
    return {
        "status": "success",
        "result": f"Task completed: {task_data.get('task', 'Unknown')}",
        "activity_id": activity_id,
        "timestamp": datetime.now().isoformat()
    }

def main():
    print("🚀 Starting OpenHands on port 7777...")
    print("🌐 Dashboard: http://localhost:7777")
    print("🔧 Health: http://localhost:7777/health")
    print("📊 Monitoring: Active and collecting data")
    print("=" * 50)
    print("Press Ctrl+C to stop the server")
    
    # Use uvicorn.run with proper configuration
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=7777,
        log_level="info",
        access_log=True
    )

if __name__ == "__main__":
    main()