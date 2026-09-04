# L2: Module Specification — Money

> ⚠⚠ **ABSORBED COPY — this is now the AUTHORITATIVE one.** `src/shared/` moved into
> `collective-investment-ai-assistant` on 2026-09-04 (`questions.md` `QR-22` — absorption is
> per-domain). The code this spec governs lives **here**, so this spec is edited **here**.
> ⚠ `../ai-investment-pipeline` still carries a copy because ~10 of its documents cross-reference it;
> that copy is **historical** and must not be edited. It is reconciled at `MS-8`.
> **Path deliberately mirrors upstream's** (`sdd/design/rel6_design/`) so `MS-8` is a merge, not a
> move (`PG-8`).

> **Tier:** `sdd/design/rel6_design/` — **design tier, not yet authoritative.**
> **Parent:** [`L0-system-vision.md`](L0-system-vision.md) **INV-001**, **M-5** ·
> [`L4-coding-standards.md`](L4-coding-standards.md) §1.1
> **Domain:** D-00 Shared Infrastructure · **Seat:** none (cross-cutting)
> **Path:** `src/shared/money.py`
> **Prior art it inherits:** `constitution.md` INV-5, `F4_data_plane/spec.md` CT-4.1/CT-4.2,
> `pipeline/portfolio/{snapshot,book_state}.py`

## Document Control

| Version | Date | Author | Changes |
|---|---|---|---|
| 0.4.0 | 2026-08-18 | Victor | ⚠ **`F4`'s `AC-4.9` migrated here as `AC-M.1` before F4's deletion** (G-7: acceptance criteria migrate into the receiving L-spec *before* an F-spec is retired). It was **live** — 19 passing tests — and would otherwise have been orphaned. `AC-M.2`/`AC-M.3` added for MO-8/9/10. |
| 0.3.0 | 2026-08-18 | Victor | ✅ **QM-1/3/4 closed.** `sum_money(items, currency)` rather than `+ 0` — ★ *`sum()` over an empty iterable returns `0`, which has no currency and is the untagged value INV-001 forbids*. No optional `as_of` — an amount is not an observation. **No fractional shares (MO-10)**, and ⚠ **that quantises position size**: a $4,000 sleeve in a $400 name steps in 10 % increments, so D-06 sizes with `floor` and **reports the residual cash**. |
| 0.2.0 | 2026-08-18 | Victor | ⚠ **Cross-spec audit: MO-4 read literally forbade the entire D-02 feature panel.** *"float never appears in a stored field"* prohibits `ret_1d` — a stored float. **MO-8** states the boundary that was always intended and never written: **a same-currency ratio is dimensionless and leaves the Money type; division is where the type is left.** **MO-9** keeps the other half — a cross-currency ratio is **an unrecorded FX rate wearing a return's clothing** (INV-5). Pairs with D-02 **FE-32**. |
| 0.1.1 | 2026-08-15 | Victor | Cascade from L0 **v0.10.0**: display formatting is **D-09 Reporting** (the domain narrowed). No contract, rule or AC change. |
| 0.1.0 | 2026-08-14 | Victor | Initial draft — closes **Q-1**. |

## Why this module exists first

`src/shared/money.py` is imported by every domain, so in a parallel build it must exist before the
first domain moves. Nothing else in `src/` can be written correctly until it does.

**The semantics are not new.** `constitution.md` INV-5 has required explicit currency since before
this redesign; F4 requires `price_currency`/`total_currency` on every leg; `portfolio_state.json`
already holds cash per-currency and records `fx_rate_used`. What has never existed is a **type**:
there is no `Money` class anywhere in the 38,669 legacy lines, and no `Decimal` usage. Currency
travels as a sibling string field next to a float, by convention, in each place that remembers.

This module turns a convention that is *followed* into one that is *enforced*.

---

# 1. MODULE OVERVIEW

