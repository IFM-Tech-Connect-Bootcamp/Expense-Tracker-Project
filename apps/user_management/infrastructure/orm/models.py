"""Django ORM models for User Management infrastructure.

This module contains Django models that map to database tables
for the User Management bounded context.
"""

from __future__ import annotations

import uuid
from typing import Any, Dict

from django.db import models
from django.utils import timezone


class UserModel(models.Model):
    """Django model for User entity persistence.
    
    Maps to the User domain entity and provides database persistence
    through Django ORM.
    """
    
    id: models.UUIDField = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the user"
    )
    
    email: models.EmailField = models.EmailField(
        unique=True,
        max_length=254,
        help_text="User's email address (unique)"
    )
    
    password_hash: models.CharField = models.CharField(
        max_length=255,
        help_text="Hashed password for authentication"
    )
    
    first_name: models.CharField = models.CharField(
        max_length=50,
        help_text="User's first name"
    )
    
    last_name: models.CharField = models.CharField(
        max_length=50,
        help_text="User's last name"
    )
    
    status: models.CharField = models.CharField(
        max_length=32,
        default="active",
        help_text="User account status"
    )
    
    created_at: models.DateTimeField = models.DateTimeField(
        default=timezone.now,
        help_text="When the user account was created"
    )
    
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        help_text="When the user account was last updated"
    )

    class Meta:
        db_table = "user_management_user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            models.Index(fields=['email'], name='user_email_idx'),
            models.Index(fields=['status'], name='user_status_idx'),
            models.Index(fields=['created_at'], name='user_created_idx'),
        ]

    def __str__(self) -> str:
        """String representation of the user."""
        return f"UserModel(id={self.id}, email={self.email})"

    def __repr__(self) -> str:
        """Detailed string representation of the user."""
        return (
            f"UserModel(id={self.id}, email='{self.email}', "
            f"first_name='{self.first_name}', last_name='{self.last_name}', "
            f"status='{self.status}')"
        )


class OutboxEvent(models.Model):
    """Django model for outbox event pattern.
    
    Stores domain events for reliable delivery to external systems.
    Implements the transactional outbox pattern for eventual consistency.
    """
    
    id: models.BigAutoField = models.BigAutoField(
        primary_key=True,
        help_text="Auto-incrementing primary key"
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
        help_text="Last error message if processing failed"
    )

    class Meta:
        db_table = "user_management_outbox"
        verbose_name = "Outbox Event"
        verbose_name_plural = "Outbox Events"
        indexes = [
            models.Index(fields=['event_type'], name='outbox_event_type_idx'),
            models.Index(fields=['processed_at'], name='outbox_processed_idx'),
            models.Index(fields=['created_at'], name='outbox_created_idx'),
            models.Index(fields=['aggregate_id'], name='outbox_aggregate_idx'),
        ]
        ordering = ['created_at']

    def __str__(self) -> str:
        """String representation of the outbox event."""
        status = "processed" if self.processed_at else "pending"
        return f"OutboxEvent(id={self.id}, type={self.event_type}, status={status})"

    def __repr__(self) -> str:
        """Detailed string representation of the outbox event."""
        return (
            f"OutboxEvent(id={self.id}, event_type='{self.event_type}', "
            f"aggregate_id={self.aggregate_id}, attempts={self.attempts})"
        )

    @property
    def is_processed(self) -> bool:
        """Check if the event has been processed."""
        return self.processed_at is not None

    @property
    def is_failed(self) -> bool:
        """Check if the event has failed processing."""
        return self.attempts > 0 and not self.is_processed

    def mark_processed(self) -> None:
        """Mark the event as successfully processed."""
        self.processed_at = timezone.now()

    def increment_attempts(self, error_message: str | None = None) -> None:
        """Increment the number of processing attempts."""
        self.attempts += 1
        if error_message:
            self.error_message = error_message