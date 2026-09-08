"""The self-contained HTML rendering — the artifact of record (RP-31, RP-32, RP-34).

```
RP-31: no external stylesheet, no CDN font, no remote image, no network
fetch of any kind. THIS IS P6, NOT AESTHETICS — an artifact that needs a
live server to render is not viewable later, and "later" is exactly when a
decision gets audited.
```

⚠ **RP-34: no script.** A self-contained report needs none, an emailed HTML file
that executes is a needless risk surface, and script-free is what guarantees it
still renders after the next browser generation.
"""

from __future__ import annotations

import html as _html
import re

from src.reporting.errors import ExternalRefError, ScriptPresentError
from src.reporting.render.classes import GLYPH, LABEL

#: Anything that would reach the network. Checked on the EMITTED BYTES, not on
#: intent (AC-9.24a) — the only check that cannot be satisfied by good manners.
_EXTERNAL = re.compile(
    r"""(?:src|href)\s*=\s*["'](?!\#)(?:https?:|//|data:(?!image/svg\+xml;base64,))"""
    r"""|@import|url\(\s*["']?https?:""",
    re.I,
)
_SCRIPT = re.compile(r"<\s*script\b|\son[a-z]+\s*=", re.I)

#: Class styling. ★ Glyph and label carry the class; colour only reinforces
#: (QP-1 residual, AC-9.24d). Both palettes are declared so the card does not
#: invert into illegibility in dark mode.
_CSS = """
:root { --bg:#ffffff; --fg:#16181d; --muted:#5b6270; --rule:#d8dce4;
        --fact:#0b6b3a; --computation:#1c4f9c; --judgement:#8a5a00; --warn:#8a1f11; }
@media (prefers-color-scheme: dark) {
  :root { --bg:#14161a; --fg:#e8eaf0; --muted:#9aa3b2; --rule:#2b3038;
          --fact:#5fd39b; --computation:#8ab4ff; --judgement:#e0b256; --warn:#ff9a8a; }
}
body { background:var(--bg); color:var(--fg); margin:0; padding:2rem 1.25rem;
       font:16px/1.55 ui-sans-serif,-apple-system,Segoe UI,Roboto,Helvetica,Arial,sans-serif; }
.wrap { max-width:52rem; margin:0 auto; }
h1 { font-size:1.5rem; margin:0 0 .25rem; } h2 { font-size:1.05rem; margin:1.75rem 0 .5rem; }
.sub { color:var(--muted); margin:0 0 1.5rem; }
.banner { border:2px solid var(--warn); color:var(--warn); border-radius:8px;
          padding:.85rem 1rem; margin:0 0 1.5rem; font-weight:600; }
table { border-collapse:collapse; width:100%; }
th,td { text-align:left; padding:.45rem .6rem; border-bottom:1px solid var(--rule);
        vertical-align:top; }
th { color:var(--muted); font-weight:600; font-size:.85rem; text-transform:uppercase;
     letter-spacing:.04em; }
.cls { white-space:nowrap; font-weight:600; font-size:.85rem; }
.fact { color:var(--fact); } .computation { color:var(--computation); }
.judgement { color:var(--judgement); }
.overflow { overflow-x:auto; }
ul { margin:.25rem 0 0 1.1rem; padding:0; } li { margin:.2rem 0; }
.foot { color:var(--muted); font-size:.85rem; margin-top:2rem;
        border-top:1px solid var(--rule); padding-top:.75rem; }
"""


def render_html(card) -> str:
    """Deterministic: same card, same bytes (RP-28). Validated before returning."""
    e = _html.escape
    rows = "\n".join(
        f'      <tr><td>{e(f.field)}</td><td>{e(_fmt(f.value))}</td>'
        f'<td class="cls {f.reliability}">{GLYPH[f.reliability]} {LABEL[f.reliability]}</td>'
        f'<td>{e(f.source)}</td><td>{e(f.as_of.isoformat())}</td></tr>'
        for f in card.fields
    )
    gaps = "\n".join(f"      <li>{e(g)}</li>" for g in card.data_gaps) or \
        "      <li>none</li>"
    stubs = "".join(
        '\n    <h2>Stubs in this run</h2>\n    <ul>\n' +
        "\n".join(f'      <li>{e(s["domain"])} <code>{e(s["job"])}</code>: '
                  f'{e(s["behaviour"])} — replaced at {e(s["replaced_at"])} '
                  f'({e(s["rule"])})</li>' for s in card.stubs) +
        "\n    </ul>"
    ) if card.stubs else ""
    banner = (
        f'\n    <p class="banner">⚠ NOT ACTIONABLE — {e(card.not_actionable_reason or "")}</p>'
        if not card.actionable else ""
    )

    doc = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(card.ticker)} — discipline card {e(card.as_of.isoformat())}</title>
<style>{_CSS}</style></head>
<body><div class="wrap">
    <h1>{e(card.ticker)} — discipline card</h1>
    <p class="sub">as of {e(card.as_of.isoformat())}</p>{banner}
    <h2>What would prove this wrong</h2>
    <p>{e(card.falsifier)}</p>
    <h2>Fields</h2>
    <div class="overflow"><table>
      <tr><th>field</th><th>value</th><th>reliability</th><th>source</th><th>as of</th></tr>
{rows}
    </table></div>
    <h2>Data gaps</h2>
    <ul>
{gaps}
    </ul>
    <h2>Risk</h2>
    <ul>
      <li>status: {e(card.alerts_status)}</li>
    </ul>{stubs}
    <p class="foot">Reliability classes are marked by glyph and label, never by
    colour alone. This file is self-contained and fetches nothing.</p>
</div></body></html>
"""
    return assert_self_contained(doc)


def assert_self_contained(doc: str) -> str:
    """AC-9.24a / AC-9.24b — asserted on the EMITTED BYTES, not on intent."""
    hit = _EXTERNAL.search(doc)
    if hit:
        raise ExternalRefError(
            f"HTML rendering references a network resource: {hit.group(0)!r}. An "
            f"artifact that needs a live server is not viewable later, and later is "
            f"when a decision gets audited (RP-31, P6)"
        )
    hit = _SCRIPT.search(doc)
    if hit:
        raise ScriptPresentError(
            f"HTML rendering contains script or an inline handler: {hit.group(0)!r} "
            f"(RP-34)"
        )
    return doc


def _fmt(value) -> str:
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "—"
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)
