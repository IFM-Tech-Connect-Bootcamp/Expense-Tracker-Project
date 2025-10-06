"""Repository interfaces for User Management domain.

This package contains the repository interfaces that define how
the domain interacts with persistent storage.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    pass

__all__ = ["UserRepository"]