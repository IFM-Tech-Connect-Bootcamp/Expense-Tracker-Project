"""Value objects for the User Management domain."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

__all__ = ["UserId", "Email", "PasswordHash", "FirstName", "LastName"]