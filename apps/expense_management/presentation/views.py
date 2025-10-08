"""
Views for Expense Management API endpoints.

This module contains Django REST Framework views that handle HTTP requests
for expense management operations including expense CRUD, category management,
and expense analytics.
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
    CreateExpenseSerializer,
    UpdateExpenseSerializer,
    CreateCategorySerializer,
    UpdateCategorySerializer,
    ExpenseResponseSerializer,
    CategoryResponseSerializer,
    ExpenseSummaryResponseSerializer,
    ErrorResponseSerializer,
    SuccessResponseSerializer,
)
from ..application.commands import (
    CreateExpenseCommand,
    UpdateExpenseCommand,
    DeleteExpenseCommand,
    CreateCategoryCommand,
    UpdateCategoryCommand,
    DeleteCategoryCommand,
    GetExpenseSummaryCommand,
)
from ..application.handlers import (
    CreateExpenseHandler,
    UpdateExpenseHandler,
    DeleteExpenseHandler,
    CreateCategoryHandler,
    UpdateCategoryHandler,
    DeleteCategoryHandler,
    GetExpenseSummaryHandler,
)
from ..application.errors import (
    ExpenseNotFoundError,
    ExpenseAccessDeniedError,
    CategoryNotFoundError,
    CategoryAccessDeniedError,
    DuplicateCategoryNameError,
    CategoryInUseError,
    BusinessRuleViolationError,
    ApplicationError,
    ValidationError as AppValidationError,
)
from ..domain.errors import (
    ExpenseManagementDomainError,
    ValidationError as DomainValidationError,
)
from ..infrastructure.container import get_container
from .authentication import get_current_user_from_request

logger = logging.getLogger(__name__)


def _handle_domain_errors(error: Exception) -> Response:
    """Convert domain and application errors to standardized HTTP responses.
    
    Args:
        error: The exception that occurred.
        
    Returns:
        Django REST Framework Response with standardized format and appropriate status code.
    """
    logger.debug(f"Handling domain error: {type(error).__name__}: {str(error)}")
    
    # Handle specific expense management errors
    if isinstance(error, ExpenseNotFoundError):
        response_data = StandardResponseBuilder.error(
            message="The requested expense was not found",
            code=StandardErrorCodes.EXPENSE_NOT_FOUND
        )
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
    elif isinstance(error, ExpenseAccessDeniedError):
        response_data = StandardResponseBuilder.error(
            message="You do not have permission to access this expense",
            code=StandardErrorCodes.EXPENSE_ACCESS_DENIED
        )
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)
        
    elif isinstance(error, CategoryNotFoundError):
        response_data = StandardResponseBuilder.error(
            message="The requested category was not found",
            code=StandardErrorCodes.CATEGORY_NOT_FOUND
        )
        return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
    elif isinstance(error, CategoryAccessDeniedError):
        response_data = StandardResponseBuilder.error(
            message="You do not have permission to access this category",
            code=StandardErrorCodes.CATEGORY_ACCESS_DENIED
        )
        return Response(response_data, status=status.HTTP_403_FORBIDDEN)
        
    elif isinstance(error, DuplicateCategoryNameError):
        response_data = StandardResponseBuilder.error(
            message="A category with this name already exists",
            code=StandardErrorCodes.DUPLICATE_CATEGORY_NAME
        )
        return Response(response_data, status=status.HTTP_409_CONFLICT)
        
    elif isinstance(error, CategoryInUseError):
        response_data = StandardResponseBuilder.error(
            message="Category cannot be deleted because it is currently in use",
            code=StandardErrorCodes.CATEGORY_IN_USE
        )
        return Response(response_data, status=status.HTTP_409_CONFLICT)
        
    elif isinstance(error, (AppValidationError, DomainValidationError)):
        response_data = StandardResponseBuilder.error(
            message=str(error),
            code=StandardErrorCodes.VALIDATION_ERROR
        )
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
    elif isinstance(error, BusinessRuleViolationError):
        response_data = StandardResponseBuilder.error(
            message=str(error),
            code=StandardErrorCodes.BUSINESS_RULE_VIOLATION
        )
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
    elif isinstance(error, ApplicationError):
        # Determine the specific error type from the message
        error_msg = str(error).lower()
        if "expense" in error_msg and "creation" in error_msg:
            code = StandardErrorCodes.EXPENSE_CREATION_FAILED
        elif "expense" in error_msg and "update" in error_msg:
            code = StandardErrorCodes.EXPENSE_UPDATE_FAILED
        elif "expense" in error_msg and ("delet" in error_msg or "remov" in error_msg):
            code = StandardErrorCodes.EXPENSE_DELETION_FAILED
        elif "category" in error_msg and "creation" in error_msg:
            code = StandardErrorCodes.CATEGORY_CREATION_FAILED
        elif "category" in error_msg and "update" in error_msg:
            code = StandardErrorCodes.CATEGORY_UPDATE_FAILED
        elif "category" in error_msg and ("delet" in error_msg or "remov" in error_msg):
            code = StandardErrorCodes.CATEGORY_DELETION_FAILED
        else:
            code = StandardErrorCodes.OPERATION_NOT_ALLOWED
            
        response_data = StandardResponseBuilder.error(
            message=str(error),
            code=code
        )
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
    # Generic error handling
    else:
        logger.error(f"Unexpected error in expense management API: {str(error)}")
        response_data = StandardResponseBuilder.error(
            message="An unexpected error occurred",
            code=StandardErrorCodes.INTERNAL_ERROR
        )
        return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def _create_expense_response_data(expense_dto) -> Dict[str, Any]:
    """Create standardized expense response data from DTO."""
    return {
        "id": expense_dto.id,
        "user_id": expense_dto.user_id,
        "category_id": expense_dto.category_id,
        "amount_tzs": expense_dto.amount_tzs,
        "amount_formatted": f"TZS {expense_dto.amount_tzs:,.2f}",
        "description": expense_dto.description,
        "expense_date": expense_dto.expense_date.isoformat() if expense_dto.expense_date else None,
        "created_at": expense_dto.created_at.isoformat() + "Z" if expense_dto.created_at else None,
        "updated_at": expense_dto.updated_at.isoformat() + "Z" if expense_dto.updated_at else None,
    }


def _create_category_response_data(category_dto) -> Dict[str, Any]:
    """Create standardized category response data from DTO."""
    return {
        "id": category_dto.id,
        "user_id": category_dto.user_id,
        "name": category_dto.name,
        "created_at": category_dto.created_at.isoformat() + "Z" if category_dto.created_at else None,
        "updated_at": category_dto.updated_at.isoformat() + "Z" if category_dto.updated_at else None,
    }


def _create_expense_summary_response_data(summary_dto) -> Dict[str, Any]:
    """Create standardized expense summary response data from DTO."""
    category_summaries = []
    if hasattr(summary_dto, 'category_summaries') and summary_dto.category_summaries:
        for cat_summary in summary_dto.category_summaries:
            category_summaries.append({
                "category_id": cat_summary.category_id,
                "category_name": cat_summary.category_name,
                "total_amount_tzs": cat_summary.total_amount_tzs,
                "total_amount_formatted": f"TZS {cat_summary.total_amount_tzs:,.2f}",
                "expense_count": cat_summary.expense_count,
                "average_amount_tzs": cat_summary.average_amount_tzs,
                "average_amount_formatted": f"TZS {cat_summary.average_amount_tzs:,.2f}",
            })
    
    return {
        "user_id": summary_dto.user_id,
        "total_amount_tzs": summary_dto.total_amount_tzs,
        "total_amount_formatted": f"TZS {summary_dto.total_amount_tzs:,.2f}",
        "expense_count": summary_dto.total_expense_count,
        "average_amount_tzs": summary_dto.average_expense_amount_tzs,
        "average_amount_formatted": f"TZS {summary_dto.average_expense_amount_tzs:,.2f}",
        "start_date": summary_dto.start_date.isoformat() if summary_dto.start_date else None,
        "end_date": summary_dto.end_date.isoformat() if summary_dto.end_date else None,
        "category_summaries": category_summaries,
    }


@extend_schema(
    summary="Create new expense",
    description="Create a new expense record for the authenticated user",
    request=CreateExpenseSerializer,
    responses={
        201: OpenApiResponse(
            response=ExpenseResponseSerializer,
            description="Expense created successfully"
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid request data"
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Category not found"
        ),
    },
    tags=["expenses"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_expense(request: Request) -> Response:
    """Create a new expense for the authenticated user."""
    logger.info("Processing expense creation request")
    
    try:
        # Get authenticated user
        user_id = get_current_user_from_request(request)
        
        # Validate request data
        serializer = CreateExpenseSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Expense creation validation failed: {serializer.errors}")
            field_errors = {field: [str(error) for error in errors] 
                          for field, errors in serializer.errors.items()}
            response_data = StandardResponseBuilder.validation_error(
                message="Expense creation data validation failed",
                field_errors=field_errors
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Create command from validated data
        command = CreateExpenseCommand(
            user_id=user_id,
            category_id=str(serializer.validated_data['category_id']),
            amount_tzs=serializer.validated_data['amount_tzs'],
            description=serializer.validated_data.get('description'),
            expense_date=serializer.validated_data['expense_date']
        )
        
        # Get handler from container and execute
        container = get_container()
        handler = container.get(CreateExpenseHandler)
        result = handler.handle(command)
        
        # Create successful response
        expense_data = _create_expense_response_data(result.expense_dto)
        response_data = StandardResponseBuilder.created(
            data=expense_data,
            message=CommonMessages.EXPENSE_CREATED
        )
        
        logger.info(f"Expense created successfully for user {user_id}: {result.expense_dto.id}")
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating expense: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="Update existing expense",
    description="Update an existing expense for the authenticated user",
    request=UpdateExpenseSerializer,
    responses={
        200: OpenApiResponse(
            response=ExpenseResponseSerializer,
            description="Expense updated successfully"
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid request data"
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Expense not found"
        ),
    },
    tags=["expenses"],
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_expense(request: Request, expense_id: str) -> Response:
    """Update an existing expense for the authenticated user."""
    logger.info(f"Processing expense update request for expense: {expense_id}")
    
    try:
        # Get authenticated user
        user_id = get_current_user_from_request(request)
        
        # Validate request data
        serializer = UpdateExpenseSerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Expense update validation failed: {serializer.errors}")
            field_errors = {field: [str(error) for error in errors] 
                          for field, errors in serializer.errors.items()}
            response_data = StandardResponseBuilder.validation_error(
                message="Expense update data validation failed",
                field_errors=field_errors
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Create command from validated data
        command = UpdateExpenseCommand(
            expense_id=expense_id,
            user_id=user_id,
            category_id=str(serializer.validated_data['category_id']) if 'category_id' in serializer.validated_data else None,
            amount_tzs=serializer.validated_data.get('amount_tzs'),
            description=serializer.validated_data.get('description'),
            expense_date=serializer.validated_data.get('expense_date')
        )
        
        # Get handler from container and execute
        container = get_container()
        handler = container.get(UpdateExpenseHandler)
        result = handler.handle(command)
        
        # Create successful response
        expense_data = _create_expense_response_data(result.expense_dto)
        response_data = StandardResponseBuilder.updated(
            data=expense_data,
            message=CommonMessages.EXPENSE_UPDATED
        )
        
        logger.info(f"Expense updated successfully: {expense_id}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error updating expense {expense_id}: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="Delete expense",
    description="Delete an existing expense for the authenticated user",
    responses={
        200: OpenApiResponse(
            response=SuccessResponseSerializer,
            description="Expense deleted successfully"
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Expense not found"
        ),
    },
    tags=["expenses"],
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_expense(request: Request, expense_id: str) -> Response:
    """Delete an existing expense for the authenticated user."""
    logger.info(f"Processing expense deletion request for expense: {expense_id}")
    
    try:
        # Get authenticated user
        user_id = get_current_user_from_request(request)
        
        # Create command
        command = DeleteExpenseCommand(
            expense_id=expense_id,
            user_id=user_id
        )
        
        # Get handler from container and execute
        container = get_container()
        handler = container.get(DeleteExpenseHandler)
        handler.handle(command)
        
        # Create successful response
        response_data = StandardResponseBuilder.deleted(
            message=CommonMessages.EXPENSE_DELETED
        )
        
        logger.info(f"Expense deleted successfully: {expense_id}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error deleting expense {expense_id}: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="Get expense summary",
    description="Get expense summary and analytics for the authenticated user",
    responses={
        200: OpenApiResponse(
            response=ExpenseSummaryResponseSerializer,
            description="Expense summary retrieved successfully"
        ),
    },
    tags=["analytics"],
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_expense_summary(request: Request) -> Response:
    """Get expense summary for the authenticated user."""
    logger.info("Processing expense summary request")
    
    try:
        # Get authenticated user
        user_id = get_current_user_from_request(request)
        
        # Create command
        command = GetExpenseSummaryCommand(
            user_id=user_id,
            start_date=None,  # Could be extended to support date filtering
            end_date=None
        )
        
        # Get handler from container and execute
        container = get_container()
        handler = container.get(GetExpenseSummaryHandler)
        result = handler.handle(command)
        
        # Create successful response
        summary_data = _create_expense_summary_response_data(result.summary_dto)
        response_data = StandardResponseBuilder.success(
            data=summary_data,
            message=CommonMessages.EXPENSE_SUMMARY_RETRIEVED
        )
        
        logger.info(f"Expense summary retrieved successfully for user: {user_id}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error retrieving expense summary: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="Create new category",
    description="Create a new expense category for the authenticated user",
    request=CreateCategorySerializer,
    responses={
        201: OpenApiResponse(
            response=CategoryResponseSerializer,
            description="Category created successfully"
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid request data"
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Category name already exists"
        ),
    },
    tags=["categories"],
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_category(request: Request) -> Response:
    """Create a new expense category for the authenticated user."""
    logger.info("Processing category creation request")
    
    try:
        # Get authenticated user
        user_id = get_current_user_from_request(request)
        
        # Validate request data
        serializer = CreateCategorySerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Category creation validation failed: {serializer.errors}")
            field_errors = {field: [str(error) for error in errors] 
                          for field, errors in serializer.errors.items()}
            response_data = StandardResponseBuilder.validation_error(
                message="Category creation data validation failed",
                field_errors=field_errors
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Create command from validated data
        command = CreateCategoryCommand(
            user_id=user_id,
            name=serializer.validated_data['name']
        )
        
        # Get handler from container and execute
        container = get_container()
        handler = container.get(CreateCategoryHandler)
        result = handler.handle(command)
        
        # Create successful response
        category_data = _create_category_response_data(result.category_dto)
        response_data = StandardResponseBuilder.created(
            data=category_data,
            message=CommonMessages.CATEGORY_CREATED
        )
        
        logger.info(f"Category created successfully for user {user_id}: {result.category_dto.id}")
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error creating category: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="Update existing category",
    description="Update an existing expense category for the authenticated user",
    request=UpdateCategorySerializer,
    responses={
        200: OpenApiResponse(
            response=CategoryResponseSerializer,
            description="Category updated successfully"
        ),
        400: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Invalid request data"
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Category not found"
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Category name already exists"
        ),
    },
    tags=["categories"],
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_category(request: Request, category_id: str) -> Response:
    """Update an existing expense category for the authenticated user."""
    logger.info(f"Processing category update request for category: {category_id}")
    
    try:
        # Get authenticated user
        user_id = get_current_user_from_request(request)
        
        # Validate request data
        serializer = UpdateCategorySerializer(data=request.data)
        if not serializer.is_valid():
            logger.warning(f"Category update validation failed: {serializer.errors}")
            field_errors = {field: [str(error) for error in errors] 
                          for field, errors in serializer.errors.items()}
            response_data = StandardResponseBuilder.validation_error(
                message="Category update data validation failed",
                field_errors=field_errors
            )
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        # Create command from validated data
        command = UpdateCategoryCommand(
            category_id=category_id,
            user_id=user_id,
            name=serializer.validated_data['name']
        )
        
        # Get handler from container and execute
        container = get_container()
        handler = container.get(UpdateCategoryHandler)
        result = handler.handle(command)
        
        # Create successful response
        category_data = _create_category_response_data(result.category_dto)
        response_data = StandardResponseBuilder.updated(
            data=category_data,
            message=CommonMessages.CATEGORY_UPDATED
        )
        
        logger.info(f"Category updated successfully: {category_id}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error updating category {category_id}: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="Delete category",
    description="Delete an existing expense category for the authenticated user",
    responses={
        200: OpenApiResponse(
            response=SuccessResponseSerializer,
            description="Category deleted successfully"
        ),
        404: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Category not found"
        ),
        409: OpenApiResponse(
            response=ErrorResponseSerializer,
            description="Category is in use and cannot be deleted"
        ),
    },
    tags=["categories"],
)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_category(request: Request, category_id: str) -> Response:
    """Delete an existing expense category for the authenticated user."""
    logger.info(f"Processing category deletion request for category: {category_id}")
    
    try:
        # Get authenticated user
        user_id = get_current_user_from_request(request)
        
        # Create command
        command = DeleteCategoryCommand(
            category_id=category_id,
            user_id=user_id
        )
        
        # Get handler from container and execute
        container = get_container()
        handler = container.get(DeleteCategoryHandler)
        handler.handle(command)
        
        # Create successful response
        response_data = StandardResponseBuilder.deleted(
            message=CommonMessages.CATEGORY_DELETED
        )
        
        logger.info(f"Category deleted successfully: {category_id}")
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error deleting category {category_id}: {str(e)}")
        return _handle_domain_errors(e)


@extend_schema(
    summary="Expense management health check",
    description="Check the health status of the expense management service",
    responses={
        200: OpenApiResponse(
            description="Service is healthy"
        ),
    },
    tags=["health"],
)
@api_view(['GET'])
@permission_classes([AllowAny])
def expense_health_check(request: Request) -> Response:
    """Health check endpoint for expense management service."""
    try:
        # Test service availability by checking container
        container = get_container()
        
        # Build health response
        health_data = HealthCheckResponse.healthy(
            service_name="expense_management",
            version="1.0.0",
            handlers=[
                "CreateExpenseHandler",
                "UpdateExpenseHandler", 
                "DeleteExpenseHandler",
                "CreateCategoryHandler",
                "UpdateCategoryHandler",
                "DeleteCategoryHandler",
                "GetExpenseSummaryHandler"
            ]
        )
        health_data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        return JsonResponse(health_data, status=200)
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        health_data = HealthCheckResponse.unhealthy(
            service_name="expense_management",
            errors=[str(e)],
            version="1.0.0"
        )
        health_data["timestamp"] = datetime.utcnow().isoformat() + "Z"
        
        return JsonResponse(health_data, status=503)