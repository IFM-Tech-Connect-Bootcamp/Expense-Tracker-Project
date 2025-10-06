"""AmountTZS value object for Tanzanian Shillings amounts.

This module contains the AmountTZS value object for monetary amounts in TZS.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from typing import Self


@dataclass(frozen=True, slots=True)
class AmountTZS:
    """A monetary amount in Tanzanian Shillings (TZS).
    
    This value object ensures all monetary values are properly validated,
    formatted, and constrained to 2 decimal places as appropriate for currency.
    """
    
    value: Decimal
    
    def __post_init__(self) -> None:
        """Validate the amount after initialization."""
        if not isinstance(self.value, Decimal):
            raise TypeError("Amount value must be a Decimal instance")
        
        if self.value < 0:
            raise ValueError("Amount cannot be negative")
        
        # Ensure proper precision for currency (2 decimal places)
        quantized = self.value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        object.__setattr__(self, 'value', quantized)
    
    @classmethod
    def from_float(cls, amount: float) -> Self:
        """Create AmountTZS from float value.
        
        Args:
            amount: Float amount to convert.
            
        Returns:
            AmountTZS instance.
            
        Raises:
            ValueError: If amount is negative.
        """
        return cls(value=Decimal(str(amount)))
    
    @classmethod
    def from_string(cls, amount: str) -> Self:
        """Create AmountTZS from string value.
        
        Args:
            amount: String amount to convert.
            
        Returns:
            AmountTZS instance.
            
        Raises:
            ValueError: If amount is invalid or negative.
        """
        try:
            return cls(value=Decimal(amount))
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid amount string: {amount}") from e
    
    @classmethod
    def zero(cls) -> Self:
        """Create a zero amount.
        
        Returns:
            AmountTZS instance with value of 0.00.
        """
        return cls(value=Decimal('0.00'))
    
    def add(self, other: AmountTZS) -> Self:
        """Add two amounts together.
        
        Args:
            other: Another AmountTZS to add.
            
        Returns:
            New AmountTZS with the sum.
        """
        if not isinstance(other, AmountTZS):
            raise TypeError("Can only add AmountTZS to AmountTZS")
        return AmountTZS(value=self.value + other.value)
    
    def subtract(self, other: AmountTZS) -> Self:
        """Subtract another amount from this amount.
        
        Args:
            other: Another AmountTZS to subtract.
            
        Returns:
            New AmountTZS with the difference.
            
        Raises:
            ValueError: If result would be negative.
        """
        if not isinstance(other, AmountTZS):
            raise TypeError("Can only subtract AmountTZS from AmountTZS")
        
        result = self.value - other.value
        return AmountTZS(value=result)  # Will raise ValueError if negative
    
    def multiply(self, factor: Decimal | int | float) -> Self:
        """Multiply amount by a factor.
        
        Args:
            factor: Factor to multiply by.
            
        Returns:
            New AmountTZS with the product.
        """
        if isinstance(factor, (int, float)):
            factor = Decimal(str(factor))
        elif not isinstance(factor, Decimal):
            raise TypeError("Factor must be Decimal, int, or float")
        
        return AmountTZS(value=self.value * factor)
    
    def divide(self, divisor: Decimal | int | float) -> Self:
        """Divide amount by a divisor.
        
        Args:
            divisor: Value to divide by.
            
        Returns:
            New AmountTZS with the quotient.
            
        Raises:
            ValueError: If divisor is zero.
        """
        if isinstance(divisor, (int, float)):
            divisor = Decimal(str(divisor))
        elif not isinstance(divisor, Decimal):
            raise TypeError("Divisor must be Decimal, int, or float")
        
        if divisor == 0:
            raise ValueError("Cannot divide by zero")
        
        return AmountTZS(value=self.value / divisor)
    
    def is_zero(self) -> bool:
        """Check if amount is zero.
        
        Returns:
            True if amount is zero, False otherwise.
        """
        return self.value == Decimal('0.00')
    
    def to_float(self) -> float:
        """Convert to float for serialization.
        
        Returns:
            Float representation of the amount.
        """
        return float(self.value)
    
    def __str__(self) -> str:
        """Return formatted string representation."""
        return f"TZS {self.value:,.2f}"
    
    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"AmountTZS({self.value!r})"
    
    def __eq__(self, other: object) -> bool:
        """Check equality with another AmountTZS."""
        if not isinstance(other, AmountTZS):
            return NotImplemented
        return self.value == other.value
    
    def __lt__(self, other: AmountTZS) -> bool:
        """Check if this amount is less than another."""
        if not isinstance(other, AmountTZS):
            return NotImplemented
        return self.value < other.value
    
    def __le__(self, other: AmountTZS) -> bool:
        """Check if this amount is less than or equal to another."""
        if not isinstance(other, AmountTZS):
            return NotImplemented
        return self.value <= other.value
    
    def __gt__(self, other: AmountTZS) -> bool:
        """Check if this amount is greater than another."""
        if not isinstance(other, AmountTZS):
            return NotImplemented
        return self.value > other.value
    
    def __ge__(self, other: AmountTZS) -> bool:
        """Check if this amount is greater than or equal to another."""
        if not isinstance(other, AmountTZS):
            return NotImplemented
        return self.value >= other.value