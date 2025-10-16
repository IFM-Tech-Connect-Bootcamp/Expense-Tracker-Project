from dataclasses import dataclass
from typing import Optional


@dataclass
class ExpenseDTO:
    """Data transfer object representing an expense for application layer.

    Fields are kept primitive (str, int) so presentation and infrastructure
    layers can map them to domain value objects or ORM models.
    """
    expense_id: Optional[str]
    user_id: str
    amount_tzs: float
    description: Optional[str]
    date: str  # ISO date string
    category_id: Optional[str] = None
