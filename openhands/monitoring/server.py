"""WebSocket server for real-time monitoring visualization."""

import asyncio
import json
import logging
from typing import Dict, Any, Set
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from openhands.monitoring.monitor import ActivityMonitor
from openhands.monitoring.types import Activity, SystemMetrics


class ConnectionManager:
    """Manages WebSocket connections."""
    
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.add(connection)
        
        # Remove disconnected connections
        for connection in disconnected:
            self.active_connections.remove(connection)


class MonitoringServer:
    """Monitoring server that provides real-time data to visualization clients."""
    
    def __init__(self, monitor: ActivityMonitor, host: str = "0.0.0.0", port: int = 8000):
        self.monitor = monitor
        self.host = host
        self.port = port
        self.manager = ConnectionManager()
        self.app = FastAPI(title="OpenHands Monitoring")
        
        # Setup routes
        self._setup_routes()
        
        # Subscribe to monitor events
        self.monitor.subscribe_to_activities(self._on_activity_update)
        self.monitor.subscribe_to_metrics(self._on_metrics_update)
    
    def _setup_routes(self):
        """Setup FastAPI routes."""
        
        @self.app.get("/")
        async def get_dashboard():
            return FileResponse("openhands/monitoring/static/index.html")
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.manager.connect(websocket)
            try:
                # Send initial data
                await self._send_initial_data(websocket)
                
                # Keep connection alive
                while True:
                    await websocket.receive_text()
                    
            except WebSocketDisconnect:
                self.manager.disconnect(websocket)
        
        @self.app.get("/api/activities")
        async def get_activities(limit: int = 50):
            activities = self.monitor.get_recent_activities(limit)
            return {
                "activities": [self._serialize_activity(activity) for activity in activities]
            }
        
        @self.app.get("/api/active-activities")
        async def get_active_activities():
            activities = self.monitor.get_active_activities()
            return {
                "activities": [self._serialize_activity(activity) for activity in activities]
            }
        
        @self.app.get("/api/metrics")
        async def get_metrics(limit: int = 100):
            metrics = self.monitor.get_system_metrics(limit)
            return {
                "metrics": [self._serialize_metrics(metric) for metric in metrics]
            }
        
        @self.app.get("/api/agent-metrics")
        async def get_agent_metrics():
            metrics = self.monitor.get_agent_metrics()
            return {
                "agent_metrics": {
                    name: self._serialize_agent_metrics(metric) 
                    for name, metric in metrics.items()
                }
            }
        
        @self.app.get("/api/statistics")
        async def get_statistics():
            return self.monitor.get_statistics()
    
    async def _send_initial_data(self, websocket: WebSocket):
        """Send initial data to a new connection."""
        # Send current state
        activities = self.monitor.get_recent_activities(50)
        active_activities = self.monitor.get_active_activities()
        metrics = self.monitor.get_system_metrics(100)
        agent_metrics = self.monitor.get_agent_metrics()
        statistics = self.monitor.get_statistics()
        
        initial_data = {
            "type": "initial_state",
            "data": {
                "activities": [self._serialize_activity(a) for a in activities],
                "active_activities": [self._serialize_activity(a) for a in active_activities],
                "metrics": [self._serialize_metrics(m) for m in metrics],
                "agent_metrics": {
                    name: self._serialize_agent_metrics(m) 
                    for name, m in agent_metrics.items()
                },
                "statistics": statistics
            }
        }
        
        await self.manager.send_personal_message(
            json.dumps(initial_data), websocket
        )
    
    def _on_activity_update(self, activity: Activity):
        """Handle activity updates from monitor."""
        message = {
            "type": "activity_update",
            "data": self._serialize_activity(activity)
        }
        
        asyncio.create_task(self.manager.broadcast(json.dumps(message)))
    
    def _on_metrics_update(self, metrics: SystemMetrics):
        """Handle metrics updates from monitor."""
        message = {
            "type": "metrics_update",
            "data": self._serialize_metrics(metrics)
        }
        
        asyncio.create_task(self.manager.broadcast(json.dumps(message)))
    
    def _serialize_activity(self, activity: Activity) -> Dict[str, Any]:
        """Serialize activity for JSON transmission."""
        return {
            "id": activity.id,
            "type": activity.type.value,
            "name": activity.name,
            "timestamp": activity.timestamp.isoformat(),
            "status": activity.status.value,
            "metadata": activity.metadata,
            "duration": activity.duration,
            "parent_id": activity.parent_id,
            "children": activity.children
        }
    
    def _serialize_metrics(self, metrics: SystemMetrics) -> Dict[str, Any]:
        """Serialize system metrics for JSON transmission."""
        return {
            "timestamp": metrics.timestamp.isoformat(),
            "cpu_usage": metrics.cpu_usage,
            "memory_usage": metrics.memory_usage,
            "disk_usage": metrics.disk_usage,
            "network_io": metrics.network_io,
            "active_processes": metrics.active_processes
        }
    
    def _serialize_agent_metrics(self, metrics: Any) -> Dict[str, Any]:
        """Serialize agent metrics for JSON transmission."""
        return {
            "agent_name": metrics.agent_name,
            "tasks_completed": metrics.tasks_completed,
            "tasks_failed": metrics.tasks_failed,
            "average_response_time": metrics.average_response_time,
            "tool_usage": metrics.tool_usage,
            "token_usage": metrics.token_usage
        }
    
    async def start(self):
        """Start the monitoring server."""
        import uvicorn
        
        # Start the monitor
        self.monitor.start_monitoring()
        
        # Start the server
        config = uvicorn.Config(
            self.app, 
            host=self.host, 
            port=self.port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        
        print(f"OpenHands monitoring server starting on http://{self.host}:{self.port}")
        await server.serve()
    
    async def stop(self):
        """Stop the monitoring server."""
        self.monitor.stop_monitoring()