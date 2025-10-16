"""Django model for outbox events."""

import uuid
from django.db import models
from django.utils import timezone


class OutboxEvent(models.Model):
    """Model for storing domain events in outbox pattern.
    
    Using transactional outbox pattern for reliable event delivery.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event_type = models.CharField(max_length=255)
    aggregate_id = models.UUIDField(null=True, blank=True)
    payload = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    error_count = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)

    class Meta:
        db_table = 'expense_management_outbox'
        ordering = ['created_at']

    def __str__(self) -> str:
        return f"{self.event_type} ({self.id})"