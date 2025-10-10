#!/usr/bin/env python3
"""
OpenHands Server on Port 7777 with Integrated Monitoring

This script runs a simplified version of OpenHands on port 7777 with
integrated monitoring capabilities.
"""

import asyncio
import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Import OpenHands components
from openhands.server.app import app as openhands_app
from openhands.monitoring import integration, monitor
from openhands.monitoring.server import MonitoringServer


class OpenHands7777Server:
    """Custom OpenHands server running on port 7777 with monitoring."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 7777):
        self.host = host
        self.port = port
        
        # Create main app
        self.app = FastAPI(
            title="OpenHands on Port 7777",
            description="OpenHands AI Agent Platform with Integrated Monitoring",
            version="1.0.0"
        )
        
        # Enable CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Setup routes
        self._setup_routes()
        
        # Enable monitoring
        integration.enable_monitoring(True)
        
    def _setup_routes(self):
        """Setup API routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>OpenHands on Port 7777</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .card { background: #f5f5f5; padding: 20px; margin: 10px 0; border-radius: 5px; }
                    .monitoring-link { color: #007bff; text-decoration: none; }
                    .monitoring-link:hover { text-decoration: underline; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 OpenHands Server</h1>
                    <p>Running on port <strong>7777</strong> with integrated monitoring</p>
                    
                    <div class="card">
                        <h2>📊 Monitoring Dashboard</h2>
                        <p>Access the real-time monitoring dashboard:</p>
                        <a href="/monitoring" class="monitoring-link" target="_blank">
                            Open Monitoring Dashboard
                        </a>
                    </div>
                    
                    <div class="card">
                        <h2>🔧 API Endpoints</h2>
                        <ul>
                            <li><strong>GET /health</strong> - Server health check</li>
                            <li><strong>GET /monitoring</strong> - Monitoring dashboard</li>
                            <li><strong>GET /api/monitoring/stats</strong> - Monitoring statistics</li>
                            <li><strong>POST /api/agent/execute</strong> - Execute agent task</li>
                        </ul>
                    </div>
                    
                    <div class="card">
                        <h2>🤖 Agent Demo</h2>
                        <p>Test the agent functionality:</p>
                        <form action="/api/agent/execute" method="post">
                            <input type="text" name="task" placeholder="Enter a task for the agent" style="width: 300px; padding: 8px;">
                            <button type="submit" style="padding: 8px 16px; background: #007bff; color: white; border: none; border-radius: 4px;">Execute</button>
                        </form>
                    </div>
                </div>
            </body>
            </html>
            """
        
        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "server": "OpenHands on Port 7777",
                "monitoring": "enabled",
                "timestamp": asyncio.get_event_loop().time()
            }
        
        @self.app.get("/monitoring", response_class=HTMLResponse)
        async def monitoring_dashboard():
            """Serve the monitoring dashboard."""
            # Read the monitoring dashboard HTML
            dashboard_path = "/workspace/OpenHands/openhands/monitoring/static/index.html"
            if os.path.exists(dashboard_path):
                with open(dashboard_path, 'r') as f:
                    return f.read()
            else:
                return """
                <html>
                <body>
                    <h1>Monitoring Dashboard</h1>
                    <p>Monitoring dashboard files not found. The monitoring system is still active.</p>
                    <p><a href="/api/monitoring/stats">View monitoring statistics</a></p>
                </body>
                </html>
                """
        
        @self.app.get("/api/monitoring/stats")
        async def monitoring_stats():
            """Get monitoring statistics."""
            return {
                "statistics": monitor.get_statistics(),
                "recent_activities": [
                    {
                        "name": activity.name,
                        "type": activity.type.value,
                        "status": activity.status.value,
                        "timestamp": activity.timestamp.isoformat(),
                        "duration": activity.duration
                    }
                    for activity in monitor.get_recent_activities(10)
                ],
                "system_metrics": [
                    {
                        "cpu_usage": metric.cpu_usage,
                        "memory_usage": metric.memory_usage,
                        "timestamp": metric.timestamp.isoformat()
                    }
                    for metric in monitor.get_system_metrics(5)
                ]
            }
        
        @self.app.post("/api/agent/execute")
        async def execute_agent_task(task: str):
            """Execute a simple agent task with monitoring."""
            try:
                # Simulate agent execution with monitoring
                with integration.hooks.monitor_agent_execution("demo_agent", task):
                    # Simulate some work
                    await asyncio.sleep(1)
                    
                    # Simulate tool usage
                    with integration.hooks.monitor_tool_execution("demo_tool", {"task": task}):
                        await asyncio.sleep(0.5)
                    
                    # Update metrics
                    monitor.update_agent_metrics("demo_agent", {
                        "task_completed": True,
                        "response_time": 1.5,
                        "tokens_used": len(task) * 2
                    })
                
                return {
                    "status": "success",
                    "task": task,
                    "result": f"Task '{task}' completed successfully",
                    "monitoring": "Activity tracked in monitoring system"
                }
                
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Agent execution failed: {str(e)}")
    
    async def start(self):
        """Start the server."""
        print(f"🚀 Starting OpenHands Server on port {self.port}")
        print(f"📊 Monitoring dashboard: http://{self.host}:{self.port}/monitoring")
        print(f"🔧 Health check: http://{self.host}:{self.port}/health")
        print("⏳ Starting server...")
        
        # Start the monitoring server on a different port
        monitoring_server = MonitoringServer(monitor, "0.0.0.0", 7778)
        
        # Start both servers
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    async def stop(self):
        """Stop the server."""
        integration.enable_monitoring(False)
        print("🛑 Server stopped")


async def main():
    """Main function to run the server."""
    server = OpenHands7777Server("0.0.0.0", 7777)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n⏹️  Server interrupted by user")
    finally:
        await server.stop()


if __name__ == "__main__":
    print("=" * 60)
    print("🤖 OpenHands Server - Port 7777")
    print("=" * 60)
    print("This server demonstrates OpenHands with integrated monitoring")
    print("Features:")
    print("• OpenHands API endpoints")
    print("• Real-time monitoring dashboard")
    print("• Agent execution with activity tracking")
    print("• System resource monitoring")
    print("=" * 60)
    
    asyncio.run(main())