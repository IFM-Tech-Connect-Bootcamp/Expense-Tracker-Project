"""
Views for User Management API endpoints.

This module contains Django REST Framework views that handle HTTP requests
for user management operations including registration, authentication,
profile management, and account operations.
"""

import logging
from typing import Dict, Any
from datetime import datetime

from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiResponse

from shared.response_standards import (
    StandardResponseBuilder,
    StandardErrorCodes,
    CommonMessages,
    HealthCheckResponse
)
from .serializers import (
    RegisterUserSerializer,
    AuthenticateUserSerializer,
    UpdateProfileSerializer,
    ChangePasswordSerializer,
    UserResponseSerializer,
    AuthResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)
from ..application.handlers import (
    RegisterUserHandler,
    AuthenticateUserHandler,
    UpdateProfileHandler,
    ChangePasswordHandler,
    DeactivateUserHandler,
)
from ..application.commands import (
    RegisterUserCommand,
    AuthenticateUserCommand,
    UpdateProfileCommand,
    ChangePasswordCommand,
    DeactivateUserCommand,
)
from ..application.dto import UserDTO, AuthResultDTO
from ..infrastructure.container import InfrastructureContainer
from ..domain.repositories.user_repository import UserRepository
from ..domain.services.password_policy import PasswordHasher, TokenProvider
from ..application.errors import (
    AuthenticationFailedError,
    UserNotFoundError as AppUserNotFoundError,
    RegistrationFailedError,
    ProfileUpdateFailedError,
    PasswordChangeFailedError,
    UserDeactivationFailedError,
    ValidationError as AppValidationError,
)
from ..domain.errors import (
    UserAlreadyExistsError,
    UserNotFoundError,
    InvalidCredentialsError,
    UserDeactivatedError,
    InvalidOperationError,
    PasswordPolicyError,
    DomainValidationError,
)
from .authentication import get_current_user_from_request

logger = logging.getLogger(__name__)


def get_current_user_id_from_request(request: Request) -> str:
    """
    Extract the current authenticated user ID from request.
    
    Args:
        request: Django REST request object
        
    Returns:
        Current user ID as string
        
    Raises:
        AuthenticationFailedError: If user is not authenticated
    """
    user_entity = get_current_user_from_request(request)
    if not user_entity:
        raise AuthenticationFailedError("User not authenticated")
    return str(user_entity.id.value)


