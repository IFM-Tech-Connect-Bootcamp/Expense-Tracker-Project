# usermanagement/presentation/api_views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.conf import settings # For dependency injection

# Imports for Dependency Injection (DI)
from ..domain.repositories import UserRepository
from ..infrastructure.persistence import UserRepositoryImpl
from ..infrastructure.auth import AuthService
from ..application.use_cases import (
    RegisterUserHandler, RegisterUserRequest #,
    #AuthenticateUserHandler, AuthenticateUserRequest
)
from .serializers import RegisterSerializer, LoginSerializer

# --- DI Setup (Example: In a real project, use a DI container) ---
def get_user_repo() -> UserRepository:
    return UserRepositoryImpl()
def get_auth_service() -> AuthService:
    return AuthService()
# ------------------------------------------------------------------

class RegisterView(APIView):
    serializer_class = RegisterSerializer
    # Allow unauthenticated access
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Dependency Injection & Execution
        handler = RegisterUserHandler(
            user_repo=get_user_repo(),
            auth_service=get_auth_service()
        )
        
        try:
            # Map validated data to Application Request object
            req = RegisterUserRequest(**serializer.validated_data) # type: ignore
            user_id = handler.execute(req)
            return Response(
                {"user_id": str(user_id.value), "message": "User registered successfully."},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            # Handle unique email, password strength, etc. errors here
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# ... (Implement LoginView, ProfileUpdateView, etc., similarly)