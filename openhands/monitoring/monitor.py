"""Core monitoring system for OpenHands."""

import asyncio
import uuid
import time
import psutil
import threading
from typing import Dict, List, Optional, Callable, Any
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

from openhands.monitoring.types import (
    Activity, ActivityType, ActivityStatus, 
    SystemMetrics, AgentMetrics, VisualizationConfig
)


class ActivityMonitor:
    """Monitors and tracks activities in real-time."""
    
    def __init__(self, config: Optional[VisualizationConfig] = None):
        self.config = config or VisualizationConfig()
        self.activities: Dict[str, Activity] = {}
        self.activities_history: List[Activity] = []
        self.system_metrics: List[SystemMetrics] = []
        self.agent_metrics: Dict[str, AgentMetrics] = {}
        
        # Real-time subscribers
        self.subscribers: List[Callable[[Activity], None]] = []
        self.metrics_subscribers: List[Callable[[SystemMetrics], None]] = []
        
        # Threading and async
        self._lock = threading.RLock()
        self._executor = ThreadPoolExecutor(max_workers=4)
        self._monitoring_task: Optional[asyncio.Task] = None
        self._is_monitoring = False
        
        # Statistics
        self.stats = {
            'activities_started': 0,
            'activities_completed': 0,
            'activities_failed': 0,
            'total_duration': 0.0
        }
    
    def start_monitoring(self) -> None:
        """Start the monitoring system."""
        if self._is_monitoring:
            return
        
        self._is_monitoring = True
        
        if self.config.enable_resource_monitoring:
            # Start system metrics collection in background thread
            self._monitoring_task = asyncio.create_task(self._collect_system_metrics())
        
        print("OpenHands monitoring system started")
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring system."""
        self._is_monitoring = False
        
        if self._monitoring_task:
            self._monitoring_task.cancel()
        
        self._executor.shutdown(wait=False)
        print("OpenHands monitoring system stopped")
    
    def start_activity(
        self, 
        activity_type: ActivityType, 
        name: str,
        metadata: Optional[Dict[str, Any]] = None,
        parent_id: Optional[str] = None
    ) -> str:
        """Start tracking a new activity."""
        if not self.config.enabled:
            return ""
        
        activity_id = str(uuid.uuid4())
        activity = Activity(
            id=activity_id,
            type=activity_type,
            name=name,
            timestamp=datetime.now(),
            status=ActivityStatus.STARTED,
            metadata=metadata or {},
            parent_id=parent_id
        )
        
        with self._lock:
            self.activities[activity_id] = activity
            self.stats['activities_started'] += 1
        
        # Notify subscribers
        self._notify_subscribers(activity)
        
        return activity_id
    
    def end_activity(
        self, 
        activity_id: str, 
        status: ActivityStatus = ActivityStatus.COMPLETED,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """End an activity with the given status."""
        if not self.config.enabled or not activity_id:
            return
        
        with self._lock:
            if activity_id not in self.activities:
                return
            
            activity = self.activities[activity_id]
            activity.status = status
            activity.duration = (datetime.now() - activity.timestamp).total_seconds()
            
            if metadata:
                activity.metadata.update(metadata)
            
            # Move to history
            self.activities_history.append(activity)
            del self.activities[activity_id]
            
            # Update statistics
            if status == ActivityStatus.COMPLETED:
                self.stats['activities_completed'] += 1
                self.stats['total_duration'] += activity.duration
            elif status == ActivityStatus.FAILED:
                self.stats['activities_failed'] += 1
            
            # Trim history if needed
            if len(self.activities_history) > self.config.max_history:
                self.activities_history = self.activities_history[-self.config.max_history:]
        
        # Notify subscribers
        self._notify_subscribers(activity)
    
    def add_child_activity(self, parent_id: str, child_id: str) -> None:
        """Add a child activity to a parent activity."""
        if not self.config.enabled:
            return
        
        with self._lock:
            if parent_id in self.activities and child_id in self.activities:
                self.activities[parent_id].children.append(child_id)
    
    def update_agent_metrics(self, agent_name: str, metrics_update: Dict[str, Any]) -> None:
        """Update metrics for a specific agent."""
        if not self.config.enabled or not self.config.enable_agent_metrics:
            return
        
        with self._lock:
            if agent_name not in self.agent_metrics:
                self.agent_metrics[agent_name] = AgentMetrics(
                    agent_name=agent_name,
                    tasks_completed=0,
                    tasks_failed=0,
                    average_response_time=0.0,
                    tool_usage={},
                    token_usage=0
                )
            
            metrics = self.agent_metrics[agent_name]
            
            if 'task_completed' in metrics_update:
                metrics.tasks_completed += 1
            if 'task_failed' in metrics_update:
                metrics.tasks_failed += 1
            if 'response_time' in metrics_update:
                # Update moving average
                total_tasks = metrics.tasks_completed + metrics.tasks_failed
                if total_tasks > 0:
                    metrics.average_response_time = (
                        (metrics.average_response_time * (total_tasks - 1) + 
                         metrics_update['response_time']) / total_tasks
                    )
            if 'tool_used' in metrics_update:
                tool_name = metrics_update['tool_used']
                metrics.tool_usage[tool_name] = metrics.tool_usage.get(tool_name, 0) + 1
            if 'tokens_used' in metrics_update:
                metrics.token_usage += metrics_update['tokens_used']
    
    def subscribe_to_activities(self, callback: Callable[[Activity], None]) -> None:
        """Subscribe to activity updates."""
        self.subscribers.append(callback)
    
    def subscribe_to_metrics(self, callback: Callable[[SystemMetrics], None]) -> None:
        """Subscribe to system metrics updates."""
        self.metrics_subscribers.append(callback)
    
    def get_recent_activities(self, limit: int = 50) -> List[Activity]:
        """Get recent activities."""
        with self._lock:
            return self.activities_history[-limit:]
    
    def get_active_activities(self) -> List[Activity]:
        """Get currently active activities."""
        with self._lock:
            return list(self.activities.values())
    
    def get_system_metrics(self, limit: int = 100) -> List[SystemMetrics]:
        """Get recent system metrics."""
        with self._lock:
            return self.system_metrics[-limit:]
    
    def get_agent_metrics(self) -> Dict[str, AgentMetrics]:
        """Get agent metrics."""
        with self._lock:
            return self.agent_metrics.copy()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get monitoring statistics."""
        with self._lock:
            stats = self.stats.copy()
            stats['active_activities'] = len(self.activities)
            stats['total_activities'] = len(self.activities_history)
            stats['system_metrics_count'] = len(self.system_metrics)
            stats['agents_monitored'] = len(self.agent_metrics)
            
            if stats['activities_completed'] > 0:
                stats['average_duration'] = (
                    stats['total_duration'] / stats['activities_completed']
                )
            else:
                stats['average_duration'] = 0.0
            
            return stats
    
    async def _collect_system_metrics(self) -> None:
        """Continuously collect system metrics."""
        while self._is_monitoring:
            try:
                # Get system metrics
                cpu_percent = psutil.cpu_percent(interval=None)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                net_io = psutil.net_io_counters()
                
                metrics = SystemMetrics(
                    timestamp=datetime.now(),
                    cpu_usage=cpu_percent,
                    memory_usage=memory.used / (1024 * 1024),  # Convert to MB
                    disk_usage=disk.used / (1024 * 1024),  # Convert to MB
                    network_io={
                        'bytes_sent': net_io.bytes_sent if net_io else 0,
                        'bytes_recv': net_io.bytes_recv if net_io else 0
                    },
                    active_processes=len(psutil.pids())
                )
                
                with self._lock:
                    self.system_metrics.append(metrics)
                    # Trim history
                    if len(self.system_metrics) > self.config.max_history:
                        self.system_metrics = self.system_metrics[-self.config.max_history:]
                
                # Notify metrics subscribers
                for subscriber in self.metrics_subscribers:
                    try:
                        subscriber(metrics)
                    except Exception:
                        pass  # Don't let subscriber errors break monitoring
                
                await asyncio.sleep(self.config.update_interval)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                if self.config.enable_detailed_logging:
                    print(f"Error collecting system metrics: {e}")
                await asyncio.sleep(1)  # Wait before retrying
    
    def _notify_subscribers(self, activity: Activity) -> None:
        """Notify all activity subscribers."""
        for subscriber in self.subscribers:
            try:
                subscriber(activity)
            except Exception:
                pass  # Don't let subscriber errors break monitoring