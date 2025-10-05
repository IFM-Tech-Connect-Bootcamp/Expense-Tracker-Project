"""Infrastructure settings and configuration.

This module provides configuration for infrastructure components
including authentication, outbox processing, and database settings.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class AuthConfig:
    """Authentication configuration."""
    
    # JWT settings
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    
    # Password hashing settings
    bcrypt_rounds: int = 12
    password_rehash_check: bool = True
    
    # Password policy settings
    password_policy_type: str = "default"  # "default", "lenient", "strict"
    password_min_length: int = 8


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
    
    auth: AuthConfig
    outbox: OutboxConfig
    
    @classmethod
    def from_django_settings(cls, settings: Optional[object] = None) -> "InfrastructureConfig":
        """Create configuration from Django settings.
        
        Args:
            settings: Django settings object. If None, imports from django.conf.
            
        Returns:
            InfrastructureConfig instance.
        """
        if settings is None:
            try:
                from django.conf import settings as django_settings
                settings = django_settings
            except ImportError:
                # Use defaults if Django not available
                return cls.default()
        
        # Extract auth settings
        auth_config = AuthConfig(
            jwt_secret_key=getattr(settings, 'JWT_SECRET_KEY', AuthConfig.jwt_secret_key),
            jwt_algorithm=getattr(settings, 'JWT_ALGORITHM', AuthConfig.jwt_algorithm),
            jwt_access_token_expire_minutes=getattr(
                settings, 'JWT_ACCESS_TOKEN_EXPIRE_MINUTES', AuthConfig.jwt_access_token_expire_minutes
            ),
            jwt_refresh_token_expire_days=getattr(
                settings, 'JWT_REFRESH_TOKEN_EXPIRE_DAYS', AuthConfig.jwt_refresh_token_expire_days
            ),
            bcrypt_rounds=getattr(settings, 'BCRYPT_ROUNDS', AuthConfig.bcrypt_rounds),
            password_rehash_check=getattr(
                settings, 'PASSWORD_REHASH_CHECK', AuthConfig.password_rehash_check
            ),
            password_policy_type=getattr(settings, 'PASSWORD_POLICY_TYPE', AuthConfig.password_policy_type),
            password_min_length=getattr(settings, 'PASSWORD_MIN_LENGTH', AuthConfig.password_min_length),
        )
        
        # Extract outbox settings
        outbox_config = OutboxConfig(
            auto_process=getattr(settings, 'OUTBOX_AUTO_PROCESS', OutboxConfig.auto_process),
            batch_size=getattr(settings, 'OUTBOX_BATCH_SIZE', OutboxConfig.batch_size),
            processing_interval_seconds=getattr(
                settings, 'OUTBOX_PROCESSING_INTERVAL_SECONDS', OutboxConfig.processing_interval_seconds
            ),
            max_retry_attempts=getattr(
                settings, 'OUTBOX_MAX_RETRY_ATTEMPTS', OutboxConfig.max_retry_attempts
            ),
            retry_delay_seconds=getattr(
                settings, 'OUTBOX_RETRY_DELAY_SECONDS', OutboxConfig.retry_delay_seconds
            ),
            webhook_timeout_seconds=getattr(
                settings, 'OUTBOX_WEBHOOK_TIMEOUT_SECONDS', OutboxConfig.webhook_timeout_seconds
            ),
            webhook_max_retries=getattr(
                settings, 'OUTBOX_WEBHOOK_MAX_RETRIES', OutboxConfig.webhook_max_retries
            ),
        )
        
        return cls(auth=auth_config, outbox=outbox_config)
    
    @classmethod 
    def default(cls) -> "InfrastructureConfig":
        """Create default configuration."""
        return cls(
            auth=AuthConfig(),
            outbox=OutboxConfig(),
        )


# Global configuration instance
_config: Optional[InfrastructureConfig] = None


def get_config() -> InfrastructureConfig:
    """Get the global infrastructure configuration.
    
    Returns:
        InfrastructureConfig instance.
    """
    global _config
    if _config is None:
        _config = InfrastructureConfig.from_django_settings()
    return _config


def set_config(config: InfrastructureConfig) -> None:
    """Set the global infrastructure configuration.
    
    Args:
        config: InfrastructureConfig instance.
    """
    global _config
    _config = config