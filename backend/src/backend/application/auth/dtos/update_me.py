from dataclasses import dataclass, field


@dataclass
class UpdateMeCommand:
    username: str | None = field(default=None)
    avatar_url: str | None = field(default=None)
