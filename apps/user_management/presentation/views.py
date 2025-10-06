"""
API Views for User Management endpoints.

This module contains Django REST Framework views that handle HTTP requests
for user management operations. All views integrate with the application
layer handlers following clean architecture principles.
"""

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.http import JsonResponse
import logging
from typing import Dict, Any

from .serializers import (
    RegisterUserSerializer,
    AuthenticateUserSerializer,
    ChangePasswordSerializer,
    UpdateProfileSerializer,
    DeactivateUserSerializer,
    UserResponseSerializer,
    AuthResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)
from .authentication import get_current_user_from_request
from ..application.handlers import (
    RegisterUserHandler,
    AuthenticateUserHandler,
    ChangePasswordHandler,
    UpdateProfileHandler,
    DeactivateUserHandler,
)
from ..application.commands import (
    RegisterUserCommand,
    AuthenticateUserCommand,
    ChangePasswordCommand,
    UpdateProfileCommand,
    DeactivateUserCommand,
)
from ..application.dto import UserDTO, AuthResultDTO
from ..infrastructure.container import InfrastructureContainer
from ..infrastructure.outbox.writer import write_domain_event
from ..domain.repositories.user_repository import UserRepository
from ..domain.services.password_policy import PasswordHasher, TokenProvider
from ..domain.errors import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    InvalidOperationError,
    PasswordPolicyError,
    UserDeactivatedError,
    DomainValidationError,
)
from ..application.errors import (
    ApplicationError,
    AuthenticationFailedError,
    ValidationError,
    RegistrationFailedError,
    ProfileUpdateFailedError,
    PasswordChangeFailedError,
    UserDeactivationFailedError,
    UserNotFoundError as AppUserNotFoundError,
)


logger = logging.getLogger(__name__)


def _publish_domain_events(events):
    """
    Publish domain events to the outbox for reliable delivery.
    
    Args:
        events: List of domain events to publish
    """
    try:
        logger.info(f"Publishing {len(events)} domain events to outbox")
        for event in events:
            logger.debug(f"Publishing event: {event.__class__.__name__}")
            write_domain_event(event, use_transaction_commit=False)
        logger.info(f"Successfully published {len(events)} domain events to outbox")
    except Exception as e:
        logger.error(f"Failed to publish domain events: {str(e)}", exc_info=True)
        # Don't raise - event publishing failure shouldn't break the main flow


