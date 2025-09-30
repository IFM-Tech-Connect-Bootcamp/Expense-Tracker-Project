# usermanagement/models.py

import uuid
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager

# This is the persistence model, *not* the Domain entity.
class CustomUserManager(BaseUserManager):
    # Minimal manager for the simple User entity
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        # Note: Password is set/hashed in the domain layer, but the Django model needs a save method.
        # For simplicity with Django's system, we'll hash here, but in a pure DDD/Clean
        # setup, the domain layer would pass the hash.
        user.set_password(password) # We'll bypass this in the true DDD repo impl.
        user.save(using=self._db)
        return user
    
    # We will not implement a superuser/staff for the MVP constraint.

class UserORM(models.Model): # We'll use a standard Model and manage auth manually
    # Or inherit from AbstractBaseUser for better integration, but needs more setup.
    # Sticking to models.Model for a 'flat user model' for MVP simplicity.

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    password_hash = models.CharField(max_length=255) # Stores the hash
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    # Django ORM requirements
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email