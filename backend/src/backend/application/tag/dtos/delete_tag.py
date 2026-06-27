from dataclasses import dataclass
from uuid import UUID


@dataclass
class DeleteTagCommand:
    tag_id: UUID
