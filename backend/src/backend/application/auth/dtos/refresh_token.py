from dataclasses import dataclass


@dataclass
class RefreshTokenCommand:
    refresh_token: str


@dataclass
class RefreshTokenResult:
    access_token: str
    refresh_token: str
    token_type: str
