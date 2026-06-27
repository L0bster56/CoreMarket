"""Markdown rendering via mistune 3.

escape=False on the renderer allows raw HTML in markdown source.
Content is admin-authored (trusted), so no sanitization layer is applied.
External links receive target="_blank" rel="noopener noreferrer" automatically.
"""
from __future__ import annotations

import re
from typing import Optional

import mistune
from mistune.renderers.html import HTMLRenderer

_EXTERNAL_URL_RE = re.compile(r'^https?://', re.IGNORECASE)


class _SafeLinkRenderer(HTMLRenderer):
    """HTMLRenderer that opens external links in a new tab."""

    def link(self, text: str, url: str, title: Optional[str] = None) -> str:
        base = super().link(text, url, title)
        if url and _EXTERNAL_URL_RE.match(url):
            # Inject safety attributes without re-building the URL logic
            return base.replace('<a ', '<a target="_blank" rel="noopener noreferrer" ', 1)
        return base


class MistureRenderer:
    def __init__(self) -> None:
        self._render = mistune.create_markdown(
            renderer=_SafeLinkRenderer(escape=False),
            plugins=['strikethrough', 'table', 'task_lists'],
        )

    def render(self, text: str) -> str:
        return self._render(text)
