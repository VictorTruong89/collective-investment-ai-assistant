#!/usr/bin/env python
"""Consistency audit for the SDD design tier (``sdd/design/rel6_design/``).

WHY THIS EXISTS
---------------
The design tier is ~19 documents and ~13,000 lines, written by accretion across
many sessions. Accretion is deliberate — the retractions and reversals *are* the
evidence — but it has a cost: rules get deleted by a section rewrite, defined
twice with nothing saying which binds, or asserted against contract fields that
were never declared anywhere.

Every check below was added because it caught a REAL defect on 2026-08-18. The
docstrings name the defect, so this file doubles as a record of what goes wrong.

    python tools/sdd_audit.py          # exits 1 on any failure — CI-ready
    python tools/sdd_audit.py -v       # also list the checks that passed

This audits the DESIGN tier only. It governs no code, so it is not itself
spec-governed (constitution P1 applies to production features); it is a tool,
in the same family as ``tools/inspect_data.py``.

EXTENDING IT
------------
The highest-value check is :func:`check_contract_seams`, and it is table-driven:
add a row to ``SEAMS``. Six of the nine defects found on 2026-08-18 were seam
defects, and five of those were the SAME mistake — a consumer asserting a check
against a field the producer's contract never declared.

    Prose agreement between two specs is not a contract.

Natural next steps, in rough value order:
  * derive ``SEAMS`` from each spec's "Depends on:" header instead of hand-listing
  * check that every ``AC-n.k`` names a testing tier (constitution §4)
  * check that every ``formula_id`` cited has a MethodEntry (D-03 CT-3.3)
  * flag numbers that appear in two specs with different values (the δ = 1.92
    vs 2.19 defect, and the $20k vs $142.5k capital base)
"""

from __future__ import annotations

import collections
import glob
import os
import pathlib
import re
import sys

DESIGN_DIR = "sdd/design/rel6_design"
BLUEPRINT_DIR = "sdd/blueprints"

#: Rule-ID families in use. Extend when a spec introduces one (L0 §16.1, rule T-7).
FAMILIES = (
    "DE|FE|RA|MT|RK|PS|OR|RP|RC|DN|CB|CN|PD|EH|IM|MO|FX|QA|ST|CA|SI|GW|CF|LG|SC|BS|DOC"
)

#: Contract seams: (label, producer contract, consumer file, fields the consumer relies on).
#: A seam fails when the producer's contract does not declare a field the consumer needs,
#: or when the consumer never names the contract it reads.
SEAMS = [
    # `adj_as_of` added 2026-08-23: DE-30, AC-7.46 and FE-8 all assert against it
    # and CT-7.1 had never declared it. Same shape as the `adj_open_minor`
    # defect this row was created for, one field over — which is the argument
    # for widening an existing seam rather than trusting it stays fixed.
    ("D-07 price panel  -> D-02", "CT-7.1", "L1-feature-engineering.md",
     ["adj_open_minor", "adj_as_of"]),
    ("D-02 label set    -> D-04", "CT-2.3", "L1-model-training.md", ["decision_anchor"]),
    ("D-03 nomination   -> D-12", "CT-3.4", "L1-decision.md", ["ranked_quantity", "rank"]),
    ("D-08 run manifest -> D-04", "CT-8.1", "L1-model-training.md", ["decision_anchor"]),
    ("D-01 gate verdict -> D-12", "CT-1.4", "L1-decision.md", ["stability_fraction", "conviction"]),
    ("D-11 book state   -> D-05", "CT-11.4", "L1-risk-management.md", ["nav_base", "capital_base"]),
    ("D-11 book state   -> D-06", "CT-11.4", "L1-portfolio-strategy.md", ["capital_base"]),
    ("D-12 recommend.   -> D-09", "CT-12.1", "L1-reporting.md", ["thesis_ref", "alerts"]),
    ("D-12 vetoed cand. -> D-11", "CT-12.2", "L1-recording.md", ["binding_gates"]),
    ("D-00 llm call     -> D-01", "CT-0.1", "L1-fundamental-analysis.md", ["tokens_in", "temperature"]),
    # Added 2026-08-23 (B3). Each was a live seam defect at the time:
    #   report_id     — CT-2.2 stamps calendar_check_id; CT-7.7 declared no id at all
    #   alerts_status — RK-30/RK-36 make "unchecked" first-class; CT-12.1 could not say it
    #   stubs         — L3 BS-27 writes the stub into the manifest; CT-8.1 had no field
    ("D-07 calendar    -> D-02", "CT-7.7", "L1-feature-engineering.md", ["report_id"]),
    ("D-12 alerts      -> D-09", "CT-12.1", "L1-reporting.md", ["alerts_status"]),
    ("D-08 manifest    -> L3", "CT-8.1", "L1-orchestration.md", ["stubs"]),
    # Added 2026-08-23 (B4.1). CT-1.2 carried a FLAT `temperature` and no
    # `effort` — reintroducing, one contract downstream, the exact shape CT-0.1
    # was reshaped away from (GW-9). D-01 is deep-tier only, so `effort` was the
    # single control it had and the run record could not hold it.
    ("D-00 llm call     -> D-01 run", "CT-1.2", "L2-shared-infrastructure.md",
     ["decoding"]),
]


