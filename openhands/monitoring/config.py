"""Configuration for the monitoring system."""

from typing import Dict, Any
from openhands.monitoring.types import VisualizationConfig


class MonitoringConfig:
    """Configuration for the OpenHands monitoring system."""
    
    def __init__(self, config_dict: Dict[str, Any] = None):
        self.config_dict = config_dict or {}
        
        # Default configuration
        self.default_config = {
            'enabled': True,
            'server': {
                'host': '0.0.0.0',
                'port': 8000,
                'enable_cors': True
            },
            'visualization': {
                'update_interval': 0.1,
                'max_history': 1000,
                'enable_resource_monitoring': True,
                'enable_agent_metrics': True,
                'enable_detailed_logging': False
            },
            'integration': {
                'auto_patch_agents': True,
                'auto_patch_tools': True,
                'auto_start_server': False
            }
        }
        
        # Merge with provided config
        self._config = self._merge_configs(self.default_config, self.config_dict)
    
    def _merge_configs(self, default: Dict[str, Any], custom: Dict[str, Any]) -> Dict[str, Any]:
        """Recursively merge two configuration dictionaries."""
        result = default.copy()
        
        for key, value in custom.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
        
        return result
    
    @property
    def enabled(self) -> bool:
        """Whether monitoring is enabled."""
        return self._config['enabled']
    
    @property
    def server_host(self) -> str:
        """Server host address."""
        return self._config['server']['host']
    
    @property
    def server_port(self) -> int:
        """Server port."""
        return self._config['server']['port']
    
    @property
    def enable_cors(self) -> bool:
        """Whether to enable CORS."""
        return self._config['server']['enable_cors']
    
    @property
    def visualization_config(self) -> VisualizationConfig:
        """Get visualization configuration."""
        viz_config = self._config['visualization']
        return VisualizationConfig(
            enabled=self.enabled,
            update_interval=viz_config['update_interval'],
            max_history=viz_config['max_history'],
            enable_resource_monitoring=viz_config['enable_resource_monitoring'],
            enable_agent_metrics=viz_config['enable_agent_metrics'],
            enable_detailed_logging=viz_config['enable_detailed_logging']
        )
    
    @property
    def auto_patch_agents(self) -> bool:
        """Whether to automatically patch agents."""
        return self._config['integration']['auto_patch_agents']
    
    @property
    def auto_patch_tools(self) -> bool:
        """Whether to automatically patch tools."""
        return self._config['integration']['auto_patch_tools']
    
    @property
    def auto_start_server(self) -> bool:
        """Whether to automatically start the monitoring server."""
        return self._config['integration']['auto_start_server']
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self._config.copy()


# Default configuration
default_config = MonitoringConfig()