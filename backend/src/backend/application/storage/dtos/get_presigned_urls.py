from dataclasses import dataclass, field


@dataclass
class GetPresignedUrlsCommand:
    keys: list[str]
    expires_in: int = field(default=3600)


@dataclass
class GetPresignedUrlsResult:
    urls: dict[str, str]
