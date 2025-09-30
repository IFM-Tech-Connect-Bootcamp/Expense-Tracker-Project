# usermanagement/domain/entities.py
from .value_objects import UserId, Email, Password
from datetime import datetime
from typing import Optional

class User :
    def __init__(
        self,
        user_id: UserId,
        email: Email,
        password: Password, # The stored hash
        name: Optional[str] = None,
        created_at: Optional[datetime] = None,
        is_active: bool = True,
    ):
        self.user_id = user_id
        self.email = email
        self._password = password
        self.name = name
        self.created_at = created_at or datetime.utcnow()
        self.is_active = is_active

    @property
    def password(self) -> Password:
        return self._password

    # Business Logic from Requirements
    def update_profile(self, new_email: Email, new_name: str):
        self.email = new_email
        self.name = new_name

    def change_password(self, new_password_hash: str):
        # This is called *after* old password verification by the UserService
        self._password = Password(hash=new_password_hash)

    def deactivate(self):
        self.is_active = False

    # Used for communicating the User to other contexts (Value Object)
    @property
    def public_id(self) -> UserId:
        return self.user_id