#!/usr/bin/env python3
"""
OpenHands Enhanced with Monitoring

This script runs the ACTUAL OpenHands system with integrated monitoring capabilities.
It preserves all the original OpenHands functionality while adding monitoring features.
"""

import os
import sys
import asyncio
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Import the actual OpenHands server
from openhands.server.listen import app as openhands_app

# Import monitoring components
from openhands.monitoring import integration, monitor
from openhands.monitoring.server import MonitoringServer


class OpenHandsEnhanced:
    """Enhanced OpenHands server with monitoring capabilities."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 3000, monitoring_port: int = 7778):
        self.host = host
        self.port = port
        self.monitoring_port = monitoring_port
        
        # Use the actual OpenHands app as base
        self.app = openhands_app
        
        # Enable monitoring
        integration.enable_monitoring(True)
        
        # Add monitoring routes to the existing OpenHands app
        self._add_monitoring_routes()
        
    def _add_monitoring_routes(self):
        """Add monitoring routes to the existing OpenHands app."""
        
        @self.app.get("/monitoring")
        async def monitoring_dashboard():
            """Serve the monitoring dashboard."""
            dashboard_path = "/workspace/Deepseek-Openhands/openhands/monitoring/static/index.html"
            if os.path.exists(dashboard_path):
                with open(dashboard_path, 'r') as f:
                    return f.read()
            else:
                return {
                    "message": "Monitoring dashboard available at separate port",
                    "monitoring_url": f"http://{self.host}:{self.monitoring_port}"
                }
        
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
    
    async def start(self):
        """Start both the OpenHands server and monitoring server."""
        print("🚀 Starting OpenHands Enhanced Server")
        print(f"📱 OpenHands API: http://{self.host}:{self.port}")
        print(f"📊 Monitoring Dashboard: http://{self.host}:{self.monitoring_port}")
        print(f"🔧 Health Check: http://{self.host}:{self.port}/health")
        print("=" * 60)
        print("Features:")
        print("• Full OpenHands AI Agent Platform")
        print("• Real-time Monitoring Dashboard")
        print("• Agent Execution Tracking")
        print("• System Resource Monitoring")
        print("• All Original OpenHands Tools & Capabilities")
        print("=" * 60)
        
        # Start monitoring server on separate port
        monitoring_server = MonitoringServer(monitor, self.host, self.monitoring_port)
        monitoring_task = asyncio.create_task(monitoring_server.start())
        
        # Start the actual OpenHands server
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
    """Main function to run the enhanced server."""
    server = OpenHandsEnhanced("0.0.0.0", 3000, 7778)
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n⏹️  Server interrupted by user")
    finally:
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())