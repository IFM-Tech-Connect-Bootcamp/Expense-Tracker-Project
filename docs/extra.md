Great — let’s design the **infrastructure layer** so it fully implements the application layer you described and plugs cleanly into your domain (which you’ve already implemented). I’ll give a clear file layout, the responsibilities for each piece, and ready-to-drop code sketches for the most important components:

* Django ORM models & mappers (domain ↔ db)
* Repository implementation using Django ORM
* Password hasher (bcrypt / passlib) implementation of domain `PasswordHasher`
* Token provider (JWT) implementation of domain `TokenProvider`
* Outbox table + writer (reliable delivery for external side-effects)
* Outbox dispatcher/worker (simple management command + optional Celery task)
* Event subscriber wiring and startup registration (AppConfig)
* Notes on transactions, error handling, and testing

I keep everything modular (module-scoped Django app), framework-specific code in `infrastructure/`, and domain/application layers unchanged.

---

# 1) Infrastructure file structure (per `modules/user_management/`)

```
user_management/
└── infrastructure/
    ├── __init__.py
    ├── orm/
    │   ├── models.py                 # Django models: UserModel, OutboxEvent
    │   └── mappers.py                # map <-> domain
    │
    ├── repositories/
    │   └── user_repository_django.py # UserRepository implementation
    │
    ├── auth/
    │   ├── bcrypt_hasher.py          # PasswordHasher impl
    │   └── jwt_provider.py           # TokenProvider impl
    │
    ├── outbox/
    │   ├── writer.py                 # helper to save outbox entries (transaction-safe)
    │   ├── dispatcher.py             # process/flush outbox -> external systems
    │   └── management/commands/flush_outbox.py  # simple CLI runner
    │
    ├── subscribers/
    │   ├── notify_on_user_registered.py  # infra-level subscriber, writes to outbox
    │   └── register.py                   # helper to wire infra subscribers to EventBus
    │
    └── migrations/                    # Django migrations for models
```

---

# 2) Django models (`orm/models.py`)

Key points:

* `UserModel` holds persisted fields (UUID PK, email unique, name(s), password_hash, status, created/updated).
* `OutboxEvent` stores events to be delivered to external systems. Keep a JSON payload, event_type, aggregate_id, created_at, processed_at, attempts.

```python
# user_management/infrastructure/orm/models.py
from django.db import models
import uuid
from django.utils import timezone

class UserModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, max_length=254)
    password_hash = models.CharField(max_length=255)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    status = models.CharField(max_length=32, default="active")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_management_user"

class OutboxEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    event_type = models.CharField(max_length=255)
    aggregate_id = models.UUIDField(null=True)
    payload = models.JSONField()
    created_at = models.DateTimeField(default=timezone.now)
    processed_at = models.DateTimeField(null=True, blank=True)
    attempts = models.IntegerField(default=0)

    class Meta:
        db_table = "user_management_outbox"
        indexes = [
            models.Index(fields=["processed_at", "created_at"]),
        ]
```

---

# 3) Mappers: domain ↔ persistence (`orm/mappers.py`)

Keep mapping logic in one place. Use domain value objects and constructors.

```python
# user_management/infrastructure/orm/mappers.py
from ..domain.value_objects.user_id import UserId
from ..domain.value_objects.email import Email
from ..domain.value_objects.password_hash import PasswordHash
from ..domain.value_objects.first_name import FirstName
from ..domain.value_objects.last_name import LastName
from ..domain.entities.user import User
from .models import UserModel
from datetime import timezone

def model_to_entity(model: UserModel) -> User:
    return User(
        id=UserId(model.id),
        email=Email(model.email),
        password_hash=PasswordHash(model.password_hash),
        first_name=FirstName(model.first_name),
        last_name=LastName(model.last_name),
        created_at=model.created_at,
        updated_at=model.updated_at,
        status=model.status
    )

def entity_to_model(entity: User) -> dict:
    # return dict to use in create/update
    return dict(
        id=entity.id.value,
        email=str(entity.email),
        password_hash=entity.password_hash.value,
        first_name=str(entity.first_name),
        last_name=str(entity.last_name),
        status=entity.status.value,
        created_at=entity.created_at,
    )
```

Note: adjust names/attributes to match your domain entity fields exactly.

---

# 4) Repository implementation (`repositories/user_repository_django.py`)

Use Django ORM and mappers. Ensure transaction boundaries and translate DB integrity errors to domain errors.

