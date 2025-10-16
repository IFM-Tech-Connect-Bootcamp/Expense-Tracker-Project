from dataclasses import dataclass
from typing import Optional


@dataclass
class CreateExpenseCommand:
    user_id: str
    amount_tzs: int
    description: Optional[str]
    date: str
    category_id: Optional[str] = None


@dataclass
class UpdateExpenseCommand:
    expense_id: str
    user_id: str
    amount_tzs: Optional[int] = None
    description: Optional[str] = None
    date: Optional[str] = None
    category_id: Optional[str] = None
