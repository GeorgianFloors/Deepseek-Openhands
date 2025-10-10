"""Enhanced agent controller with monitoring capabilities."""

from typing import Dict, Any, Optional
from openhands.core.agent import BaseAgent
from openhands.core.runtime import Runtime
from openhands.monitoring.hooks import MonitoringHooks


class MonitoredAgentController:
    """Agent controller with integrated monitoring."""
    
    def __init__(self, agent: BaseAgent, runtime: Runtime, hooks: MonitoringHooks):
        self.agent = agent
        self.runtime = runtime
        self.hooks = hooks
    
    async def execute_task(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a task with monitoring."""
        with self.hooks.monitor_agent_execution(self.agent.name, task):
            # Execute the task using the original agent
            result = await self.agent.execute(task, context or {})
            
            # Record tool usage if available
            if hasattr(result, 'tool_calls') and result.tool_calls:
                for tool_call in result.tool_calls:
                    self.hooks.monitor.update_agent_metrics(
                        self.agent.name, 
                        {"tool_used": tool_call.get('name', 'unknown')}
                    )
            
            return result
    
    async def step(self) -> Any:
        """Execute a single step with monitoring."""
        # This would need to be integrated with the specific agent implementation
        # For now, we'll use a generic approach
        with self.hooks.monitor_agent_execution(self.agent.name, "step"):
            if hasattr(self.agent, 'step'):
                return await self.agent.step()
            else:
                # Fallback to basic execution
                return await self.execute_task("step")
    
    def reset(self) -> None:
        """Reset the agent with monitoring."""
        with self.hooks.monitor_agent_execution(self.agent.name, "reset"):
            if hasattr(self.agent, 'reset'):
                self.agent.reset()
    
    def get_agent_metrics(self) -> Dict[str, Any]:
        """Get metrics for this agent."""
        return self.hooks.monitor.get_agent_metrics().get(self.agent.name, {})