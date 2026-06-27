from typing import Protocol


class MarkdownRenderer(Protocol):
    def render(self, text: str) -> str: ...