# --------------------------------------------------------------------------- #
# Loading
# --------------------------------------------------------------------------- #

def load():
    files = sorted(glob.glob(f"{DESIGN_DIR}/*.md"))
    if not files:
        sys.exit(f"no specs found under {DESIGN_DIR}/ — run from the repo root")
    return {os.path.basename(f): open(f, encoding="utf-8").read() for f in files}


def rule_definitions(text):
    """Rule IDs DEFINED in this text.

    DOC-1 (L4 §18): a rule is defined exactly once, in a **bold** ID cell. Every
    other appearance — §12 roll-ups, §10.1 grep tables — is an index row and is
    NOT bold. That convention is what makes "one binding definition" checkable
    rather than a reading exercise.
    """
    return re.findall(r"^\|\s*~*\*\*`?([A-Z]{2,4}-\d+[a-z]?)`?\*\*~*", text, re.M)


def contract_fields(text, contract):
    """Field names a contract declares — JSON, YAML, markdown table, or tuple form.

    All four styles are in use. The tuple form ``(a, b in {x,y}, c[])`` is the one
    that trips naive regexes; getting it wrong produces false failures, which is
    worse than no check at all. (The first version of this audit reported five
    phantom seam defects for exactly that reason.)
    """
    start = text.find(f"## {contract}")
    if start < 0:
        return None
    nxt = text.find("\n## ", start + 3)
    seg = text[start: nxt if nxt > 0 else start + 4000]

    out = set()
    for block in re.findall(r"```(?:json|yaml)(.*?)```", seg, re.S):
        out |= set(re.findall(r'"([a-z_0-9]+)"\s*:', block))            # JSON keys
        out |= set(re.findall(r"^\s{0,4}([a-z_0-9]+):", block, re.M))    # YAML keys
    out |= set(re.findall(r"^\|\s*.{0,3}`([a-z_0-9*.…]+)`", seg, re.M))  # markdown table rows
    for tup in re.findall(r"`\(([^)]+)\)`", seg, re.S):                  # tuple form
        for part in tup.split(","):
            # Strip decoration the specs use inside tuples: a leading star, a
            # trailing "[]" for list fields, "{}" for a struct field, and
            # "name: {...}" / "name in {...}" suffixes. Missing any of these
            # produced phantom failures on the first repo run of this script.
            # ⚠ "{}" added 2026-08-23: CT-1.2's `decoding{}` parsed as a field
            # named "decoding{}", so the seam reported the field undeclared when
            # the contract had just declared it — a FALSE failure, which is the
            # one outcome worse than no check (it teaches a reader to ignore it).
            stripped = part.strip(" `\n★*")
            name = stripped.split()[0] if stripped else ""
            name = name.rstrip("[]{}").rstrip(":")
            if re.fullmatch(r"[a-z_0-9]+", name):
                out.add(name)
    return out


# --------------------------------------------------------------------------- #
# Checks — each returns a list of failure strings
# --------------------------------------------------------------------------- #

