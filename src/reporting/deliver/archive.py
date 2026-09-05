"""RP-32 — all renderings of one artifact are CONTENT-equivalent (AC-9.24c).

Presentation may differ per medium; **a value present in one rendering and
absent in another is a defect**, as is a value that differs. Checked
mechanically by extracting the class-tagged fields from each rendering and
diffing — which is exactly what this module does, rather than trusting that two
templates were written from the same object.
"""

from __future__ import annotations

import re

from src.reporting.errors import RenderingsDivergedError

#: Markdown table row: | field | value | glyph LABEL | source | as_of |
_MD_ROW = re.compile(r"^\|\s*([a-z_]+)\s*\|\s*(.*?)\s*\|\s*\S+\s+([A-Z]+)\s*\|", re.M)
#: HTML table row, same five cells.
_HTML_ROW = re.compile(
    r"<tr><td>([a-z_]+)</td><td>(.*?)</td><td class=\"cls \w+\">\S+\s+([A-Z]+)</td>",
    re.S,
)


def fields_from_markdown(text: str) -> dict:
    return {m.group(1): (m.group(2), m.group(3)) for m in _MD_ROW.finditer(text)
            if m.group(1) != "field"}


def fields_from_html(text: str) -> dict:
    import html as _html
    return {m.group(1): (_html.unescape(m.group(2)), m.group(3))
            for m in _HTML_ROW.finditer(text)}


def assert_content_equivalent(html_text: str, markdown_text: str) -> None:
    """Raise unless the two renderings carry the same class-tagged field set."""
    a, b = fields_from_html(html_text), fields_from_markdown(markdown_text)
    if set(a) != set(b):
        raise RenderingsDivergedError(
            f"renderings carry different fields: html-only {sorted(set(a) - set(b))}, "
            f"markdown-only {sorted(set(b) - set(a))}. A value present in one and "
            f"absent in another is a defect (RP-32)"
        )
    differing = {k: (a[k], b[k]) for k in sorted(a) if a[k] != b[k]}
    if differing:
        raise RenderingsDivergedError(
            f"renderings disagree on {sorted(differing)}: {differing}. Presentation "
            f"may differ per medium; content may not (RP-32)"
        )