```python
# user_management/infrastructure/repositories/user_repository_django.py
from typing import Optional
from django.db import transaction, IntegrityError
from ..domain.value_objects.user_id import UserId
from ..domain.value_objects.email import Email
from ..domain.repositories.user_repository import UserRepository
from ..domain.errors import UserAlreadyExistsError, UserNotFoundError
from ..infrastructure.orm.models import UserModel
from ..infrastructure.orm.mappers import model_to_entity, entity_to_model

class DjangoUserRepository(UserRepository):
    def find_by_id(self, user_id: UserId) -> Optional[object]:
        try:
            model = UserModel.objects.get(id=user_id.value)
            return model_to_entity(model)
        except UserModel.DoesNotExist:
            return None

    def find_by_email(self, email: Email) -> Optional[object]:
        try:
            model = UserModel.objects.get(email=str(email))
            return model_to_entity(model)
        except UserModel.DoesNotExist:
            return None

    def exists_by_email(self, email: Email) -> bool:
        return UserModel.objects.filter(email=str(email)).exists()

    def save(self, user) -> None:
        # create (if not existing) or save
        data = entity_to_model(user)
        try:
            with transaction.atomic():
                UserModel.objects.create(**data)
        except IntegrityError as e:
            # Unique email collision or other constraint
            raise UserAlreadyExistsError("User with this email already exists") from e

    def update(self, user) -> None:
        try:
            with transaction.atomic():
                UserModel.objects.filter(id=user.id.value).update(
                    email=str(user.email),
                    password_hash=user.password_hash.value,
                    first_name=str(user.first_name),
                    last_name=str(user.last_name),
                    status=user.status.value
                )
        except IntegrityError as e:
            raise
```

Notes:

* `save` is optimistic: applications that need upsert or more advanced semantics can use `select_for_update()` in transactions.
* Translate infra exceptions to domain errors consistently.

---

# 5) Password hasher: `bcrypt_hasher.py` (infrastructure implementation of domain `PasswordHasher`)

Use `passlib` (recommended) or `bcrypt`. Example with `passlib.hash.bcrypt`.

```python
# user_management/infrastructure/auth/bcrypt_hasher.py
from passlib.hash import bcrypt
from ...domain.value_objects.password_hash import PasswordHash
from ...domain.services.password_policy import PasswordHasher

class BcryptPasswordHasher(PasswordHasher):
    def hash(self, plain: str) -> PasswordHash:
        hashed = bcrypt.using(rounds=12).hash(plain)
        return PasswordHash(hashed)

    def verify(self, hashed: PasswordHash, plain: str) -> bool:
        return bcrypt.verify(plain, hashed.value)
```

Notes:

* Keep salt + rounds configuration in Django settings.

---

# 6) Token provider: `jwt_provider.py` (infrastructure `TokenProvider`)

Use `pyjwt`. Keep signing key in Django settings. Provide `issue_token` and `verify_token`.

```python
# user_management/infrastructure/auth/jwt_provider.py
import jwt
import datetime
from django.conf import settings
from ...domain.services.token_provider import TokenProvider
from ...domain.value_objects.user_id import UserId

class JWTProvider(TokenProvider):
    def __init__(self, secret=None, algo="HS256", expiry_minutes=60):
        self.secret = secret or settings.JWT_SECRET
        self.algo = algo
        self.expiry_minutes = expiry_minutes

    def issue_token(self, user_id: UserId, claims: dict):
        now = datetime.datetime.utcnow()
        payload = {
            "sub": str(user_id.value),
            "iat": int(now.timestamp()),
            "exp": int((now + datetime.timedelta(minutes=self.expiry_minutes)).timestamp()),
            **claims
        }
        return jwt.encode(payload, self.secret, algorithm=self.algo)

    def verify_token(self, token: str) -> UserId:
        payload = jwt.decode(token, self.secret, algorithms=[self.algo])
        return UserId(uuid.UUID(payload["sub"]))
```

---

# 7) Outbox writer & dispatcher (`outbox/writer.py`, `outbox/dispatcher.py`)

**Writer**: store outbox events atomically in same DB transaction — use `transaction.on_commit()` to ensure outbox record is persisted after the successful transaction (or write inside same transaction).

```python
# user_management/infrastructure/outbox/writer.py
from django.db import transaction
from ..orm.models import OutboxEvent

def write_outbox_event(event_type: str, aggregate_id: str | None, payload: dict):
    # Use on_commit to ensure DB transaction success before writing if needed,
    # or write inside the transaction if you are already inside `transaction.atomic()`.
    def _save():
        OutboxEvent.objects.create(event_type=event_type, aggregate_id=aggregate_id, payload=payload)
    try:
        transaction.on_commit(_save)
    except Exception:
        # fallback to immediate write (depends on your strategy)
        _save()
```

**Dispatcher**: periodic job that picks unprocessed events and delivers them (HTTP, SMTP, or push to a message broker). Basic example (synchronous):