def check_dangling_rules(docs):
    """A rule is cited but defined nowhere.

    Found: QA-27 was cited by FOUR specs as "the quantile stop/target the LLM may
    narrate but not alter" — and had never been written. Also QA-6, QA-26, RC-6/7.
    A rule that is referenced and undefined is worse than one that is wrong: it
    reads as authority nobody can check.
    """
    defined = set()
    for text in docs.values():
        defined |= set(rule_definitions(text))
        defined |= set(re.findall(r"\*\*([A-Z]{2,4}-\d+)\.\d+\*\*", text))  # sub-numbered prose
    fails = []
    for name, text in docs.items():
        missing = sorted({r for r in re.findall(rf"\b((?:{FAMILIES})-\d+)\b", text)} - defined)
        if missing:
            fails.append(f"{name}: cites undefined {missing}")
    return fails


def check_duplicate_definitions(docs):
    """A rule ID defined more than once with nothing saying which binds.

    Found: QA-87 defined THREE times; QA-77/79/80 twice each. A top-down reader
    met QA-79 as "downgraded", then "RE-PROMOTED", then "restored" — only the
    last bound, and the document did not say so. QA-116 is the fix: strike the
    superseded row, mark the live one "binding".
    """
    fails = []
    for name, text in docs.items():
        ids = re.findall(
            r"^\|\s*\*\*`?([A-Z]{2,4}-\d+[a-z]?)`?\*\*\s*(?:✅ \*binding\*\s*)?\|", text, re.M
        )
        dupes = {k: v for k, v in collections.Counter(ids).items() if v > 1}
        if dupes:
            fails.append(f"{name}: {dupes} — strike the superseded row or mark one binding")
    return fails


def check_supersession_pointers(docs):
    """A struck-through rule must say what replaced it (QA-116).

    Questions are exempt: a struck ``~~QQ-24~~ CLOSED`` is a different and correct
    convention — questions are *closed*, rules are *superseded*.
    """
    fails = []
    for name, text in docs.items():
        for line in text.splitlines():
            if (re.match(r"^\|\s*~~\*\*[A-Z]{2,4}-\d+", line)
                    and not re.match(r"^\|\s*~~\*\*Q", line)
                    and "SUPERSEDED" not in line and "→" not in line):
                fails.append(f"{name}: struck rule with no pointer — {line[:70]}")
    return fails


def check_parent_versions(docs):
    """Every spec claims the CURRENT L0 version as its parent.

    The claim means "reconciled against L0 at version X". Deliberately strict: it
    costs one sweep per L0 bump, and it is what caught D-12 being invisible to
    five specs that still claimed L0 v0.10.0 while D-12 had landed at v0.17.0.
    """
    l0 = re.search(r"^\| (\d+\.\d+\.\d+)\s*\|", docs["L0-system-vision.md"], re.M).group(1)
    fails = []
    for name, text in docs.items():
        m = re.search(r"L0-system-vision\.md\)\s*\*\*v(\d+\.\d+\.\d+)\*\*", text)
        if m and m.group(1) != l0:
            fails.append(f"{name}: claims parent v{m.group(1)}, L0 is v{l0}")
    return fails


def check_version_tables(docs):
    """Every spec carries a Document Control table. Without one, nothing is dated."""
    return [f"{n}: no version row" for n, t in docs.items()
            if not re.search(r"^\| \d+\.\d+\.\d+\s*\|", t, re.M)]


def check_contract_citations(docs):
    """A ``CT-n.k`` cited in the design tier resolves to a definition.

    F-spec contracts (e.g. "F4 CT-4.5") are external and exempt — they are
    qualified by their spec name at the citation site, which is exactly the
    convention L0 §16.4 requires for the D-nn/F-n ID collisions.
    """
    everything = "\n".join(docs.values())
    # ``~~`` allows a T-2 TOMBSTONE to count as defined. L0 T-2: "retire by
    # tombstone, never by deletion — a superseded ID keeps its row and says
    # where it went." Requiring a live heading would have forced deletion of
    # exactly the row T-2 exists to preserve. Found 2026-08-23 retiring CT-11.5.
    defined = set(re.findall(r"^## ~{0,2}(CT-[\dM]+\.\d+)", everything, re.M))
    cited = set(re.findall(r"\b(CT-\d+\.\d+)\b", everything))
    external = {c for c in cited if re.search(rf"F\d`?\s+{re.escape(c)}", everything)}
    missing = sorted(cited - defined - external)
    return [f"cited but undefined: {missing}"] if missing else []


