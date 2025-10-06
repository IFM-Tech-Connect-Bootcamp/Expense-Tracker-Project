"""Infrastructure settings and configuration for Expense Management.

This module provides configuration for infrastructure components
including outbox processing and database settings.
"""

from dataclasses import dataclass
from typing import Optional


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
class ExpenseConfig:
    """Expense management specific configuration."""
    
    # TZS currency settings
    default_currency: str = "TZS"
    decimal_places: int = 2
    
    # Validation settings
    max_expense_amount: float = 1000000.00  # 1M TZS max expense
    min_expense_amount: float = 0.01  # 1 cent minimum
    
    # Category settings
    max_categories_per_user: int = 100
    default_category_name: str = "Miscellaneous"
    
    # Pagination settings
    default_page_size: int = 20
    max_page_size: int = 100


@dataclass(frozen=True)
class InfrastructureConfig:
    """Combined infrastructure configuration for Expense Management."""
    
    outbox: OutboxConfig
    expense: ExpenseConfig
    
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
        
        # Extract outbox settings
        outbox_config = OutboxConfig(
            auto_process=getattr(settings, 'EXPENSE_OUTBOX_AUTO_PROCESS', OutboxConfig.auto_process),
            batch_size=getattr(settings, 'EXPENSE_OUTBOX_BATCH_SIZE', OutboxConfig.batch_size),
            processing_interval_seconds=getattr(
                settings, 'EXPENSE_OUTBOX_PROCESSING_INTERVAL_SECONDS', OutboxConfig.processing_interval_seconds
            ),
            max_retry_attempts=getattr(
                settings, 'EXPENSE_OUTBOX_MAX_RETRY_ATTEMPTS', OutboxConfig.max_retry_attempts
            ),
            retry_delay_seconds=getattr(
                settings, 'EXPENSE_OUTBOX_RETRY_DELAY_SECONDS', OutboxConfig.retry_delay_seconds
            ),
            webhook_timeout_seconds=getattr(
                settings, 'EXPENSE_OUTBOX_WEBHOOK_TIMEOUT_SECONDS', OutboxConfig.webhook_timeout_seconds
            ),
            webhook_max_retries=getattr(
                settings, 'EXPENSE_OUTBOX_WEBHOOK_MAX_RETRIES', OutboxConfig.webhook_max_retries
            ),
        )
        
        # Extract expense settings
        expense_config = ExpenseConfig(
            default_currency=getattr(settings, 'EXPENSE_DEFAULT_CURRENCY', ExpenseConfig.default_currency),
            decimal_places=getattr(settings, 'EXPENSE_DECIMAL_PLACES', ExpenseConfig.decimal_places),
            max_expense_amount=getattr(settings, 'EXPENSE_MAX_AMOUNT', ExpenseConfig.max_expense_amount),
            min_expense_amount=getattr(settings, 'EXPENSE_MIN_AMOUNT', ExpenseConfig.min_expense_amount),
            max_categories_per_user=getattr(
                settings, 'EXPENSE_MAX_CATEGORIES_PER_USER', ExpenseConfig.max_categories_per_user
            ),
            default_category_name=getattr(
                settings, 'EXPENSE_DEFAULT_CATEGORY_NAME', ExpenseConfig.default_category_name
            ),
            default_page_size=getattr(settings, 'EXPENSE_DEFAULT_PAGE_SIZE', ExpenseConfig.default_page_size),
            max_page_size=getattr(settings, 'EXPENSE_MAX_PAGE_SIZE', ExpenseConfig.max_page_size),
        )
        
        return cls(outbox=outbox_config, expense=expense_config)
    
    @classmethod 
    def default(cls) -> "InfrastructureConfig":
        """Create default configuration."""
        return cls(
            outbox=OutboxConfig(),
            expense=ExpenseConfig(),
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