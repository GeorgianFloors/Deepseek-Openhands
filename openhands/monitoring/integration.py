"""Integration module for monitoring OpenHands components."""

import asyncio
import inspect
from typing import Dict, Any, Callable
from functools import wraps

from openhands.monitoring.types import ActivityType


class MonitoringIntegration:
    """Integrates monitoring with OpenHands components."""
    
    def __init__(self):
        from openhands.monitoring import monitor, hooks
        self.monitor = monitor
        self.hooks = hooks
        self._patched_methods = set()
    
    def patch_agent(self, agent_class):
        """Patch an agent class to add monitoring."""
        if hasattr(agent_class, '_monitoring_patched'):
            return agent_class
        
        original_execute = getattr(agent_class, 'execute', None)
        if original_execute and callable(original_execute):
            @wraps(original_execute)
            async def monitored_execute(self, task, context=None):
                with self.hooks.monitor_agent_execution(self.name, task):
                    return await original_execute(self, task, context or {})
            
            agent_class.execute = monitored_execute
        
        original_step = getattr(agent_class, 'step', None)
        if original_step and callable(original_step):
            @wraps(original_step)
            async def monitored_step(self):
                with self.hooks.monitor_agent_execution(self.name, "step"):
                    return await original_step(self)
            
            agent_class.step = monitored_step
        
        agent_class._monitoring_patched = True
        return agent_class
    
    def patch_tool(self, tool_func, tool_name: str):
        """Patch a tool function to add monitoring."""
        if hasattr(tool_func, '_monitoring_patched'):
            return tool_func
        
        @wraps(tool_func)
        def monitored_tool(*args, **kwargs):
            # Extract parameters for monitoring
            params = {}
            if kwargs:
                params.update(kwargs)
            
            with self.hooks.monitor_tool_execution(tool_name, params):
                return tool_func(*args, **kwargs)
        
        monitored_tool._monitoring_patched = True
        return monitored_tool
    
    def patch_runtime(self, runtime_class):
        """Patch a runtime class to add monitoring."""
        if hasattr(runtime_class, '_monitoring_patched'):
            return runtime_class
        
        # Patch file operations
        original_file_ops = getattr(runtime_class, 'file_operations', None)
        if original_file_ops:
            # This would need to be implemented based on the specific runtime
            pass
        
        runtime_class._monitoring_patched = True
        return runtime_class
    
    def start_monitoring_server(self, host: str = "0.0.0.0", port: int = 8000):
        """Start the monitoring web server."""
        from openhands.monitoring.server import MonitoringServer
        
        server = MonitoringServer(self.monitor, host, port)
        
        # Start server in background
        async def run_server():
            await server.start()
        
        asyncio.create_task(run_server())
        return server
    
    def enable_monitoring(self, enable: bool = True):
        """Enable or disable monitoring."""
        self.monitor.config.enabled = enable
        
        if enable:
            self.monitor.start_monitoring()
        else:
            self.monitor.stop_monitoring()
    
    def get_dashboard_url(self, host: str = "localhost", port: int = 8000) -> str:
        """Get the URL for the monitoring dashboard."""
        return f"http://{host}:{port}"


# Global integration instance
integration = MonitoringIntegration()


def monitor_agent_execution(func: Callable) -> Callable:
    """Decorator to monitor agent execution."""
    @wraps(func)
    async def wrapper(self, *args, **kwargs):
        from openhands.monitoring import hooks
        task = kwargs.get('task', args[0] if args else 'unknown')
        with hooks.monitor_agent_execution(self.name, task):
            return await func(self, *args, **kwargs)
    return wrapper


def monitor_tool_execution(tool_name: str) -> Callable:
    """Decorator factory for monitoring tool execution."""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from openhands.monitoring import hooks
            params = {}
            if kwargs:
                # Filter out sensitive parameters
                sensitive_keys = ['password', 'key', 'secret', 'token']
                params = {k: '***' if any(s in k.lower() for s in sensitive_keys) else v 
                         for k, v in kwargs.items()}
            
            with hooks.monitor_tool_execution(tool_name, params):
                return func(*args, **kwargs)
        return wrapper
    return decorator


def monitor_llm_call(func: Callable) -> Callable:
    """Decorator to monitor LLM API calls."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        from openhands.monitoring import hooks
        model = kwargs.get('model', 'unknown')
        prompt = kwargs.get('prompt', '')
        
        with hooks.monitor_llm_call(model, len(prompt)):
            return await func(*args, **kwargs)
    return wrapper