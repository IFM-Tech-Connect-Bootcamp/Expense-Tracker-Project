"""AmountTZS value object with validation."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import ClassVar, Self


@dataclass(frozen=True, slots=True)
class AmountTZS:
    """A value object representing an amount in Tanzanian Shillings (TZS).
    
    This class ensures that the amount is a non-negative number with up to two decimal places.
    """
    
    value: float
    AMOUNT_REGEX: ClassVar[re.Pattern] = re.compile(r"^\d+(\.\d{1,2})?$")
    
    
    
    def __post_init__(self) -> None:
        """Validate the amount value."""
        if not isinstance(self.value, (int, float)):
            raise TypeError("AmountTZS value must be a number")
        if self.value < 0:
            raise ValueError("AmountTZS value must be non-negative")
        if not self.AMOUNT_REGEX.match(f"{self.value:.2f}"):
            raise ValueError("AmountTZS value must have at most two decimal places")
    
    
    
    @classmethod
    def from_string(cls, value: str) -> Self:
        """Create an AmountTZS from a string representation.
        
        Args:
            value: String representation of the amount.
            
        Returns:
            AmountTZS instance.
            
        Raises:
            ValueError: If the string is not a valid amount.
        """
        try:
            amount = float(value)
            return cls(amount)
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid amount string: {value}") from e