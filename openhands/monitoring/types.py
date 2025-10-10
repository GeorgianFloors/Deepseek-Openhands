"""Data types for monitoring system."""

from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


class ActivityType(Enum):
    """Types of activities that can be monitored."""
    AGENT_EXECUTION = "agent_execution"
    TOOL_EXECUTION = "tool_execution"
    LLM_CALL = "llm_call"
    FILE_OPERATION = "file_operation"
    COMMAND_EXECUTION = "command_execution"
    NETWORK_REQUEST = "network_request"
    MEMORY_OPERATION = "memory_operation"
    WORKFLOW_STEP = "workflow_step"


class ActivityStatus(Enum):
    """Status of an activity."""
    STARTED = "started"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Activity:
    """Represents a monitored activity."""
    id: str
    type: ActivityType
    name: str
    timestamp: datetime
    status: ActivityStatus
    metadata: Dict[str, Any] = field(default_factory=dict)
    duration: Optional[float] = None
    parent_id: Optional[str] = None
    children: List[str] = field(default_factory=list)


@dataclass
class SystemMetrics:
    """System resource metrics."""
    timestamp: datetime
    cpu_usage: float  # Percentage
    memory_usage: float  # MB
    disk_usage: float  # MB
    network_io: Dict[str, float]  # Bytes in/out
    active_processes: int


@dataclass
class AgentMetrics:
    """Agent-specific metrics."""
    agent_name: str
    tasks_completed: int
    tasks_failed: int
    average_response_time: float
    tool_usage: Dict[str, int]  # Tool name -> usage count
    token_usage: int


@dataclass
class VisualizationConfig:
    """Configuration for visualization settings."""
    enabled: bool = True
    update_interval: float = 0.1  # seconds
    max_history: int = 1000  # max activities to keep
    enable_resource_monitoring: bool = True
    enable_agent_metrics: bool = True
    enable_detailed_logging: bool = False