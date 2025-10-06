"""Django ORM models for Expense Management infrastructure.

This module contains Django models that map to database tables
for the Expense Management bounded context.
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Any, Dict

from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxLengthValidator


class ExpenseModel(models.Model):
    """Django model for Expense entity persistence.
    
    Maps to the Expense domain entity and provides database persistence
    through Django ORM for financial data.
    """
    
    id: models.UUIDField = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the expense"
    )
    
    user_id: models.UUIDField = models.UUIDField(
        help_text="ID of the user who owns this expense"
    )
    
    category_id: models.UUIDField = models.UUIDField(
        help_text="ID of the category for this expense"
    )
    
    amount_tzs: models.DecimalField = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Expense amount in Tanzanian Shillings (TZS)"
    )
    
    description: models.TextField = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Optional description of the expense"
    )
    
    expense_date: models.DateField = models.DateField(
        help_text="Date when the expense occurred"
    )
    
    created_at: models.DateTimeField = models.DateTimeField(
        default=timezone.now,
        help_text="When the expense record was created"
    )
    
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        help_text="When the expense record was last updated"
    )
    
    class Meta:
        """Model metadata."""
        app_label = 'expense_management'
        db_table = 'expense_management_expenses'
        verbose_name = 'Expense'
        verbose_name_plural = 'Expenses'
        
        # Indexes for optimized queries
        indexes = [
            models.Index(fields=['user_id'], name='em_exp_user_idx'),
            models.Index(fields=['category_id'], name='em_exp_category_idx'),
            models.Index(fields=['expense_date'], name='em_exp_date_idx'),
            models.Index(fields=['user_id', 'expense_date'], name='em_exp_user_date_idx'),
            models.Index(fields=['user_id', 'category_id'], name='em_exp_user_cat_idx'),
            models.Index(fields=['created_at'], name='em_exp_created_idx'),
        ]
        
        # Constraints
        constraints = [
            models.CheckConstraint(
                check=models.Q(amount_tzs__gte=0),
                name='em_exp_amount_non_negative'
            ),
        ]
        
        # Ordering
        ordering = ['-expense_date', '-created_at']
    
    def __str__(self) -> str:
        """String representation of the expense."""
        return f"Expense({self.id}) - TZS {self.amount_tzs:,.2f} on {self.expense_date}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"ExpenseModel(id={self.id}, user_id={self.user_id}, "
            f"amount_tzs={self.amount_tzs}, expense_date={self.expense_date})"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'category_id': str(self.category_id),
            'amount_tzs': float(self.amount_tzs),
            'description': self.description,
            'expense_date': self.expense_date.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class CategoryModel(models.Model):
    """Django model for Category entity persistence.
    
    Maps to the Category domain entity and provides database persistence
    through Django ORM for expense categorization.
    """
    
    id: models.UUIDField = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the category"
    )
    
    user_id: models.UUIDField = models.UUIDField(
        help_text="ID of the user who owns this category"
    )
    
    name: models.CharField = models.CharField(
        max_length=100,
        help_text="Name of the category"
    )
    
    created_at: models.DateTimeField = models.DateTimeField(
        default=timezone.now,
        help_text="When the category was created"
    )
    
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        help_text="When the category was last updated"
    )
    
    class Meta:
        """Model metadata."""
        app_label = 'expense_management'
        db_table = 'expense_management_categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        
        # Unique constraint: category names must be unique per user
        constraints = [
            models.UniqueConstraint(
                fields=['user_id', 'name'],
                name='em_cat_user_name_unique'
            ),
        ]
        
        # Indexes for optimized queries
        indexes = [
            models.Index(fields=['user_id'], name='em_cat_user_idx'),
            models.Index(fields=['name'], name='em_cat_name_idx'),
            models.Index(fields=['created_at'], name='em_cat_created_idx'),
        ]
        
        # Ordering
        ordering = ['name', 'created_at']
    
    def __str__(self) -> str:
        """String representation of the category."""
        return f"Category({self.name}) - User {self.user_id}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"CategoryModel(id={self.id}, user_id={self.user_id}, "
            f"name='{self.name}')"
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model instance to dictionary."""
        return {
            'id': str(self.id),
            'user_id': str(self.user_id),
            'name': self.name,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }


class OutboxEvent(models.Model):
    """Django model for transactional outbox pattern.
    
    Stores domain events that need to be published to external systems
    using the transactional outbox pattern for reliable event delivery.
    """
    
    id: models.BigAutoField = models.BigAutoField(
        primary_key=True,
        help_text="Auto-incrementing event identifier"
    )
    
    event_type: models.CharField = models.CharField(
        max_length=255,
        help_text="Type of the domain event"
    )
    
    aggregate_id: models.UUIDField = models.UUIDField(
        null=True,
        blank=True,
        help_text="ID of the aggregate that generated the event"
    )
    
    payload: models.JSONField = models.JSONField(
        help_text="Event data as JSON"
    )
    
    created_at: models.DateTimeField = models.DateTimeField(
        default=timezone.now,
        help_text="When the event was created"
    )
    
    processed_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the event was successfully processed"
    )
    
    attempts: models.IntegerField = models.IntegerField(
        default=0,
        help_text="Number of processing attempts"
    )
    
    error_message: models.TextField = models.TextField(
        null=True,
        blank=True,
        help_text="Error message from last failed attempt"
    )
    
    class Meta:
        """Model metadata."""
        app_label = 'expense_management'
        db_table = 'expense_management_outbox_events'
        verbose_name = 'Outbox Event'
        verbose_name_plural = 'Outbox Events'
        
        # Indexes for event processing
        indexes = [
            models.Index(fields=['created_at'], name='em_outbox_created_idx'),
            models.Index(fields=['processed_at'], name='em_outbox_processed_idx'),
            models.Index(fields=['event_type'], name='em_outbox_type_idx'),
            models.Index(fields=['aggregate_id'], name='em_outbox_aggregate_idx'),
            models.Index(fields=['attempts'], name='em_outbox_attempts_idx'),
        ]
        
        # Ordering: process events in creation order
        ordering = ['created_at', 'id']
    
    @property
    def is_processed(self) -> bool:
        """Check if the event has been processed."""
        return self.processed_at is not None
    
    @property
    def is_failed(self) -> bool:
        """Check if the event has failed processing."""
        return self.attempts > 0 and not self.is_processed
    
    def __str__(self) -> str:
        """String representation of the outbox event."""
        status = "Processed" if self.is_processed else f"Pending (attempts: {self.attempts})"
        return f"OutboxEvent({self.event_type}) - {status}"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return (
            f"OutboxEvent(id={self.id}, event_type='{self.event_type}', "
            f"aggregate_id={self.aggregate_id}, attempts={self.attempts})"
        )
    
    def increment_attempts(self, error_message: str = None) -> None:
        """Increment the number of processing attempts.
        
        Args:
            error_message: Optional error message from failed attempt.
        """
        self.attempts += 1
        if error_message:
            self.error_message = error_message
    
    def mark_processed(self) -> None:
        """Mark the event as successfully processed."""
        self.processed_at = timezone.now()