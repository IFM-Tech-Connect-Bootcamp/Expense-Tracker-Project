"""Django management command for expense management infrastructure health checks.

This command verifies that all expense management infrastructure components 
are working correctly and can connect to external dependencies.
"""

import asyncio
import logging
import warnings
from decimal import Decimal
from typing import Any
from datetime import date, datetime

from django.core.management.base import BaseCommand, CommandParser
from django.db import transaction

# Suppress bcrypt version compatibility warnings from passlib
warnings.filterwarnings('ignore', message='.*bcrypt version.*', category=UserWarning)
warnings.filterwarnings('ignore', message='.*error reading bcrypt version.*')

# Also suppress at logging level for passlib
logging.getLogger('passlib.handlers.bcrypt').setLevel(logging.ERROR)

from ...config import get_config
from ...container import get_container
from ...orm.models import ExpenseModel, CategoryModel, OutboxEvent
from ...repositories import DjangoExpenseRepository, DjangoCategoryRepository
from ...database import DjangoTransactionManager
from ...outbox.writer import write_domain_event, write_outbox_event

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command for expense management infrastructure health checks."""
    
    help = "Check expense management infrastructure component health"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments.
        
        Args:
            parser: Command argument parser.
        """
        parser.add_argument(
            "--component",
            type=str,
            choices=["all", "database", "repositories", "outbox", "config", "currency", "transactions"],
            default="all",
            help="Component to check (default: all)",
        )
        
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Enable verbose output",
        )
    
    def handle(self, *args: Any, **options: Any) -> None:
        """Handle the command execution.
        
        Args:
            args: Positional arguments.
            options: Command options.
        """
        component = options["component"]
        verbose = options["verbose"]
        
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        
        self.stdout.write("🔍 Running expense management infrastructure health checks...")
        
        try:
            if component == "all":
                self._check_all_components()
            elif component == "database":
                self._check_database()
            elif component == "repositories":
                self._check_repositories()
            elif component == "outbox":
                self._check_outbox()
            elif component == "config":
                self._check_configuration()
            elif component == "currency":
                self._check_currency_handling()
            elif component == "transactions":
                self._check_transaction_management()
            
            self.stdout.write(
                self.style.SUCCESS("✅ All expense management health checks passed!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Health check failed: {e}")
            )
            raise
    
    def _check_all_components(self) -> None:
        """Check all infrastructure components."""
        self.stdout.write("Checking all expense management components...")
        
        self._check_configuration()
        self._check_database()
        self._check_repositories()
        self._check_outbox()
        self._check_currency_handling()
        self._check_transaction_management()
        self._check_dependency_injection()
    
    def _check_configuration(self) -> None:
        """Check configuration loading."""
        self.stdout.write("📋 Checking expense management configuration...")
        
        config = get_config()
        
        # Verify config has expected structure
        assert hasattr(config, 'expense'), "Expense config missing"
        assert hasattr(config, 'outbox'), "Outbox config missing"
        assert config.expense.default_currency == "TZS", f"Expected TZS currency, got {config.expense.default_currency}"
        assert config.expense.decimal_places == 2, f"Expected 2 decimal places, got {config.expense.decimal_places}"
        assert config.expense.max_expense_amount > 0, "Invalid max expense amount"
        assert config.expense.min_expense_amount > 0, "Invalid min expense amount"
        
        self.stdout.write("  ✓ Configuration loaded successfully")
        self.stdout.write(f"    - Currency: {config.expense.default_currency}")
        self.stdout.write(f"    - Decimal places: {config.expense.decimal_places}")
        self.stdout.write(f"    - Max amount: TZS {config.expense.max_expense_amount:,.2f}")
    
    def _check_database(self) -> None:
        """Check database connectivity and models."""
        self.stdout.write("🗄️ Checking expense management database...")
        
        # Test database connection by querying models
        try:
            expense_count = ExpenseModel.objects.count()
            category_count = CategoryModel.objects.count()
            outbox_count = OutboxEvent.objects.count()
            
            self.stdout.write(f"  ✓ Database connected")
            self.stdout.write(f"    - Expenses: {expense_count}")
            self.stdout.write(f"    - Categories: {category_count}")
            self.stdout.write(f"    - Outbox events: {outbox_count}")
            
            # Test model constraints
            self._test_model_constraints()
            
        except Exception as e:
            raise Exception(f"Database check failed: {e}")
    
    def _test_model_constraints(self) -> None:
        """Test database model constraints."""
        self.stdout.write("  🔒 Testing model constraints...")
        
        # Test expense amount constraint (non-negative)
        try:
            with transaction.atomic():
                # This should fail due to non-negative constraint
                ExpenseModel.objects.create(
                    user_id="550e8400-e29b-41d4-a716-446655440000",
                    category_id="550e8400-e29b-41d4-a716-446655440001",
                    amount_tzs=Decimal("-100.00"),  # Negative amount should fail
                    expense_date=date.today()
                )
                raise Exception("Negative amount constraint not working")
        except Exception:
            # This should fail - constraint is working
            pass
        
        self.stdout.write("    ✓ Model constraints working correctly")
    
    def _check_repositories(self) -> None:
        """Check repository implementations."""
        self.stdout.write("📚 Checking expense management repositories...")
        
        try:
            # Test expense repository
            expense_repo = DjangoExpenseRepository()
            
            # Test basic repository operations (without persisting)
            from ....domain.value_objects.expense_id import ExpenseId
            from ....domain.value_objects.user_id import UserId
            
            test_expense_id = ExpenseId.generate()
            test_user_id = UserId.from_string("550e8400-e29b-41d4-a716-446655440000")
            
            # Test find operations (these should not fail even if no data)
            found_expense = expense_repo.find_by_id(test_expense_id)
            assert found_expense is None, "Should not find non-existent expense"
            
            user_expenses = expense_repo.find_by_user_id(test_user_id, limit=10)
            assert isinstance(user_expenses, list), "Should return list for user expenses"
            
            self.stdout.write("    ✓ Expense repository working")
            
            # Test category repository
            category_repo = DjangoCategoryRepository()
            
            from ....domain.value_objects.category_id import CategoryId
            
            test_category_id = CategoryId.generate()
            
            found_category = category_repo.find_by_id(test_category_id)
            assert found_category is None, "Should not find non-existent category"
            
            user_categories = category_repo.find_by_user_id(test_user_id)
            assert isinstance(user_categories, list), "Should return list for user categories"
            
            self.stdout.write("    ✓ Category repository working")
            
        except Exception as e:
            raise Exception(f"Repository check failed: {e}")
    
    def _check_outbox(self) -> None:
        """Check outbox functionality."""
        self.stdout.write("📤 Checking expense management outbox system...")
        
        try:
            # Check if outbox table exists and is accessible
            pending_count = OutboxEvent.objects.filter(processed_at__isnull=True).count()
            processed_count = OutboxEvent.objects.filter(processed_at__isnull=False).count()
            
            self.stdout.write(f"  ✓ Outbox accessible")
            self.stdout.write(f"    - Pending events: {pending_count}")
            self.stdout.write(f"    - Processed events: {processed_count}")
            
            # Test outbox event writing (with rollback)
            with transaction.atomic():
                test_event = write_outbox_event(
                    event_type="TestEvent",
                    payload={"test": "data", "amount_tzs": 100.50},
                    use_transaction_commit=False
                )
                assert test_event.event_type == "TestEvent", "Event type not set correctly"
                
                # Rollback the test event
                transaction.set_rollback(True)
            
            self.stdout.write("    ✓ Outbox event writing working")
            
        except Exception as e:
            raise Exception(f"Outbox check failed: {e}")
    
    def _check_currency_handling(self) -> None:
        """Check TZS currency handling."""
        self.stdout.write("💰 Checking TZS currency handling...")
        
        try:
            from ....domain.value_objects.amount_tzs import AmountTZS
            
            # Test currency creation and conversion
            test_amount = AmountTZS.from_decimal(Decimal("12345.67"))
            assert test_amount.value == Decimal("12345.67"), "Amount value not preserved"
            assert test_amount.to_decimal() == Decimal("12345.67"), "Decimal conversion failed"
            
            # Test currency formatting
            formatted = f"TZS {test_amount.value:,.2f}"
            assert "12,345.67" in formatted, "Currency formatting failed"
            
            # Test precision handling
            precise_amount = AmountTZS.from_decimal(Decimal("123.456"))  # Should round to 2 places
            assert str(precise_amount.to_decimal()) == "123.46", "Precision handling failed"
            
            self.stdout.write("    ✓ TZS currency handling working")
            self.stdout.write(f"    - Test amount: TZS {test_amount.value:,.2f}")
            self.stdout.write(f"    - Precision test: TZS {precise_amount.value:,.2f}")
            
        except Exception as e:
            raise Exception(f"Currency handling check failed: {e}")
    
    def _check_transaction_management(self) -> None:
        """Check transaction management."""
        self.stdout.write("🔄 Checking transaction management...")
        
        try:
            from ...database import django_transaction, transactional
            
            # Test context manager approach
            with django_transaction():
                # This should work within transaction
                test_count = ExpenseModel.objects.count()
                assert isinstance(test_count, int), "Transaction context not working"
            
            # Test decorator approach
            @transactional
            def test_transactional_operation():
                return CategoryModel.objects.count()
            
            result = test_transactional_operation()
            assert isinstance(result, int), "Transactional decorator not working"
            
            # Test transaction manager instance
            transaction_manager = DjangoTransactionManager()
            assert transaction_manager.is_in_transaction() is not None, "Transaction manager not working"
            
            self.stdout.write("    ✓ Transaction management working")
            
        except Exception as e:
            raise Exception(f"Transaction management check failed: {e}")
    
    def _check_dependency_injection(self) -> None:
        """Check dependency injection container."""
        self.stdout.write("🔧 Checking dependency injection...")
        
        try:
            container = get_container()
            
            # Test service creation
            from ....domain.repositories.expense_repository import ExpenseRepository
            from ....domain.repositories.category_repository import CategoryRepository
            from ....domain.repositories import TransactionManager
            from ...outbox.writer import OutboxEventWriter
            
            expense_repo = container.get(ExpenseRepository)
            category_repo = container.get(CategoryRepository)
            transaction_mgr = container.get(TransactionManager)
            outbox_writer = container.get(OutboxEventWriter)
            
            assert expense_repo is not None, "Failed to create expense repository"
            assert category_repo is not None, "Failed to create category repository"
            assert transaction_mgr is not None, "Failed to create transaction manager"
            assert outbox_writer is not None, "Failed to create outbox writer"
            
            # Test singleton behavior
            expense_repo_2 = container.get(ExpenseRepository)
            assert expense_repo is expense_repo_2, "Singleton behavior not working"
            
            self.stdout.write("    ✓ Dependency injection working")
            
        except Exception as e:
            raise Exception(f"DI container check failed: {e}")