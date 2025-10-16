"""Django ORM models for expense management."""

import uuid

from django.db import models
from django.utils import timezone

class ExpenseModel(models.Model):
    """Django model representing an expense."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    amount_tzs = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date = models.DateField()
    category_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'expense_management_expenses'
        ordering = ['-date', '-created_at']


class CategoryModel(models.Model):
    """Django model representing an expense category."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7)  # hex color code
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'expense_management_categories'
        ordering = ['name']
        unique_together = [['user_id', 'name']]