def _handle_domain_errors(error: Exception) -> Response:
    """
    Convert domain and application errors to appropriate HTTP responses.
    
    Args:
        error: Domain or application exception to convert
        
    Returns:
        HTTP response with appropriate status code and error message
    """
    # Handle application errors first
    if isinstance(error, AuthenticationFailedError):
        return Response(
            {"error": str(error), "code": "INVALID_CREDENTIALS"},
            status=status.HTTP_401_UNAUTHORIZED
        )
    elif isinstance(error, AppUserNotFoundError):
        return Response(
            {"error": str(error), "code": "USER_NOT_FOUND"},
            status=status.HTTP_404_NOT_FOUND
        )
    elif isinstance(error, ValidationError):
        return Response(
            {"error": str(error), "code": "VALIDATION_ERROR"},
            status=status.HTTP_400_BAD_REQUEST
        )
    elif isinstance(error, (RegistrationFailedError, ProfileUpdateFailedError, 
                           PasswordChangeFailedError, UserDeactivationFailedError)):
        return Response(
            {"error": str(error), "code": "OPERATION_FAILED"},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Handle domain errors (legacy fallback)
    error_mappings = {
        UserAlreadyExistsError: (status.HTTP_409_CONFLICT, "USER_ALREADY_EXISTS"),
        UserNotFoundError: (status.HTTP_404_NOT_FOUND, "USER_NOT_FOUND"),
        InvalidCredentialsError: (status.HTTP_401_UNAUTHORIZED, "INVALID_CREDENTIALS"),
        UserDeactivatedError: (status.HTTP_403_FORBIDDEN, "USER_DEACTIVATED"),
        InvalidOperationError: (status.HTTP_400_BAD_REQUEST, "INVALID_OPERATION"),
        PasswordPolicyError: (status.HTTP_400_BAD_REQUEST, "PASSWORD_POLICY_VIOLATION"),
        DomainValidationError: (status.HTTP_400_BAD_REQUEST, "VALIDATION_ERROR"),
    }
    
    status_code, error_code = error_mappings.get(
        type(error), 
        (status.HTTP_500_INTERNAL_SERVER_ERROR, "INTERNAL_ERROR")
    )
    
    error_data = {
        "error": str(error),
        "code": error_code,
    }
    
    if hasattr(error, 'details') and error.details:
        error_data["details"] = error.details
    
    return Response(error_data, status=status_code)


def _create_user_response_data(user_dto) -> Dict[str, Any]:
    """
    Create user response data from DTO.
    
    Args:
        user_dto: User DTO from application layer
        
    Returns:
        Dictionary with user data for response
    """
    return {
        "id": str(user_dto.id),
        "email": user_dto.email,
        "first_name": user_dto.first_name,
        "last_name": user_dto.last_name,
        "full_name": f"{user_dto.first_name} {user_dto.last_name}",
        "status": user_dto.status,
        "created_at": user_dto.created_at.isoformat() if user_dto.created_at else None,
        "updated_at": user_dto.updated_at.isoformat() if user_dto.updated_at else None,
    }


@extend_schema(
    operation_id="register_user",
    summary="Register a new user",
    description="Create a new user account with email, password, and personal information.",
    request=RegisterUserSerializer,
    responses={
        201: OpenApiResponse(
            response=UserResponseSerializer,
            description="User registered successfully"
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Validation error or password policy violation"
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="User with this email already exists"
        ),
    },
    tags=["Authentication"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def register_user(request: Request) -> Response:
    """
    Register a new user account.
    
    Creates a new user with the provided email, password, and personal information.
    The email must be unique and the password must meet policy requirements.
    """
    try:
        # Validate request data
        serializer = RegisterUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Validation failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create command
        register_command = RegisterUserCommand(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
        )
        
        # Execute use case
        container = InfrastructureContainer()
        handler = RegisterUserHandler(
            user_repository=container.get(UserRepository),
            password_service=container.get(PasswordHasher),
        )
        
        user_result = handler.handle(register_command)
        user_dto = user_result.user_dto
        
        # Publish domain events to outbox
        if hasattr(user_result, 'events') and user_result.events:
            _publish_domain_events(user_result.events)
        
        # Return response
        user_data = _create_user_response_data(user_dto)
        return Response(user_data, status=status.HTTP_201_CREATED)
        
    except (UserAlreadyExistsError, PasswordPolicyError, DomainValidationError) as e:
        return _handle_domain_errors(e)
    except Exception as e:
        logger.error(f"Unexpected error in register_user: {str(e)}")
        return Response(
            {"error": "Internal server error", "code": "INTERNAL_ERROR"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id="authenticate_user",
    summary="Authenticate user",
    description="Authenticate user credentials and return access token.",
    request=AuthenticateUserSerializer,
    responses={
        200: OpenApiResponse(
            response=AuthResponseSerializer,
            description="Authentication successful"
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid credentials"
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="User account is deactivated"
        ),
    },
    tags=["Authentication"]
)
@api_view(['POST'])
@permission_classes([AllowAny])
@csrf_exempt
def authenticate_user(request: Request) -> Response:
    """
    Authenticate user credentials and return access token.
    
    Validates the provided email and password, and returns a JWT token
    if authentication is successful.
    """
    try:
        # Validate request data
        serializer = AuthenticateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Validation failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create command
        auth_command = AuthenticateUserCommand(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
        )
        
        # Execute use case
        container = InfrastructureContainer()
        handler = AuthenticateUserHandler(
            user_repository=container.get(UserRepository),
            password_service=container.get(PasswordHasher),
            token_provider=container.get(TokenProvider),
        )
        
        auth_result = handler.handle(auth_command)
        
        # Return response
        user_data = _create_user_response_data(auth_result.user)
        response_data = {
            "user": user_data,
            "access_token": auth_result.access_token,
            "token_type": "Bearer",
            "expires_in": settings.JWT_SETTINGS['ACCESS_TOKEN_LIFETIME'],
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except (InvalidCredentialsError, UserNotFoundError, UserDeactivatedError) as e:
        return _handle_domain_errors(e)
    except (AuthenticationFailedError, AppUserNotFoundError, ValidationError, ApplicationError) as e:
        return _handle_domain_errors(e)
    except Exception as e:
        logger.error(f"Unexpected error in authenticate_user: {str(e)}")
        return Response(
            {"error": "Internal server error", "code": "INTERNAL_ERROR"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id="get_current_user",
    summary="Get current user profile",
    description="Retrieve the profile information of the authenticated user.",
    responses={
        200: OpenApiResponse(
            response=UserResponseSerializer,
            description="User profile retrieved successfully"
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Authentication required"
        ),
    },
    tags=["User Profile"]
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request: Request) -> Response:
    """
    Get the authenticated user's profile.
    
    Returns the profile information for the currently authenticated user.
    """
    try:
        # Get the authenticated user from the request
        current_user = get_current_user_from_request(request)
        if not current_user:
            return Response(
                {"error": "User not found", "code": "USER_NOT_FOUND"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create user response data
        user_data = _create_user_response_data(UserDTO(
            id=str(current_user.id.value),
            email=current_user.email.value,
            first_name=current_user.first_name.value,
            last_name=current_user.last_name.value,
            full_name=f"{current_user.first_name.value} {current_user.last_name.value}",
            status=current_user.status.value,
            created_at=current_user.created_at,
            updated_at=current_user.updated_at
        ))
        
        return Response(user_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Unexpected error in get_current_user: {str(e)}")
        return Response(
            {"error": "Internal server error", "code": "INTERNAL_ERROR"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id="update_profile",
    summary="Update user profile",
    description="Update the authenticated user's profile information.",
    request=UpdateProfileSerializer,
    responses={
        200: OpenApiResponse(
            response=UserResponseSerializer,
            description="Profile updated successfully"
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Validation error"
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Authentication required"
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Email already in use by another user"
        ),
    },
    tags=["User Profile"]
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request: Request) -> Response:
    """
    Update the authenticated user's profile.
    
    Updates the user's email, first name, and/or last name.
    At least one field must be provided for update.
    """
    try:
        # Get the authenticated user from the request
        current_user = get_current_user_from_request(request)
        if not current_user:
            return Response(
                {"error": "User not found", "code": "USER_NOT_FOUND"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate request data
        serializer = UpdateProfileSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Validation failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create command
        update_command = UpdateProfileCommand(
            user_id=str(current_user.id.value),  # Convert UserId to string
            new_email=serializer.validated_data.get('email'),
            new_first_name=serializer.validated_data.get('first_name'),
            new_last_name=serializer.validated_data.get('last_name'),
        )
        
        # Execute use case using proper handler
        container = InfrastructureContainer()
        handler = UpdateProfileHandler(
            user_repository=container.get(UserRepository),
        )
        
        update_result = handler.handle(update_command)
        
        # Publish domain events to outbox
        if hasattr(update_result, 'events') and update_result.events:
            _publish_domain_events(update_result.events)
        
        # Return response
        user_data = _create_user_response_data(update_result.user_dto)
        return Response(user_data, status=status.HTTP_200_OK)
        
    except (UserNotFoundError, UserAlreadyExistsError, DomainValidationError) as e:
        return _handle_domain_errors(e)
    except Exception as e:
        logger.error(f"Unexpected error in update_profile: {str(e)}")
        return Response(
            {"error": "Internal server error", "code": "INTERNAL_ERROR"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id="change_password",
    summary="Change user password",
    description="Change the authenticated user's password.",
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(
            response=SuccessResponseSerializer,
            description="Password changed successfully"
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Validation error or password policy violation"
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Authentication required or invalid current password"
        ),
    },
    tags=["User Profile"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request: Request) -> Response:
    """
    Change the authenticated user's password.
    
    Validates the current password and updates it with a new one
    that meets the password policy requirements.
    """
    try:
        current_user = get_current_user_from_request(request)
        if not current_user:
            return Response(
                {"error": "User not found", "code": "USER_NOT_FOUND"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate request data
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Validation failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create command
        change_password_command = ChangePasswordCommand(
            user_id=str(current_user.id.value),  # Convert UserId to string
            old_password=serializer.validated_data['old_password'],
            new_password=serializer.validated_data['new_password'],
        )
        
        # Execute use case
        container = InfrastructureContainer()
        handler = ChangePasswordHandler(
            user_repository=container.get(UserRepository),
            password_service=container.get(PasswordHasher),
        )
        
        change_result = handler.handle(change_password_command)
        
        # Publish domain events to outbox
        if hasattr(change_result, 'events') and change_result.events:
            _publish_domain_events(change_result.events)
        
        # Return success response
        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )
        
    except (UserNotFoundError, InvalidCredentialsError, PasswordPolicyError) as e:
        return _handle_domain_errors(e)
    except Exception as e:
        logger.error(f"Unexpected error in change_password: {str(e)}")
        return Response(
            {"error": "Internal server error", "code": "INTERNAL_ERROR"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    operation_id="deactivate_user",
    summary="Deactivate user account",
    description="Deactivate the authenticated user's account.",
    request=DeactivateUserSerializer,
    responses={
        200: OpenApiResponse(
            response=SuccessResponseSerializer,
            description="Account deactivated successfully"
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Authentication required"
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid operation"
        ),
    },
    tags=["User Profile"]
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deactivate_user(request: Request) -> Response:
    """
    Deactivate the authenticated user's account.
    
    Marks the user's account as deactivated, preventing future logins.
    This operation cannot be undone by the user.
    """
    try:
        current_user = get_current_user_from_request(request)
        if not current_user:
            return Response(
                {"error": "User not found", "code": "USER_NOT_FOUND"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Validate request data (reason is optional)
        serializer = DeactivateUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"error": "Validation failed", "details": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create command
        deactivate_command = DeactivateUserCommand(
            user_id=str(current_user.id.value),  # Convert UserId to string
            reason=serializer.validated_data.get('reason'),
        )
        
        # Execute use case
        container = InfrastructureContainer()
        handler = DeactivateUserHandler(
            user_repository=container.get(UserRepository),
        )
        
        deactivate_result = handler.handle(deactivate_command)
        
        # Publish domain events
        _publish_domain_events(deactivate_result.events)
        
        # Return success response
        return Response(
            {"message": "Account deactivated successfully"},
            status=status.HTTP_200_OK
        )
        
    except (UserNotFoundError, InvalidOperationError) as e:
        return _handle_domain_errors(e)
    except Exception as e:
        logger.error(f"Unexpected error in deactivate_user: {str(e)}")
        return Response(
            {"error": "Internal server error", "code": "INTERNAL_ERROR"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def user_health_check(request: Request) -> Response:
    """Simple health check for user management API."""
    try:
        container = InfrastructureContainer()
        # Simple test to verify container works
        user_repo = container.get(UserRepository)
        
        return Response({
            "status": "healthy",
            "service": "user-management-api", 
            "message": "User management API is operational",
            "container": "initialized successfully"
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            "status": "unhealthy", 
            "error": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
