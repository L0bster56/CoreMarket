"""
Tests for MistureRenderer (infrastructure/markdown/mistune_renderer.py).

Covers:
- Headings (h1–h3): correct HTML tags produced
- Links: <a href="..."> with correct href and text
- Code blocks: inline <code> and fenced <pre><code>
- Text formatting: bold, italic, paragraphs
- HTML passthrough: escape=False means raw HTML is not double-escaped
- Edge cases: empty string, plain text, nested markdown
"""
from __future__ import annotations

import pytest

from src.backend.infrastructure.markdown.mistune_renderer import MistureRenderer


class TestMistureRendererHeadings:
    def test_h1_tag_present(self):
        result = MistureRenderer().render("# Title")
        assert "<h1>" in result

    def test_h1_contains_text(self):
        result = MistureRenderer().render("# My Title")
        assert "My Title" in result

    def test_h1_closing_tag(self):
        result = MistureRenderer().render("# Title")
        assert "</h1>" in result

    def test_h2_tag_present(self):
        result = MistureRenderer().render("## Section")
        assert "<h2>" in result

    def test_h2_contains_text(self):
        result = MistureRenderer().render("## Section Name")
        assert "Section Name" in result

    def test_h3_tag_present(self):
        result = MistureRenderer().render("### Subsection")
        assert "<h3>" in result

    def test_h3_contains_text(self):
        result = MistureRenderer().render("### Sub")
        assert "Sub" in result


class TestMistureRendererLinks:
    def test_anchor_tag_present(self):
        result = MistureRenderer().render("[text](https://example.com)")
        assert "<a " in result

    def test_href_attribute_present(self):
        result = MistureRenderer().render("[text](https://example.com)")
        assert "href=" in result

    def test_href_value_is_correct(self):
        result = MistureRenderer().render("[click](https://example.com)")
        assert "https://example.com" in result

    def test_link_text_rendered(self):
        result = MistureRenderer().render("[click here](https://example.com)")
        assert "click here" in result

    def test_closing_anchor_tag(self):
        result = MistureRenderer().render("[x](https://x.com)")
        assert "</a>" in result

    def test_link_with_path(self):
        result = MistureRenderer().render("[docs](/api/v1/items)")
        assert "/api/v1/items" in result


class TestMistureRendererCodeBlocks:
    def test_inline_code_tag(self):
        result = MistureRenderer().render("`code`")
        assert "<code>" in result

    def test_inline_code_content(self):
        result = MistureRenderer().render("`my_function()`")
        assert "my_function()" in result

    def test_fenced_pre_tag(self):
        result = MistureRenderer().render("```\nprint('hello')\n```")
        assert "<pre>" in result

    def test_fenced_code_tag(self):
        result = MistureRenderer().render("```\nhello world\n```")
        assert "<code>" in result

    def test_fenced_code_content_preserved(self):
        result = MistureRenderer().render("```\nhello world\n```")
        assert "hello world" in result

    def test_language_hint_appears_in_output(self):
        result = MistureRenderer().render("```python\npass\n```")
        assert "python" in result

    def test_multiline_code_block(self):
        md = "```\nline1\nline2\nline3\n```"
        result = MistureRenderer().render(md)
        assert "line1" in result
        assert "line2" in result
        assert "line3" in result


class TestMistureRendererFormatting:
    def test_bold_renders_strong_tag(self):
        result = MistureRenderer().render("**bold text**")
        assert "<strong>" in result

    def test_bold_content_present(self):
        result = MistureRenderer().render("**bold text**")
        assert "bold text" in result

    def test_italic_renders_em_tag(self):
        result = MistureRenderer().render("*italic text*")
        assert "<em>" in result

    def test_italic_content_present(self):
        result = MistureRenderer().render("*italic text*")
        assert "italic text" in result

    def test_paragraph_wrapped_in_p_tag(self):
        result = MistureRenderer().render("paragraph text")
        assert "<p>" in result

    def test_paragraph_content_present(self):
        result = MistureRenderer().render("paragraph text")
        assert "paragraph text" in result