def check_contract_seams(docs):
    """THE HIGHEST-VALUE CHECK — does the producer declare what the consumer relies on?

    Six of nine defects found on 2026-08-18 were here, and five were the same
    mistake:

      * ``adj_open`` — assigned to D-07 by THREE specs, appeared zero times in
        D-07's spec, and the whole open-anchored label change was blocked on a
        column no contract declared and no domain had been told to build.
      * ``decision_anchor`` — OR-35 says it lives in the RunManifest, MT-42 fails
        the run on a mismatch, DN-23 asserts the same. CT-8.1 never declared it,
        so the gate was unimplementable as contracted.
      * D-03 had NO contract for its daily nomination — the thing the pipeline
        exists to produce.
      * D-12's transported ``grade`` silently dropped ``k`` and
        ``verdict_distribution``, which RA-20 needs to render "BUY 3 / HOLD 2";
        a stability_fraction of 0.6 is equally 3/5 or 12/20.
      * D-05 and D-06 read "the book" in prose and named no contract at all.

    A consumer's assertion does not create the producer's field.
    """
    producers = {}
    for name, text in docs.items():
        for ct in re.findall(r"^## (CT-[\dM]+\.\d+)", text, re.M):
            producers[ct] = (name, contract_fields(text, ct))

    fails = []
    for label, contract, consumer, needed in SEAMS:
        if contract not in producers:
            fails.append(f"{label}: producer contract {contract} does not exist")
            continue
        declared = producers[contract][1] or set()
        absent = [f for f in needed if f not in declared]
        if absent:
            fails.append(f"{label}: {contract} does not declare {absent}")
        if consumer in docs and contract not in docs[consumer]:
            fails.append(f"{label}: {consumer} never names {contract}")
    return fails


def check_duplicate_acceptance_criteria(docs):
    """An AC id defined twice is two requirements wearing one name.

    Found 2026-08-23 in L2-shared-money.md: AC-M.1/2/3 are issued in section 8
    AND again in section 9A ("migrated from F4 on retirement", which renumbered
    into a collision). The first acceptance criteria anyone implements for
    Money were therefore ambiguous, and no check saw it — FAMILIES covers rule
    prefixes, not AC ids.
    """
    fails = []
    for name, text in docs.items():
        seen = collections.Counter(re.findall(r"^\s*(?:\u25a1|\|)?\s*(AC-[A-Z0-9]+\.\d+)\s",
                                              text, re.M))
        for ac, n in sorted(seen.items()):
            if n > 1:
                fails.append(f"{name}: {ac} defined {n} times")
    return fails


def check_orphans(docs):
    """A spec that nothing else references was written for nobody."""
    fails = []
    for name in docs:
        if name.startswith("L0"):
            continue
        stem = name[:-3]
        if not any(stem in docs[other] for other in docs if other != name):
            fails.append(f"{name}: referenced by no other spec")
    return fails


# ---------------------------------------------------------------------------
# Blueprint checks (sdd/blueprints/) — a different tier, a different question.
#
# The three checks below do NOT read ``docs``: they compare sdd/blueprints/
# against src/ and against git. They exist because a blueprint is the only
# record of WHY the code is shaped the way it is, and this project has twice
# shipped plausible-looking wrong arithmetic that no test caught
# (``_cumulative_fys`` at 41.5% error; D-19's enterprise-value-per-share).
#
# ALL THREE ARE NO-OPS UNTIL src/ HAS CODE. B0 has not run; a check that fails
# on day one is a check someone disables.
# ---------------------------------------------------------------------------


def _src_domains():
    """Directories under src/ that actually contain Python, from ownership.yaml.

    Derived rather than hard-coded: ownership.yaml is the authoritative binding
    of code path to spec (F3 CT-3.3), so a new domain is picked up for free.
    """
    own = "sdd/specs/ownership.yaml"
    if not os.path.isdir("src") or not os.path.exists(own):
        return []
    text = open(own, encoding="utf-8").read()
    dirs = sorted({m for m in re.findall(r'"src/([A-Za-z0-9_]+)/\*\*"', text)})
    return [d for d in dirs
            if any(_is_code(f) for f in glob.glob(f"src/{d}/**/*.py", recursive=True))]


