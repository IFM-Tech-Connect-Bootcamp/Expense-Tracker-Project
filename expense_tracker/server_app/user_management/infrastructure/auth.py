# usermanagement/infrastructure/auth.py
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime
from ..domain.entities import User
from ..domain.value_objects import UserId
from datetime import timedelta
import jwt
from django.conf import settings

# This would typically be defined as an interface in domain/repositories.py
class AuthService:
    def hash_password(self, plain_password: str) -> str:
        # Uses Django's secure hashing (often PBKDF2, can be configured to bcrypt)
        # Note: Django's make_password handles salting and algorithm prefix
        return make_password(plain_password, salt=None, hasher='bcrypt') # Enforce bcrypt

    def verify_password(self, password_hash: str, plain_password: str) -> bool:
        return check_password(plain_password, password_hash)

    def sign_token(self, user: User) -> dict:
        # Manually craft access and refresh token payloads since we are NOT using Django's Auth User model
        access_payload = {
            'user_id': str(user.user_id.value),
            'email': user.email.value,
            'exp': datetime.utcnow() + timedelta(hours=24),  # Access token expiry
            'iat': datetime.utcnow(),
        }

        refresh_payload = {
            'user_id': str(user.user_id.value),
            'email': user.email.value,
            'exp': datetime.utcnow() + timedelta(days=7),  # Refresh token expiry
            'iat': datetime.utcnow(),
            'type': 'refresh',
        }

        access_token = jwt.encode(access_payload, settings.SECRET_KEY, algorithm='HS256')
        refresh_token = jwt.encode(refresh_payload, settings.SECRET_KEY, algorithm='HS256')

        return {
            'access': access_token,
            'refresh': refresh_token,
        }

    # ... verifyToken method needed for custom middleware/DRF permission