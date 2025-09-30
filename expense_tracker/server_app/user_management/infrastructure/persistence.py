# usermanagement/infrastructure/persistence.py
from typing import Optional
from ..domain.repositories import UserRepository
from ..domain.entities import User
from ..domain.value_objects import UserId, Email, Password
from ..models import UserORM
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

class UserRepositoryImpl(UserRepository):

    def _to_entity(self, orm_model: UserORM) -> User:
        return User(
            user_id=UserId(orm_model.id),
            email=Email(orm_model.email),
            password=Password(orm_model.password_hash),
            name=orm_model.name,
            created_at=orm_model.created_at,
            is_active=orm_model.is_active,
        )

    def _to_orm(self, entity: User) -> UserORM:
        try:
            orm_model = UserORM.objects.get(id=entity.user_id.value)
        except ObjectDoesNotExist:
            orm_model = UserORM(id=entity.user_id.value)

        orm_model.email = entity.email.value
        orm_model.password_hash = entity.password.hash
        orm_model.name = entity.name
        orm_model.is_active = entity.is_active
        return orm_model

    def find_by_email(self, email: Email) -> Optional[User]:
        try:
            orm_model = UserORM.objects.get(email=email.value)
            return self._to_entity(orm_model)
        except ObjectDoesNotExist:
            return None

    # ... (implement find_by_id, save, and update similarly)
    # The 'save' and 'update' methods use _to_orm and then save the ORM model.
    @transaction.atomic
    def save(self, user: User) -> None:
        orm_model = self._to_orm(user)
        orm_model.save()
    
    @transaction.atomic
    def update(self, user: User) -> None:
        orm_model = self._to_orm(user)
        orm_model.save()

    def find_by_id(self, user_id: UserId) -> Optional[User]:
        raise NotImplementedError
