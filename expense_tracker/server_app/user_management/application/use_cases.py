# usermanagement/application/use_cases.py
from ..domain.repositories import UserRepository
from ..domain.services import UserService
from ..domain.value_objects import Email, UserId
from ..infrastructure.auth import AuthService
from typing import NamedTuple, Optional

class RegisterUserRequest(NamedTuple):
    email: str
    password: str
    name: Optional[str] = None

class RegisterUserHandler:
    def __init__(self, user_repo: UserRepository, auth_service: AuthService):
        self.user_service = UserService(user_repo, auth_service) # type: ignore

    def execute(self, request: RegisterUserRequest) -> UserId:
        # 1. Input Mapping/Validation (to Value Objects)
        email = Email(request.email)
        
        # 2. Call Domain Service
        user = self.user_service.register(
            email=email,
            plain_password=request.password,
            name=request.name
        )
        # 3. Return output
        return user.user_id

# ... (Implement AuthenticateUserHandler, UpdateUserProfileHandler, etc., similarly)
# They will all follow the flow: Map Input -> Call UserService -> Return Output/Token