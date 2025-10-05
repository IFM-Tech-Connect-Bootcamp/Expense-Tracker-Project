"""Default password policy implementation.

This module provides a concrete implementation of the PasswordPolicy
domain service interface with configurable password requirements.
"""

from __future__ import annotations

import re
from typing import Optional

from ...domain.errors import PasswordPolicyError


class DefaultPasswordPolicy:
    """Default password policy implementation.
    
    This implementation enforces common password security requirements:
    - Minimum length (configurable, default 8 characters)
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter  
    - Contains at least one digit
    - Contains at least one special character
    - Not in common password blacklist
    """
    
    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_digits: bool = True,
        require_special_chars: bool = True,
        special_chars: str = "!@#$%^&*()_+-=[]{}|;:,.<>?",
        blacklist: Optional[list[str]] = None,
    ) -> None:
        """Initialize password policy.
        
        Args:
            min_length: Minimum password length.
            require_uppercase: Whether uppercase letters are required.
            require_lowercase: Whether lowercase letters are required.
            require_digits: Whether digits are required.
            require_special_chars: Whether special characters are required.
            special_chars: String of allowed special characters.
            blacklist: List of forbidden passwords.
        """
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_digits = require_digits
        self.require_special_chars = require_special_chars
        self.special_chars = special_chars
        self.blacklist = blacklist or self._default_blacklist()
    
    async def validate_password_strength(self, password: str) -> None:
        """Validate that a password meets strength requirements.
        
        Args:
            password: The plain text password to validate.
            
        Raises:
            PasswordPolicyError: If the password doesn't meet requirements.
        """
        errors = []
        
        # Check minimum length
        if len(password) < self.min_length:
            errors.append(f"Password must be at least {self.min_length} characters long")
        
        # Check for uppercase letters
        if self.require_uppercase and not re.search(r'[A-Z]', password):
            errors.append("Password must contain at least one uppercase letter")
        
        # Check for lowercase letters
        if self.require_lowercase and not re.search(r'[a-z]', password):
            errors.append("Password must contain at least one lowercase letter")
        
        # Check for digits
        if self.require_digits and not re.search(r'\d', password):
            errors.append("Password must contain at least one digit")
        
        # Check for special characters
        if self.require_special_chars:
            special_char_pattern = f'[{re.escape(self.special_chars)}]'
            if not re.search(special_char_pattern, password):
                errors.append(f"Password must contain at least one special character: {self.special_chars}")
        
        # Check against blacklist
        if password.lower() in [p.lower() for p in self.blacklist]:
            errors.append("Password is too common and not allowed")
        
        # Check for repeated characters
        if self._has_excessive_repetition(password):
            errors.append("Password cannot have more than 3 consecutive identical characters")
        
        # Check for common patterns
        if self._has_common_patterns(password):
            errors.append("Password cannot contain common patterns like '123', 'abc', or 'qwerty'")
        
        if errors:
            raise PasswordPolicyError(
                "Password does not meet security requirements",
                details={"errors": errors, "requirements": self._get_requirements_description()}
            )
    
    def _has_excessive_repetition(self, password: str) -> bool:
        """Check if password has more than 3 consecutive identical characters.
        
        Args:
            password: Password to check.
            
        Returns:
            True if password has excessive repetition.
        """
        for i in range(len(password) - 3):
            if password[i] == password[i + 1] == password[i + 2] == password[i + 3]:
                return True
        return False
    
    def _has_common_patterns(self, password: str) -> bool:
        """Check if password contains common patterns.
        
        Args:
            password: Password to check.
            
        Returns:
            True if password contains common patterns.
        """
        common_patterns = [
            '123', '234', '345', '456', '567', '678', '789', '890',
            'abc', 'bcd', 'cde', 'def', 'efg', 'fgh', 'ghi', 'hij',
            'qwerty', 'qwert', 'asdf', 'asdfg', 'zxcv', 'zxcvb',
            'password', 'admin', 'login', 'user', 'guest'
        ]
        
        password_lower = password.lower()
        for pattern in common_patterns:
            if pattern in password_lower:
                return True
        return False
    
    def _get_requirements_description(self) -> dict[str, any]:
        """Get description of password requirements.
        
        Returns:
            Dictionary describing password requirements.
        """
        return {
            "min_length": self.min_length,
            "require_uppercase": self.require_uppercase,
            "require_lowercase": self.require_lowercase,
            "require_digits": self.require_digits,
            "require_special_chars": self.require_special_chars,
            "allowed_special_chars": self.special_chars,
            "forbidden_patterns": "Common patterns like '123', 'abc', 'qwerty' are not allowed",
            "repetition_limit": "No more than 3 consecutive identical characters",
        }
    
    def _default_blacklist(self) -> list[str]:
        """Get default list of forbidden passwords.
        
        Returns:
            List of common passwords to reject.
        """
        return [
            "password", "password1", "password123", "12345678", "123456789",
            "qwerty", "qwerty123", "admin", "administrator", "root", "user",
            "guest", "login", "welcome", "default", "changeme", "letmein",
            "monkey", "dragon", "princess", "football", "baseball", "basketball",
            "superman", "batman", "master", "jordan", "harley", "ranger",
            "jennifer", "hannah", "michelle", "matthew", "daniel", "andrew",
            "joshua", "robert", "jessica", "sunshine", "shadow", "soccer",
            "anthony", "friends", "butterfly", "purple", "michael", "nicole",
            "justin", "yellow", "summer", "internet", "service", "canada",
        ]


class LenientPasswordPolicy:
    """Lenient password policy for development/testing.
    
    This policy only enforces a minimum length requirement
    and is suitable for development environments where
    strict password requirements might be inconvenient.
    """
    
    def __init__(self, min_length: int = 6) -> None:
        """Initialize lenient password policy.
        
        Args:
            min_length: Minimum password length.
        """
        self.min_length = min_length
    
    async def validate_password_strength(self, password: str) -> None:
        """Validate that a password meets minimum requirements.
        
        Args:
            password: The plain text password to validate.
            
        Raises:
            PasswordPolicyError: If the password is too short.
        """
        if len(password) < self.min_length:
            raise PasswordPolicyError(
                f"Password must be at least {self.min_length} characters long",
                details={"min_length": self.min_length, "actual_length": len(password)}
            )


class StrictPasswordPolicy(DefaultPasswordPolicy):
    """Strict password policy for high-security environments.
    
    This policy enforces more stringent requirements including
    longer minimum length and additional security checks.
    """
    
    def __init__(self) -> None:
        """Initialize strict password policy."""
        super().__init__(
            min_length=12,
            require_uppercase=True,
            require_lowercase=True,
            require_digits=True,
            require_special_chars=True,
        )
    
    async def validate_password_strength(self, password: str) -> None:
        """Validate password with strict requirements.
        
        Args:
            password: The plain text password to validate.
            
        Raises:
            PasswordPolicyError: If password doesn't meet strict requirements.
        """
        # Run base validation
        super().validate_password_strength(password)
        
        errors = []
        
        # Additional strict requirements
        if len(set(password)) < 8:
            errors.append("Password must contain at least 8 unique characters")
        
        # Check for mixed case within first 8 characters (common requirement)
        first_part = password[:8]
        if not (any(c.isupper() for c in first_part) and any(c.islower() for c in first_part)):
            errors.append("Password must have mixed case within the first 8 characters")
        
        if errors:
            raise PasswordPolicyError(
                "Password does not meet strict security requirements",
                details={"errors": errors, "policy_type": "strict"}
            )