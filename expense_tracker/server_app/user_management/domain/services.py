# usermanagement/domain/services.py

from typing import Optional
from .entities import User
from .value_objects import UserId, Email, Password
from .repositories import UserRepository
# We rely on an Interface/ABC for AuthService, but use the concrete class for type hinting
# In a real setup, we'd inject an abstract AuthService.
from abc import ABC, abstractmethod

# ----------------------------------------------------
# Define the AuthService Interface (for dependency injection purity)
# ----------------------------------------------------
class AbstractAuthService(ABC):
    @abstractmethod
    def hash_password(self, plain: str) -> str:
        pass
    
    @abstractmethod
    def verify_password(self, hash: str, plain: str) -> bool:
        pass

    @abstractmethod
    def sign_token(self, user: User) -> dict:
        pass
# ----------------------------------------------------

# Note: In the infrastructure/auth.py, the concrete AuthService will implement AbstractAuthService

class UserService:
    def __init__(self, user_repo: UserRepository, auth_service: AbstractAuthService):
        self._repo = user_repo
        self._auth_service = auth_service

    # --- 1. Register a new user ---
    def register(self, email: Email, plain_password: str, name: Optional[str]) -> User:
        # Constraint: Unique Email Check
        if self._repo.find_by_email(email):
            raise ValueError("Email is already registered.")

        # Infrastructure: Hash the password
        password_hash = self._auth_service.hash_password(plain_password)
        password = Password(hash=password_hash)

        # Domain: Create the new User entity
        new_user = User(
            user_id=UserId(),
            email=email,
            password=password,
            name=name,
            is_active=True,
        )

        # Infrastructure: Persist the entity
        self._repo.save(new_user)
        return new_user

    # --- 2. Authenticate existing user (Login) ---
    def authenticate(self, email: Email, plain_password: str) -> dict:
        user = self._repo.find_by_email(email)

        if not user or not user.is_active:
            raise ValueError("Invalid credentials or inactive account.")

        # Infrastructure: Verify password
        if not self._auth_service.verify_password(user.password.hash, plain_password):
            raise ValueError("Invalid credentials.")
        
        # Infrastructure: Generate token
        token_data = self._auth_service.sign_token(user)
        return token_data

    # --- 3. Update user profile ---
    def update_profile(self, user_id: UserId, new_email: Optional[Email], new_name: Optional[str]) -> User:
        user = self._repo.find_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive.")

        final_email = new_email if new_email else user.email
        final_name = new_name if new_name is not None else user.name
        
        # Constraint: Unique Email Check if email is changing
        if final_email.value != user.email.value:
            if self._repo.find_by_email(final_email):
                raise ValueError("New email is already taken.")

        # Domain: Apply changes to the entity
        user.update_profile(final_email, final_name if final_name is not None else "")

        # Infrastructure: Persist changes
        self._repo.update(user)
        return user

    # --- 4. Change password ---
    def change_password(self, user_id: UserId, old_password: str, new_password: str) -> User:
        user = self._repo.find_by_id(user_id)
        if not user or not user.is_active:
            raise ValueError("User not found or inactive.")

        # Acceptance Criteria: Must verify old password
        if not self._auth_service.verify_password(user.password.hash, old_password):
            raise ValueError("Old password verification failed.")

        # Infrastructure: Hash the new password
        new_password_hash = self._auth_service.hash_password(new_password)
        
        # Domain: Apply changes to the entity
        user.change_password(new_password_hash)

        # Infrastructure: Persist changes
        self._repo.update(user)
        return user

    # --- 5. Deactivate user account (Soft Delete) ---
    def deactivate_user(self, user_id: UserId) -> User:
        user = self._repo.find_by_id(user_id)
        if not user:
            raise ValueError("User not found.")

        # Domain: Apply changes to the entity
        user.deactivate()

        # Infrastructure: Persist changes (updates is_active = False)
        self._repo.update(user)
        return user