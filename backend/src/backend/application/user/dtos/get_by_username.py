from dataclasses import dataclass


@dataclass
class GetByUsernameCommand:
    username: str
