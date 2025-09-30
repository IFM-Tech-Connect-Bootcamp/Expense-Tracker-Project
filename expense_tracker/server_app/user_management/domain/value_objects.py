# usermanagement/domain/value_objects.py
import uuid
import re
from dataclasses import dataclass, field

@dataclass(frozen=True)
class UserId:
    value: uuid.UUID = field(default_factory=uuid.uuid4)

    def __post_init__(self):
        if not isinstance(self.value, uuid.UUID):
            raise ValueError("UserId must be a valid UUID.")

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        # Basic validation
        if not re.match(r"[^@]+@[^@]+\.[^@]+", self.value):
            raise ValueError("Invalid email format.")
        # Normalize email
        object.__setattr__(self, 'value', self.value.lower())

@dataclass(frozen=True)
class Password:
    hash: str # Stores the bcrypt hash

    # Methods like verify() and fromPlain() will call AuthService for infrastructure details
    # This keeps the Domain pure.
    # Note: For MVP, we might simplify this to a single string field on the User entity
    # and rely on the Service for hashing/verification to save time.
    # Sticking to the design: the hash is stored, but the service provides the logic.