def _handle_domain_errors(error: Exception) -> Response:
    """
    Convert domain and application errors to standardized HTTP responses.
    
    Args:
        error: Domain or application exception to convert
        
    Returns:
        HTTP response with standardized format and appropriate status code
    """
    logger.debug(f"Handling domain error: {type(error).__name__}: {str(error)}")
    
    # Handle application errors with specific mappings
    if isinstance(error, AuthenticationFailedError):
        response_data = StandardResponseBuilder.error(
            message="Authentication failed: Invalid email or password",
            code=StandardErrorCodes.INVALID_CREDENTIALS
        )
        return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
        
    elif isinstance(error, AppUserNotFoundError):
        response_data = StandardResponseBuilder.error(
            message="User account not found",
            code=StandardErrorCodes.USER_NOT_FOUND
        )
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
    elif isinstance(error, (AppValidationError, DomainValidationError)):
        response_data = StandardResponseBuilder.error(
            message=str(error),
            code=StandardErrorCodes.VALIDATION_ERROR
        )
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
    elif isinstance(error, RegistrationFailedError):
        # Check if it's a duplicate email error
        if "already exists" in str(error).lower() or "already registered" in str(error).lower():
            response_data = StandardResponseBuilder.error(
                message="Email address is already registered",
                code=StandardErrorCodes.EMAIL_ALREADY_REGISTERED
            )
            return Response(response_data, status=status.HTTP_409_CONFLICT)
        else:
            response_data = StandardResponseBuilder.error(
                message="User registration failed",
                code=StandardErrorCodes.REGISTRATION_FAILED,
                details={"reason": str(error)}
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
    elif isinstance(error, ProfileUpdateFailedError):
        response_data = StandardResponseBuilder.error(
            message="Profile update failed",
            code=StandardErrorCodes.PROFILE_UPDATE_FAILED,
            details={"reason": str(error)}
        )
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
    elif isinstance(error, PasswordChangeFailedError):
        response_data = StandardResponseBuilder.error(
            message="Password change failed",
            code=StandardErrorCodes.PASSWORD_CHANGE_FAILED,
            details={"reason": str(error)}
        )
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
    elif isinstance(error, UserDeactivationFailedError):
        response_data = StandardResponseBuilder.error(
            message="User deactivation failed",
            code=StandardErrorCodes.USER_DEACTIVATION_FAILED,
            details={"reason": str(error)}
        )
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle domain errors (legacy support)
    elif isinstance(error, UserAlreadyExistsError):
        response_data = StandardResponseBuilder.error(
            message="Email address is already registered",
            code=StandardErrorCodes.EMAIL_ALREADY_REGISTERED
        )
        return Response(response_data, status=status.HTTP_409_CONFLICT)
        
    elif isinstance(error, UserNotFoundError):
        response_data = StandardResponseBuilder.error(
            message="User account not found",
            code=StandardErrorCodes.USER_NOT_FOUND
        )
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
    elif isinstance(error, InvalidCredentialsError):
        response_data = StandardResponseBuilder.error(
            message="Authentication failed: Invalid email or password",
            code=StandardErrorCodes.INVALID_CREDENTIALS
        )
        return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
        
    elif isinstance(error, UserDeactivatedError):
        response_data = StandardResponseBuilder.error(
            message="User account has been deactivated",
            code=StandardErrorCodes.USER_DEACTIVATED
        )
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)
        
    elif isinstance(error, InvalidOperationError):
        response_data = StandardResponseBuilder.error(
            message="The requested operation is not allowed",
            code=StandardErrorCodes.OPERATION_NOT_ALLOWED
        )
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
    elif isinstance(error, PasswordPolicyError):
        response_data = StandardResponseBuilder.error(
            message=str(error),
            code=StandardErrorCodes.PASSWORD_POLICY_VIOLATION
        )
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Generic error handling
    else:
        logger.error(f"Unexpected error in user management API: {str(error)}")
        response_data = StandardResponseBuilder.error(
            message="An unexpected error occurred",
            code=StandardErrorCodes.INTERNAL_ERROR
        )
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _create_user_response_data(user_dto) -> Dict[str, Any]:
    """
    Create user response data from DTO.
    
    Args:
        user_dto: User DTO containing user information
        
    Returns:
        Dictionary with user data for response
    """
    return {
        "id": user_dto.id,
        "email": user_dto.email,
        "first_name": user_dto.first_name,
        "last_name": user_dto.last_name,
        "full_name": user_dto.full_name,
        "status": user_dto.status,
        "created_at": user_dto.created_at,
        "updated_at": user_dto.updated_at,
    }