class TestMistureRendererHTMLPassthrough:
    def test_empty_string_returns_empty(self):
        result = MistureRenderer().render("")
        assert result.strip() == ""

    def test_plain_text_passes_through(self):
        result = MistureRenderer().render("Hello world")
        assert "Hello world" in result

    def test_html_not_double_escaped_with_escape_false(self):
        # With escape=False, < and > in raw HTML are NOT turned into &lt;/&gt;
        result = MistureRenderer().render("<b>bold</b>")
        assert "&lt;" not in result

    def test_raw_html_content_appears_in_output(self):
        result = MistureRenderer().render("<b>bold</b>")
        assert "bold" in result

    def test_script_content_passes_through(self):
        # escape=False: inline HTML including scripts is not sanitized.
        # Content rendered by this renderer must come from trusted sources.
        result = MistureRenderer().render("<script>alert(1)</script>")
        assert "alert(1)" in result

    def test_multiple_headings(self):
        md = "# H1\n## H2\n### H3"
        result = MistureRenderer().render(md)
        assert "<h1>" in result
        assert "<h2>" in result
        assert "<h3>" in result

    def test_mixed_content_renders(self):
        md = "# Title\n\nA paragraph with **bold** and *italic*.\n\n[link](https://x.com)"
        result = MistureRenderer().render(md)
        assert "<h1>" in result
        assert "<strong>" in result
        assert "<em>" in result
        assert "<a " in result


class TestMistureRendererTables:
    def test_table_tag_present(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |"
        result = MistureRenderer().render(md)
        assert "<table>" in result

    def test_table_header_row(self):
        md = "| Name | Age |\n|------|-----|\n| Bob  | 30  |"
        result = MistureRenderer().render(md)
        assert "<thead>" in result
        assert "<th>" in result
        assert "Name" in result
        assert "Age" in result

    def test_table_body_row(self):
        md = "| Name | Age |\n|------|-----|\n| Bob  | 30  |"
        result = MistureRenderer().render(md)
        assert "<tbody>" in result
        assert "<td>" in result
        assert "Bob" in result
        assert "30" in result

    def test_table_multiple_rows(self):
        md = "| A | B |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |"
        result = MistureRenderer().render(md)
        assert "1" in result
        assert "3" in result


class TestMistureRendererStrikethrough:
    def test_strikethrough_del_tag(self):
        result = MistureRenderer().render("~~deleted~~")
        assert "<del>" in result

    def test_strikethrough_content_preserved(self):
        result = MistureRenderer().render("~~removed text~~")
        assert "removed text" in result

    def test_strikethrough_closing_tag(self):
        result = MistureRenderer().render("~~x~~")
        assert "</del>" in result

    def test_strikethrough_inline_with_text(self):
        result = MistureRenderer().render("keep ~~gone~~ keep")
        assert "keep" in result
        assert "<del>" in result


class TestMistureRendererTaskLists:
    def test_checked_checkbox_present(self):
        result = MistureRenderer().render("- [x] done")
        assert 'type="checkbox"' in result
        assert "checked" in result

    def test_unchecked_checkbox_present(self):
        result = MistureRenderer().render("- [ ] todo")
        assert 'type="checkbox"' in result

    def test_checkbox_is_disabled(self):
        result = MistureRenderer().render("- [ ] todo")
        assert "disabled" in result

    def test_task_list_item_text(self):
        result = MistureRenderer().render("- [x] deploy server")
        assert "deploy server" in result

    def test_mixed_task_list(self):
        md = "- [x] done\n- [ ] pending"
        result = MistureRenderer().render(md)
        assert "done" in result
        assert "pending" in result


class TestMistureRendererExternalLinks:
    def test_external_link_opens_new_tab(self):
        result = MistureRenderer().render("[go](https://example.com)")
        assert 'target="_blank"' in result

    def test_external_link_has_rel_noopener(self):
        result = MistureRenderer().render("[go](https://example.com)")
        assert "noopener" in result
        assert "noreferrer" in result

    def test_http_link_also_gets_target(self):
        result = MistureRenderer().render("[go](http://example.com)")
        assert 'target="_blank"' in result

    def test_internal_link_no_target(self):
        result = MistureRenderer().render("[go](/about)")
        assert 'target="_blank"' not in result

    def test_internal_link_no_rel(self):
        result = MistureRenderer().render("[go](/about)")
        assert "noopener" not in result

    def test_external_link_href_preserved(self):
        result = MistureRenderer().render("[docs](https://docs.example.com/api)")
        assert "https://docs.example.com/api" in result

    def test_code_block_language_class(self):
        result = MistureRenderer().render("```python\nprint('hello')\n```")
        assert 'class="language-python"' in result
