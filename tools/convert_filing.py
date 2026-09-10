#!/usr/bin/env python3
"""EDGAR HTML → a filing fixture that can be CITED, not merely grepped (`C13`).

⚠⚠ **Changing this file re-renders every fixture and INVALIDATES every recording**
(a new `bundle_hash`). 4 of the 7 live-run failures came from here. Read
`sdd/design/rel1_design/L7-golden-set-filing-1.md` §5 before touching it.

    python3 tools/convert_filing.py IN.htm OUT.txt

⚠⚠ **Why this exists as a tool.** The first conversion was an inline script, and
its output caused **three of the six failures** in the `DX-23` live runs — 13
attempts and ~$7.88 that never produced a clean recording. An extraction
contract is built on **verbatim citation** (`X-01`, `RA-6`, `RA-131`), so how
the fixture renders is not cosmetic: it decides whether a correct reading can be
proved at all.

★★ **The rule this file exists to enforce: every cell must be a semantic unit.**
The old renderer split a currency table into pipe-separated cells including `$`
and `%` **as cells of their own**:

    SBU | 1,451 | 16 | % | 1,392 | 17 | % | 1,353 | 20 | % | 4,574 | 18 | %

⚠ Nobody can reproduce that character-for-character. A model quoting it inserted
`$ |` cells the document did not have, and `X-01` — correctly — refused the
citation. The delimiter artefact, not the reading, was wrong.

Now:

    SBU | 1,451 | 16% | 1,392 | 17% | 1,353 | 20% | 4,574 | 18% | 2,911 | 17%
    CNBU | $5,069 | $2,573 | $14,028 | $6,495

★ Pipes are kept — the column structure is what makes a segment table readable,
and `X-01` collapses whitespace anyway, so spacing was never the problem.
"""

from __future__ import annotations

import html
import pathlib
import re
import sys

#: ⚠⚠ Exotic whitespace → a plain space. `&nbsp;` and friends are HTML
#: RENDERING, carry no meaning, and are **demonstrably un-quotable**: a model
#: asked to reproduce `Form\xa010-K` returned `Form\x0cfff10-K` — it garbles the
#: character rather than copying it. ★ That was the FOURTH failure traced to this
#: converter, and the same lesson each time: **shape the fixture for citation.**
#: ⚠ A lone `\xa0` survived the old cleanup because it only collapsed RUNS of
#: two or more spaces.
_SPACES = str.maketrans(dict.fromkeys("\xa0\u2000\u2001\u2002\u2003\u2004\u2005\u2006" "\u2007\u2008\u2009\u200a\u202f\u205f\u3000\ufeff", " "))

#: ⚠ Rendering-only. Nothing here changes what the document SAYS.
_BLOCK_END = re.compile(r"(?i)</(p|div|h\d|li|table)>")
_ROW_END = re.compile(r"(?i)</tr>")
_CELL_END = re.compile(r"(?i)</t[dh]>")
_BR = re.compile(r"(?i)<br\s*/?>")
_DROP = re.compile(r"(?is)<(script|style|ix:header).*?</\1>")
_TAG = re.compile(r"<[^>]+>")


def _merge_symbols(cells: list[str]) -> list[str]:
    """`C13` — fold `$` and `%` into the value they belong to.

    ⚠ `$` binds to the FOLLOWING cell, `%` to the PRECEDING one, because that is
    how each reads aloud. A lone symbol with nothing to bind to is kept, so
    nothing is silently dropped.
    """
    out: list[str] = []
    pending_currency = ""
    for cell in cells:
        if cell == "$":
            pending_currency = "$"
            continue
        if cell == "%":
            if out:
                out[-1] = out[-1] + "%"
            else:
                out.append("%")
            continue
        out.append(pending_currency + cell)
        pending_currency = ""
    if pending_currency:
        out.append(pending_currency)
    return out


def convert(raw: str) -> str:
    text = _DROP.sub(" ", raw)
    text = _CELL_END.sub("\t", text)
    text = _ROW_END.sub("\n", text)
    text = _BLOCK_END.sub("\n", text)
    text = _BR.sub(" ", text)
    text = _TAG.sub("", text)
    text = html.unescape(text).translate(_SPACES)

    lines = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.split("\t")]
        cells = [c for c in cells if c]
        if not cells:
            lines.append("")
            continue
        cells = _merge_symbols(cells)
        lines.append(" | ".join(cells) if len(cells) > 1 else cells[0])

    out = strip_page_furniture("\n".join(lines))
    out = re.sub(r"[ \xa0]{2,}", " ", out)
    return re.sub(r"\n{3,}", "\n\n", out)


#: A printed page footer — `35 | 2025 Q3 10-Q`. ⚠ Anchored at both ends: a
#: LINE that is nothing but page furniture. Nothing that carries prose matches.
_PAGE_FOOTER = re.compile(r"^\s*\d+\s*\|\s*20\d\d\s+Q\d\s+10-[QK]\s*$")

#: The running header EDGAR puts at the top of every page.
_PAGE_HEADER = "Table of Contents"


def strip_page_furniture(text: str) -> str:
    """Delete whole lines that are printed page furniture, nothing else.

    ⚠⚠ **MEASURED, `DX-35`.** MU's filing reads:

        We have also signed a non-binding term sheet with the State of
        35 | 2025 Q3 10-Q          <- page footer
        Table of Contents          <- running header
        New York that provides for ...

    ★★ A sentence runs ACROSS a page break, and the furniture sits inside it.
    The model quoted the sentence the way a human reads it — correctly — and
    `X-01` refused the citation because the quote is not in the document. Four
    `E-02` items died on one quote and, because `X-01` aborts, took the other
    47 with them.

    ★★★ **This is the converter testing itself, for the sixth time.** Page
    numbers are an artefact of PAGINATION, which the text rendering has already
    thrown away; keeping them is keeping half of a layout. Exactly `_merge_
    symbols`' argument about `$` cells: the delimiter artefact was wrong, not
    the reading.

    ⚠ Deliberately line-granular and anchored. It removes a line that is
    ENTIRELY furniture and never edits a line that carries prose, so it cannot
    delete a sentence, a figure, or a table row.

    ★ Measured on both fixtures 2026-09-09: 1,634 chars removed from MU and
    1,116 from AMD, and **zero** of the 95 already-recorded `E-01` quotes
    stopped resolving. The re-render `L7` §5 warns about was free.
    """
    return "".join(line for line in text.splitlines(True)
                   if not _PAGE_FOOTER.match(line)
                   and line.strip() != _PAGE_HEADER)


def main() -> int:
    if len(sys.argv) != 3:
        print(__doc__.splitlines()[2].strip())
        return 2
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    body = convert(src.read_text(encoding="utf-8", errors="replace"))
    dst.write_text(body, encoding="utf-8")
    print(f"  ✅ {dst} — {len(body):,} chars, {body.count(chr(10)):,} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