```text
THIS MODULE DOES:
  ✓ Define Money — an integer amount in minor units, inseparable from its currency
  ✓ Provide exact arithmetic within a currency
  ✓ Refuse arithmetic across currencies, loudly
  ✓ Define FxRate and the one explicit conversion path
  ✓ Define the on-disk representation for parquet and JSON
  ✓ Provide explicit, documented rounding

THIS MODULE DOES NOT:
  ✗ Fetch FX rates            (D-07 Data Engine)
  ✗ Decide when to convert    (the calling domain)
  ✗ Format for display        (D-09 Reporting)
  ✗ Store anything            (stateless, pure)
  ✗ Know about tickers, positions, P&L, or any business concept
```

---

# 2. DATA MODELS

## 2.1 Money

```python
@dataclass(frozen=True, slots=True)
class Money:
    """An exact monetary amount, inseparable from its currency (INV-001).

    amount_minor: signed integer in the currency's minor unit (cents for CAD/USD).
                  Negative is legal — it means a debit, a loss, or a short cash balance.
    currency:     ISO-4217 alpha-3, uppercase. Must be in SUPPORTED_CURRENCIES.
    """
    amount_minor: int
    currency: str
```

**Why integer minor units and not `Decimal`.** Integers are exact, hash cleanly, serialize
unambiguously, and compare without tolerance. `Decimal` appears only as an *intermediate* inside
multi-step computation (§4.3), never as a stored field — a stored `Decimal` reintroduces the
precision-and-serialization questions the integer exists to remove.

**Why `frozen`.** A monetary value that can be mutated in place can be mutated by one holder and
observed by another. Every operation returns a new `Money`.

## 2.2 Currency

```python
SUPPORTED_CURRENCIES: dict[str, int] = {   # code → minor-unit exponent
    "CAD": 2,
    "USD": 2,
}
BASE_CURRENCY: str = "CAD"                 # M-5
```

Scope is CAD and USD only — the book holds nothing else (L0 §12, M-5). The exponent is a **table,
not the constant 2**, because a zero-decimal currency (JPY) or three-decimal currency (KWD) would
otherwise be silently wrong by a factor of 100 the day one is added. Constructing `Money` with an
unsupported code raises; it does not default to base.

## 2.3 FxRate

Inherits the shape already written to `portfolio_state.json` as `fx_rate_used`.

```python
@dataclass(frozen=True, slots=True)
class FxRate:
    pair: str            # "USDCAD" — convert FROM the first code TO the second
    rate: Decimal        # units of `to` per 1 unit of `from`
    as_of: datetime      # UTC, when the rate was observed
    source: str          # e.g. "FMP"

    @property
    def from_currency(self) -> str: return self.pair[:3]
    @property
    def to_currency(self) -> str:   return self.pair[3:]
```

`rate` is `Decimal`, not `float` — an FX rate multiplies every converted amount in the book, so a
float's representation error is applied at scale.

---

# 3. FUNCTIONAL REQUIREMENTS

## FR-001: Construct a Money

| Constructor | Use | Note |
|---|---|---|
| `Money(1500, "CAD")` | internal, from a known minor amount | primary |
| `Money.zero("CAD")` | an explicit zero **in a currency** | there is no currency-free zero — see §4.4 |
| `Money.from_decimal_str("15.00", "CAD")` | **external data** — the preferred boundary constructor | exact; no float ever exists |
| `Money.from_float(15.0, "CAD")` | external data that is already a float | **discouraged and deliberately greppable**; routes through `Decimal(str(x))` |

**Steps for `from_decimal_str`:**
```text
1. Reject unsupported currency                        → UnsupportedCurrencyError
2. Parse as Decimal; reject non-numeric               → InvalidAmountError
3. Reject more fractional digits than the exponent    → PrecisionLossError
   ("15.005" into a 2-dp currency is a caller bug, not a rounding request)
4. Scale by 10**exponent, quantize ROUND_HALF_UP, cast to int
5. Return Money
```

