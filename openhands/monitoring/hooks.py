"""Monitoring hooks for OpenHands core components."""

import time
from typing import Dict, Any, Optional
from contextlib import contextmanager

from openhands.monitoring.types import ActivityType, ActivityStatus


class MonitoringHooks:
    """Hooks for monitoring OpenHands activities."""
    
    def __init__(self, monitor):
        self.monitor = monitor
    
    @contextmanager
    def monitor_agent_execution(self, agent_name: str, task: str):
        """Monitor agent execution with context manager."""
        activity_id = self.monitor.start_activity(
            ActivityType.AGENT_EXECUTION,
            f"{agent_name}: {task[:50]}",
            {"agent": agent_name, "task": task}
        )
        
        start_time = time.time()
        status = ActivityStatus.COMPLETED
        error = None
        
        try:
            yield
        except Exception as e:
            status = ActivityStatus.FAILED
            error = str(e)
            raise
        finally:
            duration = time.time() - start_time
            
            # Update agent metrics
            self.monitor.update_agent_metrics(agent_name, {
                "response_time": duration,
                "task_completed" if status == ActivityStatus.COMPLETED else "task_failed": True
            })
            
            # End the activity
            self.monitor.end_activity(
                activity_id, 
                status,
                {"duration": duration, "error": error} if error else {"duration": duration}
            )
    
    @contextmanager
    def monitor_tool_execution(self, tool_name: str, parameters: Dict[str, Any] = None):
        """Monitor tool execution with context manager."""
        activity_id = self.monitor.start_activity(
            ActivityType.TOOL_EXECUTION,
            f"Tool: {tool_name}",
            {"tool": tool_name, "parameters": parameters or {}}
        )
        
        start_time = time.time()
        status = ActivityStatus.COMPLETED
        error = None
        result = None
        
        try:
            yield
        except Exception as e:
            status = ActivityStatus.FAILED
            error = str(e)
            raise
        finally:
            duration = time.time() - start_time
            
            # Update tool usage in agent metrics (if we have agent context)
            # This would need to be called from within agent context
            
            self.monitor.end_activity(
                activity_id, 
                status,
                {
                    "duration": duration, 
                    "error": error,
                    "result": str(result) if result else None
                }
            )
    
    @contextmanager
    def monitor_llm_call(self, model: str, prompt_length: int):
        """Monitor LLM API calls."""
        activity_id = self.monitor.start_activity(
            ActivityType.LLM_CALL,
            f"LLM: {model}",
            {"model": model, "prompt_length": prompt_length}
        )
        
        start_time = time.time()
        status = ActivityStatus.COMPLETED
        error = None
        tokens_used = 0
        
        try:
            yield
        except Exception as e:
            status = ActivityStatus.FAILED
            error = str(e)
            raise
        finally:
            duration = time.time() - start_time
            
            # Update token usage
            if tokens_used > 0:
                self.monitor.update_agent_metrics("unknown", {"tokens_used": tokens_used})
            
            self.monitor.end_activity(
                activity_id, 
                status,
                {
                    "duration": duration, 
                    "error": error,
                    "tokens_used": tokens_used,
                    "response_time": duration
                }
            )
    
    @contextmanager
    def monitor_file_operation(self, operation: str, file_path: str):
        """Monitor file operations."""
        activity_id = self.monitor.start_activity(
            ActivityType.FILE_OPERATION,
            f"File {operation}: {file_path}",
            {"operation": operation, "file_path": file_path}
        )
        
        start_time = time.time()
        status = ActivityStatus.COMPLETED
        error = None
        
        try:
            yield
        except Exception as e:
            status = ActivityStatus.FAILED
            error = str(e)
            raise
        finally:
            duration = time.time() - start_time
            
            self.monitor.end_activity(
                activity_id, 
                status,
                {"duration": duration, "error": error}
            )
    
    @contextmanager
    def monitor_command_execution(self, command: str):
        """Monitor command execution."""
        activity_id = self.monitor.start_activity(
            ActivityType.COMMAND_EXECUTION,
            f"Command: {command[:50]}",
            {"command": command}
        )
        
        start_time = time.time()
        status = ActivityStatus.COMPLETED
        error = None
        
        try:
            yield
        except Exception as e:
            status = ActivityStatus.FAILED
            error = str(e)
            raise
        finally:
            duration = time.time() - start_time
            
            self.monitor.end_activity(
                activity_id, 
                status,
                {"duration": duration, "error": error}
            )
    
    def record_network_request(self, url: str, method: str, status_code: Optional[int] = None):
        """Record a network request."""
        activity_id = self.monitor.start_activity(
            ActivityType.NETWORK_REQUEST,
            f"{method} {url}",
            {"url": url, "method": method}
        )
        
        self.monitor.end_activity(
            activity_id,
            ActivityStatus.COMPLETED,
            {"status_code": status_code}
        )


# Global hooks instance will be created in __init__.py