def _is_code(path):
    """True when a .py file contains something beyond a module docstring.

    Refined 2026-08-23, on the first run against a real src/ tree: B0's skeleton
    is one docstring-only ``__init__.py`` per domain, and counting those made
    every domain "built" and demanded thirteen blueprints for thirteen empty
    packages. A package marker is scaffolding, not code — and BS-31's obligation
    attaches to a domain that has been BUILT.
    """
    import ast
    try:
        body = ast.parse(open(path, encoding="utf-8").read()).body
    except SyntaxError:
        return True                      # unparseable is a problem, not an exemption
    if not body:
        return False
    if len(body) == 1 and isinstance(body[0], ast.Expr) and \
            isinstance(getattr(body[0], "value", None), ast.Constant) and \
            isinstance(body[0].value.value, str):
        return False                     # docstring only
    return True


def _blueprints():
    return {os.path.basename(p): open(p, encoding="utf-8").read()
            for p in glob.glob(f"{BLUEPRINT_DIR}/D-*.md")}


def check_blueprint_existence(_docs):
    """Every domain with code under src/ has a blueprint (DR tier, README §4).

    A domain whose code exists but whose reasoning was never written down is
    the exact state the blueprint tier exists to prevent: correct-looking
    arithmetic with no record of why it is shaped that way.
    """
    bps = _blueprints()
    fails = []
    for d in _src_domains():
        if not any(f"src/{d}/" in text for text in bps.values()):
            fails.append(f"src/{d}/ has code but no blueprint names it")
    return fails


def check_blueprint_pointers(_docs):
    """Every ``file.py::symbol`` a blueprint cites actually exists (DR-2).

    DR-2 requires a pointer on every claim precisely so the document can be
    checked rather than trusted. An unresolvable pointer means the code moved
    and the reasoning did not follow it.

    The template and the tier README are skipped: their pointers are
    deliberately illustrative.
    """
    fails = []
    for name, text in _blueprints().items():
        for ref in re.findall(r"`([A-Za-z0-9_./-]+\.py)(?:::[A-Za-z0-9_.]+)?`", text):
            if not os.path.exists(ref):
                fails.append(f"{name}: pointer does not resolve — {ref}")
        for cfg in re.findall(r"`(config/[A-Za-z0-9_./-]+\.ya?ml)`", text):
            if not os.path.exists(cfg):
                fails.append(f"{name}: config file does not exist — {cfg}")
    return fails


def check_blueprint_freshness(_docs):
    """WARN when a domain's code was committed after its blueprint (DR-8).

    Deliberately a warning, not a failure: whether a commit was logic-bearing
    is a judgement, and a formatting change should not redden CI. The point is
    to make the drift visible at the moment it appears.
    """
    import subprocess

    def last_commit(path):
        try:
            out = subprocess.run(["git", "log", "-1", "--format=%ct", "--", path],
                                 capture_output=True, text=True, timeout=10)
            return int(out.stdout.strip()) if out.stdout.strip() else None
        except Exception:
            return None                      # not a repo, or git unavailable

    warns = []
    bps = _blueprints()
    for d in _src_domains():
        owner = next((n for n, t in bps.items() if f"src/{d}/" in t), None)
        if owner is None:
            continue                         # check_blueprint_existence owns that
        code_t = last_commit(f"src/{d}")
        bp_t = last_commit(f"{BLUEPRINT_DIR}/{owner}")
        if code_t and bp_t and code_t > bp_t:
            warns.append(f"{owner}: src/{d}/ changed after the blueprint — review DR-8")
    return warns


