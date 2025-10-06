"""Initial migration for User Management bounded context.

This migration creates the complete database schema for the user management
infrastructure layer including:
- UserModel: User entity persistence with proper indexing
- OutboxEvent: Transactional outbox pattern for reliable event delivery

This follows clean architecture principles where migrations are infrastructure concerns.
"""

from django.db import migrations, models
import django.utils.timezone
import uuid


class Migration(migrations.Migration):
    """Initial migration for user management infrastructure."""

    initial = True

    dependencies = []

    operations = [
        # Create UserModel table
        migrations.CreateModel(
            name='UserModel',
            fields=[
                (
                    'id',
                    models.UUIDField(
                        primary_key=True,
                        default=uuid.uuid4,
                        editable=False,
                        help_text='Unique identifier for the user'
                    )
                ),
                (
                    'email',
                    models.EmailField(
                        unique=True,
                        max_length=254,
                        help_text="User's email address (unique)"
                    )
                ),
                (
                    'password_hash',
                    models.CharField(
                        max_length=255,
                        help_text='Hashed password for authentication'
                    )
                ),
                (
                    'first_name',
                    models.CharField(
                        max_length=50,
                        help_text="User's first name"
                    )
                ),
                (
                    'last_name',
                    models.CharField(
                        max_length=50,
                        help_text="User's last name"
                    )
                ),
                (
                    'status',
                    models.CharField(
                        max_length=32,
                        default='active',
                        help_text='User account status'
                    )
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text='When the user account was created'
                    )
                ),
                (
                    'updated_at',
                    models.DateTimeField(
                        auto_now=True,
                        help_text='When the user account was last updated'
                    )
                ),
            ],
            options={
                'db_table': 'user_management_user',
                'verbose_name': 'User',
                'verbose_name_plural': 'Users',
            },
        ),
        
        # Create OutboxEvent table
        migrations.CreateModel(
            name='OutboxEvent',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        primary_key=True,
                        help_text='Auto-incrementing primary key'
                    )
                ),
                (
                    'event_type',
                    models.CharField(
                        max_length=255,
                        help_text='Type of the domain event'
                    )
                ),
                (
                    'aggregate_id',
                    models.UUIDField(
                        null=True,
                        blank=True,
                        help_text='ID of the aggregate that generated the event'
                    )
                ),
                (
                    'payload',
                    models.JSONField(
                        help_text='Event data as JSON'
                    )
                ),
                (
                    'created_at',
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text='When the event was created'
                    )
                ),
                (
                    'processed_at',
                    models.DateTimeField(
                        null=True,
                        blank=True,
                        help_text='When the event was successfully processed'
                    )
                ),
                (
                    'attempts',
                    models.IntegerField(
                        default=0,
                        help_text='Number of processing attempts'
                    )
                ),
                (
                    'error_message',
                    models.TextField(
                        null=True,
                        blank=True,
                        help_text='Last error message if processing failed'
                    )
                ),
            ],
            options={
                'db_table': 'user_management_outbox',
                'verbose_name': 'Outbox Event',
                'verbose_name_plural': 'Outbox Events',
                'ordering': ['created_at'],
            },
        ),
        
        # Add indexes for UserModel
        migrations.AddIndex(
            model_name='usermodel',
            index=models.Index(fields=['email'], name='user_email_idx'),
        ),
        migrations.AddIndex(
            model_name='usermodel',
            index=models.Index(fields=['status'], name='user_status_idx'),
        ),
        migrations.AddIndex(
            model_name='usermodel',
            index=models.Index(fields=['created_at'], name='user_created_idx'),
        ),
        
        # Add indexes for OutboxEvent
        migrations.AddIndex(
            model_name='outboxevent',
            index=models.Index(fields=['event_type'], name='outbox_event_type_idx'),
        ),
        migrations.AddIndex(
            model_name='outboxevent',
            index=models.Index(fields=['processed_at'], name='outbox_processed_idx'),
        ),
        migrations.AddIndex(
            model_name='outboxevent',
            index=models.Index(fields=['created_at'], name='outbox_created_idx'),
        ),
        migrations.AddIndex(
            model_name='outboxevent',
            index=models.Index(fields=['aggregate_id'], name='outbox_aggregate_idx'),
        ),
    ]