```python
# user_management/infrastructure/outbox/dispatcher.py
from django.utils import timezone
from ..orm.models import OutboxEvent

def flush_outbox(batch_size=50):
    events = OutboxEvent.objects.filter(processed_at__isnull=True).order_by("created_at")[:batch_size]
    for e in events:
        try:
            # deliver(e.event_type, e.payload)  # implement delivery per event_type
            # example: if e.event_type == "UserRegistered" -> call email service
            # After success:
            e.processed_at = timezone.now()
            e.attempts += 1
            e.save(update_fields=["processed_at", "attempts"])
        except Exception:
            e.attempts += 1
            e.save(update_fields=["attempts"])
```

Optionally expose `flush_outbox` via a Django management command or Celery periodic task.

---

# 8) Infra-level subscribers & wiring

**Infra subscribers** perform external side-effects, but do *not* belong to domain/application logic. They should be registered in startup (AppConfig.ready) or via a central module registration.

Example infra subscriber that writes an outbox entry when `UserRegistered` event occurs:

```python
# user_management/infrastructure/subscribers/notify_on_user_registered.py
from ...domain.events.user_events import UserRegistered
from ..outbox.writer import write_outbox_event

def on_user_registered(event: UserRegistered):
    payload = {
        "user_id": str(event.user_id.value),
        "email": str(event.email),
        "first_name": event.first_name,
        "last_name": event.last_name,
        "occurred_at": event.timestamp.isoformat()
    }
    write_outbox_event(event_type="UserRegistered", aggregate_id=str(event.user_id.value), payload=payload)
```

**Register infra subscribers** with application event bus at app startup:

```python
# user_management/infrastructure/subscribers/register.py
from user_management.application.event_bus import event_bus
from .notify_on_user_registered import on_user_registered
from ...domain.events.user_events import UserRegistered

def register_infra_subscribers():
    event_bus.subscribe(UserRegistered, on_user_registered)
```

Call `register_infra_subscribers()` from your Django app `AppConfig.ready()` (below).

---

# 9) AppConfig.ready — startup wiring (where to register app-wide subscribers)

In your `apps.py` for the Django app:

```python
# user_management/apps.py
from django.apps import AppConfig

class UserManagementConfig(AppConfig):
    name = "user_management"

    def ready(self):
        # wire infra/application subscribers
        try:
            from .infrastructure.subscribers.register import register_infra_subscribers
            from .application import register_subscribers as register_app_subscribers
            register_app_subscribers()
            register_infra_subscribers()
        except Exception:
            # don't raise on import-time issues in tests; handle/log appropriately
            pass
```

This ensures both **application-level** and **infrastructure-level** subscribers are registered to the in-process event bus.

---

# 10) Outbox delivery: worker options

Choose one depending on project scale:

* **Simple**: Django management command `flush_outbox` scheduled via cron or systemd timer. (Included above.)
* **Recommended if you already use workers**: Celery task to flush the outbox periodically (or push events to message broker from dispatcher).
* **Transactional guarantee**: Write outbox entries inside DB transaction in `on_commit` so they’re only persisted after successful commit.

Example minimal management command skeleton:

```python
# user_management/infrastructure/outbox/management/commands/flush_outbox.py
from django.core.management.base import BaseCommand
from ...dispatcher import flush_outbox

class Command(BaseCommand):
    help = "Flush user_management outbox"

    def handle(self, *args, **options):
        flush_outbox()
```

---

# 11) Transactions & consistency

* Save domain aggregate inside `transaction.atomic()` in repository layer; use `transaction.on_commit()` to enqueue outbox writes if you write outbox after commit.
* Avoid publishing domain events to external systems before transaction commit. The pattern above (application publishes to in-process bus after repository.save) is fine for in-process subscribers; for infra subscribers that create outbox records, ensure outbox writes happen inside the same DB transaction (or schedule via `on_commit`).

Typical flow:

1. Application handler calls repository.save(user) inside transaction (repository uses `atomic()`).
2. Handler pulls events (`user.pull_events()`).
3. Handler publishes events to in-process bus (application).
4. Infra subscriber listening to event writes an `OutboxEvent` (writer uses `on_commit()` to save reliably).
5. Outbox dispatcher/worker publishes to external systems and marks processed.

---

# 12) Testing strategy for infra layer

* **Unit tests** for mappers (model_to_entity/entity_to_model).
* **Integration tests** using Django TestCase with an in-memory sqlite or test DB: repository.save/find/update; unique-email error mapping.
* **Outbox tests**: simulate a handler publish and assert OutboxEvent is created and flushed.
* **Hasher & Token provider**: test `hash` + `verify` and `issue_token` + `verify_token` roundtrip.

---

# 13) Security & Operational notes

* Keep JWT secret and hashing rounds in Django settings (not hard-coded).
* Rotate hashing algorithm via `PasswordHasher` interface (hasher should expose `needs_rehash`).
* Limit outbox retries and add exponential backoff in dispatcher logic.
* Log failures and surface metrics (Prometheus) for outbox failures.
