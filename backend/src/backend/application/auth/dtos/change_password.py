from dataclasses import dataclass


@dataclass
class ChangePasswordCommand:
    old_password: str
    new_password: str
