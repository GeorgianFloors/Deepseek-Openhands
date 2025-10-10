#!/usr/bin/env python3
"""
Simple OpenHands Demo Server on Port 7777

This demonstrates the core OpenHands functionality with monitoring
without requiring the full frontend build.
"""

import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

# Import monitoring system
from openhands.monitoring import integration, monitor
from openhands.monitoring.types import ActivityType, ActivityStatus


class SimpleOpenHandsServer:
    """Simple OpenHands server demonstrating core functionality."""
    
    def __init__(self, port: int = 7777):
        self.port = port
        
        # Create FastAPI app
        self.app = FastAPI(title="OpenHands Demo", version="1.0.0")
        
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
        """Setup demo routes."""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            return """
            <!DOCTYPE html>
            <html>
            <head>
                <title>OpenHands Demo - Port 7777</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #0f0f23; color: white; }
                    .container { max-width: 800px; margin: 0 auto; }
                    .card { background: #1a1a2e; padding: 20px; margin: 20px 0; border-radius: 10px; border: 1px solid #2d2d4d; }
                    .btn { background: #64ffda; color: #0f0f23; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; text-decoration: none; display: inline-block; }
                    .btn:hover { background: #4fd3b0; }
                    .status { color: #64ffda; font-weight: bold; }
                    .monitor { background: #16213e; padding: 15px; border-radius: 5px; margin: 10px 0; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🚀 OpenHands Demo Server</h1>
                    <p class="status">Running on port <strong>7777</strong> with real-time monitoring</p>
                    
                    <div class="card">
                        <h2>📊 Live Monitoring</h2>
                        <div class="monitor">
                            <div id="stats">Loading monitoring statistics...</div>
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
                            <li><strong>GET /monitoring/activities</strong> - Recent activities</li>
                        </ul>
                    </div>
                </div>
                
                <script>
                async function refreshStats() {
                    const response = await fetch('/monitoring/stats');
                    const data = await response.json();
                    document.getElementById('stats').innerHTML = `
                        <strong>Activities:</strong> ${data.statistics.activities_started} started, 
                        ${data.statistics.activities_completed} completed<br>
                        <strong>Active:</strong> ${data.statistics.active_activities} activities<br>
                        <strong>Agents:</strong> ${data.statistics.agents_monitored} monitored
                    `;
                }
                
                async function testAgent() {
                    const task = prompt('Enter a task for the agent:');
                    if (task) {
                        const response = await fetch('/agent/execute', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ task: task })
                        });
                        const result = await response.json();
                        alert('Agent result: ' + result.result);
                        refreshStats();
                    }
                }
                
                // Load initial stats
                refreshStats();
                </script>
            </body>
            </html>
            """
        
        @self.app.get("/health")
        async def health():
            return {
                "status": "healthy",
                "server": "OpenHands Demo",
                "port": self.port,
                "monitoring": "active"
            }
        
        @self.app.get("/monitoring/stats")
        async def monitoring_stats():
            """Get monitoring statistics."""
            stats = monitor.get_statistics()
            return {
                "statistics": stats,
                "timestamp": asyncio.get_event_loop().time()
            }
        
        @self.app.get("/monitoring/activities")
        async def monitoring_activities():
            """Get recent activities."""
            activities = monitor.get_recent_activities(20)
            return {
                "activities": [
                    {
                        "id": activity.id,
                        "name": activity.name,
                        "type": activity.type.value,
                        "status": activity.status.value,
                        "timestamp": activity.timestamp.isoformat(),
                        "duration": activity.duration,
                        "metadata": activity.metadata
                    }
                    for activity in activities
                ]
            }
        
        @self.app.post("/agent/execute")
        async def execute_agent_task(task: dict):
            """Execute a demo agent task."""
            task_text = task.get("task", "Test task")
            
            # Track the agent execution
            activity_id = monitor.start_activity(
                ActivityType.AGENT_EXECUTION,
                f"Demo Agent: {task_text}",
                {"agent": "demo_agent", "task": task_text}
            )
            
            try:
                # Simulate agent thinking
                await asyncio.sleep(1)
                
                # Simulate tool usage
                tool_id = monitor.start_activity(
                    ActivityType.TOOL_EXECUTION,
                    "Demo Tool",
                    {"tool": "demo_tool", "task": task_text},
                    parent_id=activity_id
                )
                await asyncio.sleep(0.5)
                monitor.end_activity(tool_id, ActivityStatus.COMPLETED)
                
                # Update agent metrics
                monitor.update_agent_metrics("demo_agent", {
                    "task_completed": True,
                    "response_time": 1.5,
                    "tool_used": "demo_tool"
                })
                
                # Complete the main activity
                monitor.end_activity(activity_id, ActivityStatus.COMPLETED, {
                    "result": "success",
                    "generated_content": f"I've processed your task: '{task_text}'. This is a demo of OpenHands monitoring."
                })
                
                return {
                    "status": "success",
                    "task": task_text,
                    "result": f"Task completed successfully. Check the monitoring system for details.",
                    "activity_id": activity_id
                }
                
            except Exception as e:
                monitor.end_activity(activity_id, ActivityStatus.FAILED, {"error": str(e)})
                raise HTTPException(status_code=500, detail=f"Agent failed: {str(e)}")
        
        @self.app.post("/monitoring/test")
        async def test_monitoring():
            """Test the monitoring system."""
            # Generate test activities
            for i in range(5):
                activity_id = monitor.start_activity(
                    ActivityType.AGENT_EXECUTION,
                    f"Test Activity {i+1}",
                    {"test": True, "iteration": i+1}
                )
                await asyncio.sleep(0.1)
                monitor.end_activity(activity_id, ActivityStatus.COMPLETED)
            
            return {"status": "test_completed", "activities_generated": 5}
    
    async def start(self):
        """Start the server."""
        print(f"🚀 Starting OpenHands Demo Server on port {self.port}")
        print(f"🌐 Dashboard: http://localhost:{self.port}")
        print(f"🔧 Health: http://localhost:{self.port}/health")
        print("📊 Monitoring: Active and collecting data")
        print("=" * 50)
        
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=self.port,
            log_level="info"
        )
        
        server = uvicorn.Server(config)
        await server.serve()
    
    async def stop(self):
        """Stop the server."""
        integration.enable_monitoring(False)


async def main():
    """Main function."""
    server = SimpleOpenHandsServer(7777)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n⏹️  Server stopped by user")
    finally:
        await server.stop()


if __name__ == "__main__":
    print("🤖 OpenHands Demo Server - Port 7777")
    print("Demonstrating AI agent monitoring and execution")
    asyncio.run(main())