@extend_schema(
    summary="Register new user",
    description="Create a new user account with email, password, and profile information",
    request=RegisterUserSerializer,
    responses={
        201: OpenApiResponse(
            response=UserResponseSerializer,
            description="User registered successfully"
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid request data"
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Email already registered"
        ),
    },
    tags=["authentication"],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request: Request) -> Response:
    """Register a new user account."""
    logger.info("Processing user registration request")
    
    try:
        # Validate request data
        serializer = RegisterUserSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"User registration validation failed: {serializer.errors}")
            field_errors = {field: [str(error) for error in errors] 
                          for field, errors in serializer.errors.items()}
            response_data = StandardResponseBuilder.validation_error(
                message="Registration data validation failed",
                field_errors=field_errors
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Execute registration through handler
        container = InfrastructureContainer()
        handler = RegisterUserHandler(
            user_repository=container.get(UserRepository),
            password_service=container.get(PasswordHasher),
        )
        
        command = RegisterUserCommand(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
        )
        
        result = handler.handle(command)
        user_dto = result.user_dto
        
        # Create successful response
        user_data = _create_user_response_data(user_dto)
        response_data = StandardResponseBuilder.created(
            data=user_data,
            message=CommonMessages.USER_REGISTERED
        )
        
        logger.info(f"User registration completed successfully for email: {user_dto.email}")
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="Authenticate user",
    description="Authenticate user with email and password, returning JWT access token",
    request=AuthenticateUserSerializer,
    responses={
        200: OpenApiResponse(
            response=AuthResponseSerializer,
            description="User authenticated successfully"
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid credentials"
        ),
        403: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="User account deactivated"
        ),
    },
    tags=["authentication"],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def authenticate_user(request: Request) -> Response:
    """Authenticate user and return JWT token."""
    logger.info("Processing user authentication request")
    
    try:
        # Validate request data
        serializer = AuthenticateUserSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"User authentication validation failed: {serializer.errors}")
            field_errors = {field: [str(error) for error in errors] 
                          for field, errors in serializer.errors.items()}
            response_data = StandardResponseBuilder.validation_error(
                message="Login data validation failed",
                field_errors=field_errors
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Execute authentication through handler
        container = InfrastructureContainer()
        handler = AuthenticateUserHandler(
            user_repository=container.get(UserRepository),
            password_service=container.get(PasswordHasher),
            token_provider=container.get(TokenProvider),
        )
        
        command = AuthenticateUserCommand(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password']
        )
        
        auth_result = handler.handle(command)
        
        # Create successful response
        user_data = _create_user_response_data(auth_result.user)
        auth_data = {
            "user": user_data,
            "access_token": auth_result.access_token,
            "token_type": "Bearer",
            "expires_in": auth_result.expires_in or 3600  # Use from DTO or default 1 hour
        }
        
        response_data = StandardResponseBuilder.success(
            data=auth_data,
            message=CommonMessages.USER_AUTHENTICATED
        )
        
        logger.info(f"User authentication completed successfully for email: {auth_result.user.email}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error during user authentication: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="Get current user profile",
    description="Retrieve the authenticated user's profile information",
    responses={
        200: OpenApiResponse(
            response=UserResponseSerializer,
            description="User profile retrieved successfully"
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Authentication required"
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="User not found"
        ),
    },
    tags=["profile"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_current_user(request: Request) -> Response:
    """Get current authenticated user's profile."""
    logger.info("Processing get current user request")
    
    try:
        # Get authenticated user ID
        user_id = get_current_user_id_from_request(request)
        
        # Get user directly through repository
        container = InfrastructureContainer()
        user_repository = container.get(UserRepository)
        
        from ..domain.value_objects.user_id import UserId
        user_id_vo = UserId.from_string(user_id)
        user_entity = user_repository.find_by_id(user_id_vo)
        
        if not user_entity:
            from ..domain.errors import UserNotFoundError
            raise UserNotFoundError(f"User with ID {user_id} not found")
        
        # Convert to DTO
        user_dto = UserDTO(
            id=str(user_entity.id.value),
            email=user_entity.email.value,
            first_name=user_entity.first_name.value,
            last_name=user_entity.last_name.value,
            full_name=f"{user_entity.first_name.value} {user_entity.last_name.value}",
            status=user_entity.status.value,
            created_at=user_entity.created_at,
            updated_at=user_entity.updated_at,
        )
        
        # Create successful response
        user_data = _create_user_response_data(user_dto)
        response_data = StandardResponseBuilder.success(
            data=user_data,
            message=CommonMessages.USER_PROFILE_RETRIEVED
        )
        
        logger.info(f"User profile retrieved successfully for user: {user_id}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error retrieving user profile: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="Update user profile",
    description="Update the authenticated user's profile information",
    request=UpdateProfileSerializer,
    responses={
        200: OpenApiResponse(
            response=UserResponseSerializer,
            description="Profile updated successfully"
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid request data"
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Authentication required"
        ),
    },
    tags=["profile"],
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_profile(request: Request) -> Response:
    """Update authenticated user's profile."""
    logger.info("Processing profile update request")
    
    try:
        # Get authenticated user ID
        user_id = get_current_user_id_from_request(request)
        
        # Validate request data
        serializer = UpdateProfileSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Profile update validation failed: {serializer.errors}")
            field_errors = {field: [str(error) for error in errors] 
                          for field, errors in serializer.errors.items()}
            response_data = StandardResponseBuilder.validation_error(
                message="Profile update data validation failed",
                field_errors=field_errors
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Execute profile update through handler
        from ..application.handlers.update_profile import UpdateProfileHandler
        container = InfrastructureContainer()
        handler = UpdateProfileHandler(
            user_repository=container.get(UserRepository),
        )
        
        # Create command
        command = UpdateProfileCommand(
            user_id=user_id,
            new_first_name=serializer.validated_data.get('first_name'),
            new_last_name=serializer.validated_data.get('last_name'),
        )
        
        # Execute handler
        result = handler.handle(command)
        
        # Create successful response
        user_data = _create_user_response_data(result.user_dto)
        response_data = StandardResponseBuilder.updated(
            data=user_data,
            message=CommonMessages.USER_PROFILE_UPDATED
        )
        
        logger.info(f"Profile update completed successfully for user: {user_id}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error updating profile: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="Change password",
    description="Change the authenticated user's password",
    request=ChangePasswordSerializer,
    responses={
        200: OpenApiResponse(
            response=SuccessResponseSerializer,
            description="Password changed successfully"
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid request data"
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Authentication required or invalid current password"
        ),
    },
    tags=["profile"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password(request: Request) -> Response:
    """Change authenticated user's password."""
    logger.info("Processing password change request")
    
    try:
        # Get authenticated user ID
        user_id = get_current_user_id_from_request(request)
        
        # Validate request data
        serializer = ChangePasswordSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Password change validation failed: {serializer.errors}")
            field_errors = {field: [str(error) for error in errors] 
                          for field, errors in serializer.errors.items()}
            response_data = StandardResponseBuilder.validation_error(
                message="Password change data validation failed",
                field_errors=field_errors
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Execute password change through handler
        from ..application.handlers.change_password import ChangePasswordHandler
        container = InfrastructureContainer()
        handler = ChangePasswordHandler(
            user_repository=container.get(UserRepository),
            password_service=container.get(PasswordHasher),
        )
        
        # Create command
        command = ChangePasswordCommand(
            user_id=user_id,
            old_password=serializer.validated_data['old_password'],
            new_password=serializer.validated_data['new_password']
        )
        
        # Execute handler
        result = handler.handle(command)
        
        # Create successful response
        response_data = StandardResponseBuilder.success(
            message=CommonMessages.PASSWORD_CHANGED
        )
        
        logger.info(f"Password change completed successfully for user: {user_id}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error changing password: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="Deactivate user account",
    description="Deactivate the authenticated user's account",
    responses={
        200: OpenApiResponse(
            response=SuccessResponseSerializer,
            description="Account deactivated successfully"
        ),
        401: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Authentication required"
        ),
    },
    tags=["profile"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def deactivate_user(request: Request) -> Response:
    """Deactivate authenticated user's account."""
    logger.info("Processing user deactivation request")
    
    try:
        # Get authenticated user ID
        user_id = get_current_user_id_from_request(request)
        
        # Execute deactivation through handler
        from ..application.handlers.deactivate_user import DeactivateUserHandler
        container = InfrastructureContainer()
        handler = DeactivateUserHandler(
            user_repository=container.get(UserRepository),
        )
        
        # Create command
        command = DeactivateUserCommand(user_id=user_id)
        
        # Execute handler
        result = handler.handle(command)
        
        # Create successful response
        response_data = StandardResponseBuilder.success(
            message=CommonMessages.USER_DEACTIVATED
        )
        
        logger.info(f"User deactivation completed successfully for user: {user_id}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error deactivating user: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="User management health check",
    description="Check the health status of the user management service",
    responses={
        200: OpenApiResponse(
            description="Service is healthy"
        ),
    },
    tags=["health"],
)
@api_view(['GET'])
@permission_classes([AllowAny])
def user_health_check(request: Request) -> Response:
    """Health check endpoint for user management service."""
    try:
        # Test container availability
        container = InfrastructureContainer()
        
        # Build health response
        health_data = HealthCheckResponse.healthy(
            service_name="user_management",
            version="1.0.0",
            handlers=[
                "RegisterUserHandler",
                "AuthenticateUserHandler",
                "UpdateProfileHandler",
                "ChangePasswordHandler",
                "DeactivateUserHandler"
            ]
        )
        health_data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        return JsonResponse(health_data, status=200)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        health_data = HealthCheckResponse.unhealthy(
            service_name="user_management",
            errors=[str(e)],
            version="1.0.0"
        )
        health_data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        return JsonResponse(health_data, status=503)