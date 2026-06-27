from dataclasses import dataclass
from uuid import UUID


@dataclass
class UpdateUserCommand:
    user_id: UUID
    email: str
    password: str