def check_domain_coverage(docs):
    """Every domain in L0's registry has an L1/L2 spec.

    D-10 Experiments is deliberately unspecified (L0 §4.2): its content is
    unknowable before the first end-to-end run, and ST-2's one-way import rule —
    no domain may import D-10 — is what makes leaving it unspecified safe.
    """
    registered = set(re.findall(r"^\|\s*\*\*(D-\d\d)\*\*\s*\|", docs["L0-system-vision.md"], re.M))
    owned = set()
    for text in docs.values():
        m = re.search(r"\*\*Domain:\*\*\s*(D-\d\d)", text)
        if m:
            owned.add(m.group(1))
    missing = sorted(registered - owned - {"D-10"})
    return [f"registered but unspecified: {missing}"] if missing else []


_TOMBSTONE = re.compile(r"deleted|retired|tombstone|supersed|no longer exists"
                        r"|DELETED|RETIRED", re.I)


def check_spec_pointers(docs):
    """★ Every `sdd/**` path a LIVE document cites still exists (G-7, ST-8).

    ⚠ **This check exists because F0 was deleted and nothing noticed.**
    `sdd/specs/F0_code_map/spec.md` was removed on 2026-08-20 and **26 files
    went on pointing at it** — including two blueprints and `L1-reporting.md`
    — while every other check stayed green. ★ **G-7's whole point is that a
    retired spec's content must land somewhere first**, and a dangling pointer
    is the evidence that it did not.

    `sdd/archive/**` is skipped: it is frozen pre-SDD history and its pointers
    are deliberately historical (`sdd/README.md`).
    """
    fails = []
    roots = [pathlib.Path(DESIGN_DIR), pathlib.Path("sdd/blueprints"),
             pathlib.Path("sdd/specs")]
    files = [f for root in roots if root.exists()
             for f in sorted(root.rglob("*.md"))]
    files += [pathlib.Path("CLAUDE.md")]
    for f in files:
        if not f.exists() or "_templates" in str(f):
            continue
        text = f.read_text(encoding="utf-8")
        for line in text.splitlines():
            marked = _TOMBSTONE.search(line)
            for ref in set(re.findall(r"`(sdd/[A-Za-z0-9_./-]+\.(?:md|ya?ml))`", line)):
                if ref.startswith("sdd/archive/") or os.path.exists(ref):
                    continue
                if marked:
                    # ★ A citation that SAYS the target is gone is a tombstone
                    #   (T-2), not a broken pointer. The defect this check
                    #   exists for is the silent one.
                    continue
                fails.append(f"{f.name}: spec pointer does not resolve — {ref}")
    return fails


CHECKS = [
    ("dangling rule references", check_dangling_rules),
    ("duplicate rule definitions", check_duplicate_definitions),
    ("supersession pointers", check_supersession_pointers),
    ("parent version claims", check_parent_versions),
    ("version tables present", check_version_tables),
    ("contract citations resolve", check_contract_citations),
    ("contract seams  <-- highest value", check_contract_seams),
    ("duplicate acceptance criteria", check_duplicate_acceptance_criteria),
    ("orphan specs", check_orphans),
    ("domain coverage", check_domain_coverage),
    ("blueprint exists per built domain", check_blueprint_existence),
    ("blueprint pointers resolve", check_blueprint_pointers),
    ("spec pointers resolve", check_spec_pointers, "warn"),
    ("blueprint freshness", check_blueprint_freshness, "warn"),
]


def main():
    verbose = "-v" in sys.argv
    docs = load()
    print(f"SDD audit — {len(docs)} specs under {DESIGN_DIR}/\n")

    total = warned = 0
    for entry in CHECKS:
        label, fn = entry[0], entry[1]
        severity = entry[2] if len(entry) > 2 else "fail"
        found = fn(docs)
        if found and severity == "warn":
            warned += len(found)
            print(f"  WARN  {label}")
        elif found:
            total += len(found)
            print(f"  FAIL  {label}")
        elif verbose:
            print(f"  pass  {label}")
        for f in found:
            print(f"          {f}")

    print()
    if total:
        print(f"FAILED — {total} finding(s)" + (f", {warned} warning(s)" if warned else ""))
        return 1
    if warned:
        print(f"ALL CLEAN — {len(CHECKS)} checks over {len(docs)} specs "
              f"({warned} warning(s), not blocking)")
        return 0
    print(f"ALL CLEAN — {len(CHECKS)} checks over {len(docs)} specs")
    return 0


if __name__ == "__main__":
    sys.exit(main())
