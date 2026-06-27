from dataclasses import dataclass
from uuid import UUID


@dataclass
class GetByIdCommand:
    user_id: UUID