Step 3 matters: silently rounding sub-cent input is how a reconciliation ends up off by a few cents
with no record of where. If the caller genuinely wants rounding they call `quantize` explicitly.

## FR-002: Arithmetic within a currency

```python
a + b        # Money, same currency         → Money        (exact)
a - b        # Money, same currency         → Money        (exact)
-a           # negation                      → Money
abs(a)       #                               → Money
a * n        # n: int (share count, periods) → Money        (exact)
a / n        # n: int                        → Money        (explicit rounding, §4.3)
a / b        # Money, same currency          → Decimal      (a ratio, dimensionless)
```

Mixed currency on `+`, `-`, or `/`-as-ratio → **`CurrencyMismatchError`**. Always. There is no
`allow_mixed` flag and no implicit conversion to base.

## FR-003: Multiply by a rate or weight

```python
a.mul_rate(Decimal("0.075"))                       # → Money, ROUND_HALF_UP
a.mul_rate(Decimal("0.075"), rounding=ROUND_DOWN)  # rounding is a named argument
```

Separate from `*` because `* int` is exact and `* rate` is not. Sharing one operator would let a
lossy operation look identical to an exact one at the call site.

## FR-004: Compare

| Operation | Same currency | Different currency |
|---|---|---|
| `==`, `!=` | exact integer comparison | **`False`** — never raises |
| `<`, `<=`, `>`, `>=` | exact integer comparison | **raises `CurrencyMismatchError`** |
| `hash()` | over `(amount_minor, currency)` | — |

The asymmetry is deliberate. Python requires `__eq__` to tolerate any object — raising would break
`in`, `dict`, `set`, and every `assertEqual`. Ordering carries no such requirement, and "is this
USD amount bigger than that CAD amount" is a question with no answer, so it fails loudly.

## FR-005: Convert currency — the only path across a currency boundary

```python
def convert(self, rate: FxRate) -> Money:
    """Convert to rate.to_currency. The ONLY way a Money changes currency."""
```

```text
1. rate.from_currency must equal self.currency   → FxDirectionError
2. rate.to_currency must be supported            → UnsupportedCurrencyError
3. Decimal(amount_minor) × rate.rate, quantize ROUND_HALF_UP → int
4. Return Money(result, rate.to_currency)
```

**Three rules that make conversion auditable rather than merely possible:**

| Rule | Statement |
|---|---|
| **FX-1** | Conversion is **explicit at the call site**. No operation converts implicitly, including comparison, summation and aggregation. |
| **FX-2** | **Any artifact containing a converted value must record the `FxRate` used** — pair, rate, `as_of`, source. A converted number without its rate is not reproducible, and reproducibility is the whole point (AP-6). `portfolio_state.json` already does this as `fx_rate_used`. |
| **FX-3** | **No rate ⇒ no number.** When a rate is unavailable, the dependent value is reported as **unavailable**, never computed from a stale or assumed rate. This is P5, and it is the behaviour `snapshot.py` already implements — `nav_base` is `None` rather than a NAV built on a guess. |

FX-3 is inherited rather than invented, and it is the rule most likely to be eroded under pressure:
a missing NAV looks like a bug, so the temptation is to reach for yesterday's rate. A NAV that is
quietly wrong is worse than a NAV that is visibly absent.

## FR-006: Sum a collection

```python
def sum_money(items: Iterable[Money], currency: str) -> Money:
    """Sum same-currency amounts. `currency` is REQUIRED — it is the answer for
    an empty iterable, and it asserts the caller's expectation for a non-empty one."""
```

Requiring the currency removes the empty-sum ambiguity (`sum([])` cannot know its currency) and
turns a mixed-currency list into an immediate `CurrencyMismatchError` instead of a plausible total.

---

# 4. ARITHMETIC RULES

## 4.1 Summary

