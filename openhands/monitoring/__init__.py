"""Real-time monitoring and visualization system for OpenHands."""

from openhands.monitoring.monitor import ActivityMonitor
from openhands.monitoring.types import ActivityType, ActivityStatus

# Global monitor instance
monitor = ActivityMonitor()

# Import hooks after monitor is created to avoid circular imports
from openhands.monitoring.hooks import MonitoringHooks
hooks = MonitoringHooks(monitor)

from openhands.monitoring.integration import MonitoringIntegration
integration = MonitoringIntegration()

__all__ = [
    'monitor', 
    'ActivityMonitor', 
    'ActivityType', 
    'ActivityStatus',
    'MonitoringHooks',
    'hooks',
    'MonitoringIntegration', 
    'integration'
]