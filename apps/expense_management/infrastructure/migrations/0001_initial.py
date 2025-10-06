# Generated migration for expense management models

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):
    """Initial migration for expense management models."""

    initial = True

    dependencies = [
        # Add user management dependency if tables exist
        # ('user_management', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CategoryModel',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('user_id', models.UUIDField(db_index=True)),
                ('name', models.CharField(max_length=100)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'expense_categories',
                'ordering': ['name'],
                'indexes': [
                    models.Index(fields=['user_id'], name='expense_cat_user_idx'),
                    models.Index(fields=['user_id', 'name'], name='expense_cat_user_name_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='ExpenseModel',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('user_id', models.UUIDField(db_index=True)),
                ('category_id', models.UUIDField()),
                ('amount_tzs', models.DecimalField(max_digits=12, decimal_places=2)),
                ('description', models.CharField(max_length=500, blank=True, null=True)),
                ('expense_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'db_table': 'expenses',
                'ordering': ['-expense_date', '-created_at'],
                'indexes': [
                    models.Index(fields=['user_id'], name='expense_user_idx'),
                    models.Index(fields=['user_id', 'expense_date'], name='expense_user_date_idx'),
                    models.Index(fields=['user_id', 'category_id'], name='expense_user_cat_idx'),
                    models.Index(fields=['expense_date'], name='expense_date_idx'),
                ],
            },
        ),
        migrations.CreateModel(
            name='OutboxEvent',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)),
                ('event_type', models.CharField(max_length=255)),
                ('aggregate_id', models.UUIDField(null=True, blank=True)),
                ('payload', models.JSONField()),
                ('created_at', models.DateTimeField()),
                ('processed_at', models.DateTimeField(null=True, blank=True)),
                ('attempts', models.PositiveIntegerField(default=0)),
                ('last_error', models.TextField(null=True, blank=True)),
            ],
            options={
                'db_table': 'expense_outbox_events',
                'ordering': ['created_at'],
                'indexes': [
                    models.Index(fields=['processed_at'], name='expense_outbox_processed_idx'),
                    models.Index(fields=['event_type'], name='expense_outbox_type_idx'),
                    models.Index(fields=['created_at'], name='expense_outbox_created_idx'),
                    models.Index(fields=['aggregate_id'], name='expense_outbox_aggregate_idx'),
                ],
            },
        ),
        migrations.AddConstraint(
            model_name='categorymodel',
            constraint=models.UniqueConstraint(
                fields=['user_id', 'name'],
                name='expense_unique_category_per_user'
            ),
        ),
        migrations.AddConstraint(
            model_name='expensemodel',
            constraint=models.CheckConstraint(
                check=models.Q(amount_tzs__gt=0),
                name='expense_positive_amount'
            ),
        ),
        migrations.AddConstraint(
            model_name='expensemodel',
            constraint=models.CheckConstraint(
                check=models.Q(amount_tzs__lte=1000000),
                name='expense_max_amount_1m'
            ),
        ),
    ]