"""Django management command for infrastructure health checks.

This command verifies that all infrastructure components are working
correctly and can connect to external dependencies.
"""

import asyncio
import logging
from typing import Any

from django.core.management.base import BaseCommand, CommandParser

from ...adapters import create_password_service, create_token_service
from ...config import get_config
from ...container import get_container
from ...orm.models import OutboxEvent, UserModel


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Management command for infrastructure health checks."""
    
    help = "Check infrastructure component health"
    
    def add_arguments(self, parser: CommandParser) -> None:
        """Add command arguments.
        
        Args:
            parser: Command argument parser.
        """
        parser.add_argument(
            "--component",
            type=str,
            choices=["all", "database", "auth", "outbox", "config"],
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
        
        self.stdout.write("🔍 Running infrastructure health checks...")
        
        try:
            if component == "all":
                self._check_all_components()
            elif component == "database":
                self._check_database()
            elif component == "auth":
                asyncio.run(self._check_auth_services())
            elif component == "outbox":
                self._check_outbox()
            elif component == "config":
                self._check_configuration()
            
            self.stdout.write(
                self.style.SUCCESS("✅ All health checks passed!")
            )
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"❌ Health check failed: {e}")
            )
            raise
    
    def _check_all_components(self) -> None:
        """Check all infrastructure components."""
        self.stdout.write("Checking all components...")
        
        self._check_configuration()
        self._check_database()
        asyncio.run(self._check_auth_services())
        self._check_outbox()
        self._check_dependency_injection()
    
    def _check_configuration(self) -> None:
        """Check configuration loading."""
        self.stdout.write("📋 Checking configuration...")
        
        config = get_config()
        
        # Verify config has expected structure
        assert hasattr(config, 'auth'), "Auth config missing"
        assert hasattr(config, 'outbox'), "Outbox config missing"
        assert config.auth.jwt_secret_key, "JWT secret key not configured"
        assert config.auth.bcrypt_rounds > 0, "Invalid bcrypt rounds"
        
        self.stdout.write("  ✓ Configuration loaded successfully")
    
    def _check_database(self) -> None:
        """Check database connectivity and models."""
        self.stdout.write("🗄️  Checking database...")
        
        # Test database connection by querying models
        try:
            user_count = UserModel.objects.count()
            outbox_count = OutboxEvent.objects.count()
            
            self.stdout.write(f"  ✓ Database connected ({user_count} users, {outbox_count} outbox events)")
            
        except Exception as e:
            raise Exception(f"Database check failed: {e}")
    
    async def _check_auth_services(self) -> None:
        """Check authentication services."""
        self.stdout.write("🔐 Checking authentication services...")
        
        # Test password service
        password_service = create_password_service()
        test_password = "TestPassword123!"
        
        try:
            hashed = await password_service.hash_password(test_password)
            assert hashed != test_password, "Password not hashed"
            
            verified = await password_service.verify_password(test_password, hashed)
            assert verified is True, "Password verification failed"
            
            self.stdout.write("  ✓ Password service working")
            
        except Exception as e:
            raise Exception(f"Password service check failed: {e}")
        
        # Test token service
        token_service = create_token_service()
        test_user_id = "550e8400-e29b-41d4-a716-446655440000"
        
        try:
            token = await token_service.generate_token(test_user_id)
            assert token, "Token not generated"
            
            verified_id = await token_service.verify_token(token)
            assert verified_id == test_user_id, "Token verification failed"
            
            self.stdout.write("  ✓ Token service working")
            
        except Exception as e:
            raise Exception(f"Token service check failed: {e}")
    
    def _check_outbox(self) -> None:
        """Check outbox functionality."""
        self.stdout.write("📤 Checking outbox system...")
        
        # Check if outbox table exists and is accessible
        try:
            pending_count = OutboxEvent.objects.filter(status='pending').count()
            failed_count = OutboxEvent.objects.filter(status='failed').count()
            
            self.stdout.write(f"  ✓ Outbox accessible ({pending_count} pending, {failed_count} failed)")
            
        except Exception as e:
            raise Exception(f"Outbox check failed: {e}")
    
    def _check_dependency_injection(self) -> None:
        """Check dependency injection container."""
        self.stdout.write("🔧 Checking dependency injection...")
        
        try:
            container = get_container()
            
            # Test service creation
            from ...auth.bcrypt_hasher import BcryptPasswordHasher
            from ...auth.jwt_provider import JWTTokenProvider
            from ...auth.password_policy import DefaultPasswordPolicy
            
            hasher = container.get(BcryptPasswordHasher)
            provider = container.get(JWTTokenProvider)
            policy = container.get(DefaultPasswordPolicy)
            
            assert hasher is not None, "Failed to create password hasher"
            assert provider is not None, "Failed to create token provider"
            assert policy is not None, "Failed to create password policy"
            
            self.stdout.write("  ✓ Dependency injection working")
            
        except Exception as e:
            raise Exception(f"DI container check failed: {e}")