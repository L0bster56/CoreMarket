from dataclasses import dataclass


@dataclass
class GetByEmailCommand:
    email: str
