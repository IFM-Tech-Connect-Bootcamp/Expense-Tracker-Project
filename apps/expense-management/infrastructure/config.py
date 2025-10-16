"""Infrastructure settings and configuration.

This module provides configuration for infrastructure components
including outbox processing and database settings.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class OutboxConfig:
    """Outbox pattern configuration."""
    
    # Processing settings
    auto_process: bool = False
    batch_size: int = 100
    processing_interval_seconds: int = 30
    max_retry_attempts: int = 3
    retry_delay_seconds: int = 60
    
    # Event delivery settings
    webhook_timeout_seconds: int = 30
    webhook_max_retries: int = 3


@dataclass(frozen=True)
class InfrastructureConfig:
    """Combined infrastructure configuration."""
    
    outbox: OutboxConfig

    @staticmethod
    def get_default_config() -> 'InfrastructureConfig':
        """Get default configuration."""
        return InfrastructureConfig(
            outbox=OutboxConfig(),
        )


from typing import Union
_config: Union[InfrastructureConfig, None] = None


def get_config() -> InfrastructureConfig:
    """Get global infrastructure configuration.
    
    Returns:
        InfrastructureConfig: Current configuration instance
    """
    global _config
    if _config is None:
        _config = InfrastructureConfig.get_default_config()
    return _config


def set_config(config: InfrastructureConfig) -> None:
    """Set global infrastructure configuration.
    
    Args:
        config: New configuration instance
    """
    global _config
    _config = config