| Rule | Statement |
|---|---|
| **MO-1** | A monetary value is always `(amount_minor: int, currency: str)`. A bare int is not a monetary value (**INV-001**). |
| **MO-2** | Cross-currency arithmetic raises. There is no implicit conversion, ever. |
| **MO-3** | Every lossy operation names its rounding mode. Default `ROUND_HALF_UP`. |
| **MO-4** | `float` never appears in a stored field, a comparison, or an intermediate that feeds a stored field. |
| **MO-5** | `Decimal` is permitted only as an intermediate, quantized back to `int` before return. |
| **MO-10** | ★ **Share quantity is a plain `int`.** No fractional shares (Victor, 2026-08-18). ⚠ **Consequence: position size is QUANTISED, and the granularity is not negligible at this book** — a $4,000 sleeve in a $400 name buys 10 shares, so the smallest expressible step is **10 % of the position**. D-06's sizing output is therefore `floor(budget / price)` and **the residual cash is reported, not silently absorbed** |
| **MO-8** | ★★ **A RATIO of two `Money` values of the SAME currency is dimensionless and is no longer money.** ⚠ **MO-4 read literally — *"float never appears in a stored field"* — forbids `ret_1d`, every return, every percentage and therefore the whole D-02 feature panel.** It does not: **division is where the type is left.** The result is a plain float, MO-4 stops governing it, and the constraint that remains is **MO-9** |
| **MO-9** | ★ **A cross-currency ratio is forbidden** (MO-2's shape). `usd_price / cad_price` is not dimensionless — it is an unrecorded FX rate wearing a return's clothing, and it is exactly the implicit conversion **INV-5** exists to prevent |
| **MO-6** | Negative amounts are legal and meaningful. No operation silently clamps to zero. |
| **MO-7** | Currency conversion happens only via `convert(FxRate)` and is recorded (FX-2). |

## 4.2 Why not "banker's rounding"

`ROUND_HALF_UP` is the default, and the sample L4 mislabels its own `ROUND_HALF_UP` example as
"banker's rounding" — they are different modes (`ROUND_HALF_EVEN` is banker's). Half-up matches
what a brokerage statement does and what a human checking the arithmetic by hand expects. Where a
different mode is wanted it is passed explicitly and the reason is commented.

## 4.3 Multi-step computation

Quantizing at each step accumulates error. For a chain — weight × price × quantity × FX — carry
`Decimal` through and quantize **once**, at the boundary where a `Money` is returned:

```python
result = Decimal(base.amount_minor) * weight * rate      # Decimal throughout
return Money(int(result.quantize(Decimal("1"), ROUND_HALF_UP)), currency)
```

## 4.4 Zero has a currency

`Money.zero("USD") != Money.zero("CAD")`. There is no universal zero. This surprises people, and it
is correct: a zero USD balance and a zero CAD balance are different facts about the book, and
allowing them to compare equal would let a currency error hide behind an empty account.

---

# 5. ON-DISK REPRESENTATION

## CT-M.1 — Parquet: two columns

For a logical field `price`:

| Column | Type | Example |
|---|---|---|
| `price_minor` | `int64` | `41900` |
| `price_currency` | `string` | `"USD"` |

Two columns rather than a struct: filterable and groupable without unnesting, readable by any
parquet tool, and it matches the shape F4 already writes (`price` + `price_currency`).

**A `*_minor` column without its `*_currency` sibling is a schema violation** and must fail
validation in D-07, not be defaulted to base.

## CT-M.2 — JSON: an object

```json
{ "price": { "minor": 41900, "currency": "USD" } }
```

An object rather than two sibling keys, because JSON documents are read by humans and by the LLM
gateway, and a nested pair cannot be separated by a careless field selection.

## CT-M.3 — Converted values carry their rate

```json
{
  "nav_base": { "minor": 12500000, "currency": "CAD" },
  "fx_rate_used": { "pair": "USDCAD", "rate": "1.3742",
                    "as_of": "2026-08-14T20:00:00Z", "source": "FMP" }
}
```

Per **FX-2**. `rate` is a **string** in JSON to survive the round trip without becoming a float.

> **Migration note.** Legacy artifacts store `price: 419.00` + `price_currency: "USD"` as floats.
> Conversion to `*_minor` happens at the D-07 read boundary — the legacy files are not rewritten,
> and the reader is the single place a float becomes a `Money`.

---

# 6. ERROR CATALOG

All raise. None return a sentinel (**P5**).

| Error | Raised when |
|---|---|
| `CurrencyMismatchError` | `+`, `-`, ordering, ratio, or `sum_money` across currencies |
| `UnsupportedCurrencyError` | currency not in `SUPPORTED_CURRENCIES` |
| `InvalidAmountError` | amount unparseable, or not an `int` for `amount_minor` |
| `PrecisionLossError` | input has more fractional digits than the currency's exponent |
| `FxDirectionError` | `rate.from_currency != self.currency` |

Each carries both currencies (or both values) in its message — an error saying only "currency
mismatch" costs a debugging session that "cannot add USD to CAD" does not.

---

# 7. TESTING REQUIREMENTS

| Category | Cases |
|---|---|
| **Construction** | minor / decimal-string / float; unsupported currency; sub-cent input; negative; zero |
| **Exactness** | `0.1 + 0.2` equivalent is exact; `sum` of 100 × `0.01` is exactly `1.00`; `15.00 × 3 = 45.00` (the float trap: `150.99 × 3`) |
| **Mismatch** | every operator raises across currencies; `==` returns `False` and does **not** raise |
| **Rounding** | half-up at `.5` boundaries, both signs; explicit alternate modes; multi-step quantizes once |
| **FX** | correct direction; wrong direction raises; result currency correct; **rate absent ⇒ caller reports unavailable, never a guess** |
| **Round-trip** | `Money → parquet → Money` and `Money → JSON → Money` are identity for a range including negatives and zero |
| **Property** | `a + b - b == a`; `a + b == b + a`; `Money.zero(c) + a == a`; `hash` stable |

Tier: **unit** (constitution §4). Coverage target for this module: **100%** — it is 200 lines,
every domain depends on it, and a gap here is a gap everywhere.

---

# 8. ACCEPTANCE CRITERIA

```text
□ AC-M.1  Money(int, currency) constructs; a bare int is rejected by type checking
□ AC-M.2  Unsupported currency raises UnsupportedCurrencyError — never defaults to base
□ AC-M.3  from_decimal_str is exact for every 2-dp value; no float exists on the path
□ AC-M.4  Sub-cent input raises PrecisionLossError rather than rounding silently
□ AC-M.5  +, -, ordering and ratio raise CurrencyMismatchError across currencies
□ AC-M.6  == returns False across currencies and does not raise
□ AC-M.7  * int is exact; mul_rate rounds half-up and accepts an explicit mode
□ AC-M.8  Money.zero("USD") != Money.zero("CAD")
□ AC-M.9  convert() is the only currency-changing operation; wrong direction raises
□ AC-M.10 A converted value in any artifact is accompanied by the FxRate used (FX-2)
□ AC-M.11 With no FX rate, the dependent value is reported unavailable, not computed (FX-3)
□ AC-M.12 sum_money requires a currency; empty → zero in it; mixed → raises
□ AC-M.13 Parquet round-trip is identity, including negatives and zero
□ AC-M.14 A *_minor column with no *_currency sibling fails D-07 validation
□ AC-M.15 JSON round-trip is identity; rate serializes as a string
□ AC-M.16 Multi-step computation quantizes once, not per step
□ AC-M.17 Module has no imports from any other src/ domain
□ AC-M.18 Unit coverage is 100%
```

---

# 9A. ACCEPTANCE CRITERIA — migrated from `F4` on retirement

> ⚠ **`F4_data_plane/spec.md` was deleted 2026-08-18** (L0 §17.5a). **`AC-4.9` was live** — written
> 2026-08-18, 19 passing tests in `tests/test_money_exact.py` — so per **G-7** it migrates into the
> receiving L-spec rather than dying with its F-spec.
>
> ⚠ **Renumbered again 2026-08-23 — the first renumbering collided.** It landed on `AC-M.1`…`AC-M.3`,
> which §8 had already issued, so **three acceptance criteria carried two different meanings** — in
> the module every other domain depends on, and in the ACs an implementer reaches first. Now
> **`AC-M.19`…`AC-M.21`**, continuing §8's sequence rather than restarting it. *(Caught by
> `tools/sdd_audit.py`'s `duplicate acceptance criteria` check, added the same day because nothing
> was looking: `FAMILIES` covers rule prefixes, not AC ids.)*

```text
□ AC-M.19 ★ Money arithmetic is exact and unbiased. Every monetary quantity is
          carried in Decimal and quantized to the currency's minor unit with
          ROUND_HALF_UP; no monetary value is produced by binary floating-point
          multiplication or by the builtin round().  (MO-3, MO-4, MO-5)

          Rationale, kept because it is the evidence: two error sources compound —
          binary representation error in float(rate), and round() being BANKER'S
          rounding (ROUND_HALF_EVEN) where money requires ROUND_HALF_UP. The
          resulting cent errors were SYSTEMATICALLY DOWNWARD, so they do not
          cancel across many conversions the way symmetric noise would:
          1.00 x 1.365 returned 1.36 where money arithmetic gives 1.37.

□ AC-M.20 A same-currency ratio is dimensionless and leaves the Money type;
          a cross-currency ratio raises.  (MO-8, MO-9)

□ AC-M.21 Share quantity is an int — no fractional shares.  (MO-10)
```

**Traceability:** `AC-M.19` → `tests/test_money_exact.py` (19 tests, incl. an AST check that no
`portfolio/` module calls the builtin `round()`) → `pipeline/portfolio/money.py`, and in the
rewritten tree `src/shared/money.py`.

> ⚠ **The test currently exercises `pipeline/portfolio/money.py`, which is legacy.** It stays green
> until `pipeline/` is deleted at **B7**, then moves to `src/shared/money.py` with the AC.

---

# 9. OPEN QUESTIONS

| ID | Question | Recommendation |
|---|---|---|
| ~~**QM-1**~~ | ~~Does `Money` support `+` with `int` 0 for `sum()`?~~ | ✅ **CLOSED — no. Use `sum_money(items, currency)`** (Victor). ★ The explicit currency argument is the point: `sum()` over an **empty** iterable returns `0`, which has no currency and is exactly the untagged value **INV-001** forbids |
| ~~QM-2~~ | ~~Is `from_float` permitted?~~ | **DECIDED 2026-08-14 — kept.** FMP returns JSON floats; forbidding it moves the problem to every caller. Named to stay greppable |
| ~~**QM-3**~~ | ~~Does `Money` carry an optional `as_of`?~~ | ✅ **CLOSED — no** (Victor). An amount is not an observation; `as_of` belongs to the record that holds it (D-11 CT-11.4), and an optional field would be absent exactly when it mattered |
| ~~**QM-4**~~ | ~~Are share quantities typed (fractional shares)?~~ | ✅ **CLOSED — no fractional shares; quantity is `int`** (Victor). ★ See **MO-10** — this quantises position size and the consequence lands in D-06 |

---

# 10. CROSS-REFERENCES

| Document | Relevance |
|---|---|
| `L0-system-vision.md` INV-001 | The invariant this module implements |
| `L0-system-vision.md` M-5 | CAD base, explicit currency |
| `L4-coding-standards.md` §1.1 | Path, D-00 placement |
| `sdd/specs/constitution.md` INV-5 | Prior art — currency explicit, explicit FX step |
| `sdd/specs/F4_data_plane/spec.md` CT-4.1/4.2 | Prior art — `price_currency`, `fx_rate_used` *(retired 2026-08-20 — [L5 §6](L5-inherited-defects.md))* |
| `pipeline/portfolio/snapshot.py` | Prior art — FX-3, the `nav_base = None` behaviour |
