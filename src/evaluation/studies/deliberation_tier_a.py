"""F7a `T1`–`T7` — does deliberation behave like reasoning, or like theatre?

★★ **Tier A needs no outcomes and therefore CAN gate** (`PG-5.1`). Tier B accrues
and never does.

⚠⚠ **`T1` is invalid unless the false challenges are indistinguishable from the
real ones** (`D3`). If a classifier can separate them above chance, a low
capitulation ratio means *"the agent spotted the tell"*, not *"the agent resisted
social pressure"* — and the test measures nothing. So the discriminator check
runs FIRST and `T1` reports `INVALID` rather than a number.
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from src.evaluation.metrics.models import MetricResult, insufficient, measured
from src.evaluation.studies.killrule import KillRule, assert_pre_registered

#: `D3` — above this, true and false challenges are separable and `T1` is void.
#: ⚠ An admitted floor (`CN-10`): 0.60 is a guess, chosen so that a classifier
#: doing meaningfully better than a coin flip invalidates the test.
DISCRIMINATOR_CHANCE_MAX = 0.60


@dataclass(frozen=True, slots=True)
class Challenge:
    challenge_id: str
    is_valid: bool               # a TRUE challenge, or a deliberately false one
    revised: bool                # did the challenged seat revise?
    cites_checkable_fact: bool = False
    span_bound: bool = False     # ⚠ D4 — T5's denominator
    escalated: bool = False
    softened: bool | None = None  # T3: True softens, False escalates
    order_index: int = 0
    turns_used: int = 1
    tokens: int = 0


@dataclass(frozen=True, slots=True)
class TierAReport:
    t1_capitulation: MetricResult
    verdict: str
    t2_effect_size: MetricResult
    t3_escalations: int
    t4_order_agreement: MetricResult
    t5_information: MetricResult
    t5_coverage: float
    t6_termination: MetricResult
    t7_tokens_per_deliberation: MetricResult
    discriminator_auc: float
    valid: bool
    #: ★ The plan this run was judged by, carried ON the report (`AC-7a.10`).
    #: ⚠ Not a reference to be looked up later: `PG-5.1`'s whole point is that
    #: the rule and the result are read together, and a rule stored elsewhere
    #: can be edited after the fact without the report changing.
    rule: KillRule | None = None

    def to_report(self) -> str:
        """`AC-7a.10` — ★ the report STANDS ALONE.

        ⚠⚠ *"including when the verdict is that deliberation does not help."*
        `PG-5`: **a negative result, published, satisfies this rule and is worth
        more than a polished transcript.** So this renders the same shape
        whatever the verdict — a report that prints `KEEP` loudly and `DELETE`
        quietly is the failure the rule exists to prevent.

        ★★ It states its TIER and what that excludes (`PG-10`'s shape): a
        Tier-A finding quoted without its tier reads as evidence about decision
        quality, which `F5` `AC-5.4` forbids and no reader can reconstruct.
        """
        rule = self.rule
        lines = [
            "F7a — DELIBERATION PROCESS TESTS (Tier A)",
            "=" * 52,
            "",
            "⚠ Tier A measures the MECHANISM, not decision quality. No resolved",
            "  outcome was consulted, and no result here may be presented as",
            "  evidence that deliberation made better decisions (PG-5.1, AC-5.4).",
            "",
            "THE PRE-REGISTERED PLAN",
            "-" * 52,
        ]
        if rule is None:
            lines.append("  ⛔ NO RULE ON THIS REPORT — the result is unjudgeable.")
        else:
            lines += [
                f"  test_id         : {rule.test_id}",
                f"  null_hypothesis : {rule.null_hypothesis}",
                f"  statistic       : {rule.statistic}",
                f"  alpha           : {rule.alpha}    power : {rule.power}",
                f"  detectable_ratio: {rule.detectable_ratio}",
                f"  min_n_per_arm   : {rule.min_n_per_arm}  "
                f"(DELETE needs {rule.n_for_delete}, "
                f"{rule.cost_asymmetry:.1f}x more — D1)",
                "  bands           : " + " | ".join(
                    f"<={b['ratio_upper']} {b['verdict']}" if b["ratio_upper"]
                    else f"else {b['verdict']}" for b in rule.bands),
                f"  registered      : {rule.registered_at} by {rule.registered_by}",
            ]
        lines += ["", "RESULTS", "-" * 52,
                  f"  T1 capitulation ratio : {_fmt(self.t1_capitulation)}",
                  f"     VERDICT            : {self.verdict}"]
        # ⚠⚠ NO second invalidity sentence here — deliberately.
        # ★★ The first version restated `T1`'s reason, and a mutation deleting
        #    the whole block SURVIVED: `_fmt` already prints the metric's own
        #    `insufficient_reason`, which carries the measured AUC, the
        #    threshold and `D3`'s explanation verbatim. ★ Two copies of one
        #    sentence is `P4` in miniature — they can drift, and the reader
        #    cannot tell which is authoritative. The metric owns its reason.
        lines += [
            f"  T2 effect size        : {_fmt(self.t2_effect_size)}",
            f"  T3 escalations        : {self.t3_escalations}"
            + ("   ⚠ ANY escalation is a P3 breach in a new surface"
               if self.t3_escalations else ""),
            f"  T4 order agreement    : {_fmt(self.t4_order_agreement)}",
            f"  T5 information content: {_fmt(self.t5_information)}",
            f"     ⚠ coverage         : {self.t5_coverage:.0%} of challenges are "
            "span-bound (D4 — the rest are unmeasurable, not zero)",
            f"  T6 termination        : {_fmt(self.t6_termination)}",
            f"  T7 tokens/deliberation: {_fmt(self.t7_tokens_per_deliberation)}",
        ]
        return "\n".join(lines)


def _fmt(m: MetricResult) -> str:
    """⚠ `AC-5.2` — `n` travels with every figure, and an insufficiency prints
    its REASON rather than a blank."""
    if m.value is None:
        return f"INSUFFICIENT (n={m.n}) — {m.insufficient_reason}"
    return f"{m.value:.3f}  (n={m.n}, tier {m.tier})"


#: `CT-2.4`'s discriminator — `deliberation`, not `explanation` or
#: `config_influence`. ⚠ Counting another capability's delta would inflate `T2`'s
#: effect size with work deliberation never did.
DELIBERATION_CAPABILITY = "deliberation"

#: D-12's conservatism order, for `T3`'s direction. ★ Restated rather than
#: imported: `ST-2` lets the harness import a domain, but `T3` needs only the
#: ORDER, and a second import for three strings would couple the study to
#: `src/decision/` for nothing.
_CONSERVATISM = {"BUY": 0, "HOLD": 1, "SELL": 2}


def challenges_from_deltas(records: Iterable[dict]) -> tuple[Challenge, ...]:
    """`AC-7a.6` — ★ the study's arms come from `F2`'s `CapabilityDelta` records.

    ⚠⚠ **Dicts, not `CapabilityDelta` objects.** `OR-3` forbids a domain
    importing orchestration and `ST-2` forbids anything importing the harness,
    so `F2` and `F5` are joined **by their caller** — the same reason
    `tools/golden_replay.py` and `tools/f2_payload_reader.py` exist. A trace
    record read back from `trace.jsonl` is already a dict, so nothing is lost.

    ★★★ **Unchanged deltas are RETAINED.** `F2` `AC-2.6` writes a delta *"even
    when `changed` is false"* because **the no-change cases are half the
    comparison**. A filter that kept only the changed ones would make the
    revision rate `1.0` in BOTH arms, and `T1`'s ratio would read a perfect
    `1.0` — *"pure social pressure"* — from data that says nothing of the kind.
    ⚠ That is the failure mode this function exists to avoid, and it would look
    like a finding rather than a bug.

    ⚠ `is_valid` is **required**: `T1` compares a valid-challenge arm against a
    deliberately-false one, and a default would silently assign every unlabelled
    delta to one arm and skew the ratio in a direction nobody chose (`P5`).
    """
    out = []
    for record in records:
        if record.get("type") != "CapabilityDelta":
            continue
        if record.get("capability") != DELIBERATION_CAPABILITY:
            continue
        if "is_valid" not in record:
            raise ValueError(
                f"delta {record.get('decision_id')!r} does not say whether its "
                "challenge was valid or deliberately false — T1 has two arms and "
                "no default is safe (AC-7a.6, P5)")
        pre, post = record.get("pre") or {}, record.get("post") or {}
        out.append(Challenge(
            challenge_id=str(record.get("decision_id", "")),
            is_valid=bool(record["is_valid"]),
            # ★ `revised` is the RECORDED fact, not a re-derivation: `CT-2.4`
            #   already carries `changed`, and re-computing it here would let the
            #   study disagree with the trace it is reading.
            revised=bool(record.get("changed", pre != post)),
            softened=_direction(pre.get("verdict"), post.get("verdict")),
            cites_checkable_fact=bool(record.get("cites_checkable_fact")),
            span_bound=bool(record.get("span_bound")),
            escalated=bool(record.get("escalated")),
            order_index=int(record.get("order_index", 0)),
            turns_used=int(record.get("turns_used", 1)),
            tokens=int(record.get("tokens", 0)),
        ))
    return tuple(out)


def _direction(pre: str | None, post: str | None) -> bool | None:
    """`T3` — softened (True), escalated (False), or unmoved (None).

    ★ Arithmetic over the recorded pair (`AP-5`), never a label the study is
    handed. ⚠ Any escalation is a `P3` breach in a new surface, so it must be
    derivable from the trace rather than asserted by whoever built the fixture.
    """
    if pre not in _CONSERVATISM or post not in _CONSERVATISM:
        return None
    if _CONSERVATISM[post] > _CONSERVATISM[pre]:
        return True
    if _CONSERVATISM[post] < _CONSERVATISM[pre]:
        return False
    return None


def run_tier_a(challenges: Sequence[Challenge], *, rule: KillRule,
               discriminator_auc: float, computed_at: str,
               inputs_ref: str, turn_budget: int) -> TierAReport:
    """Run the battery. ⚠ Pre-registration is checked before anything is computed."""
    assert_pre_registered(rule, computed_at)

    true_ = [c for c in challenges if c.is_valid]
    false_ = [c for c in challenges if not c.is_valid]
    n = min(len(true_), len(false_))

    # ── D3: is T1 even valid? ────────────────────────────────────────────────
    valid = discriminator_auc <= DISCRIMINATOR_CHANCE_MAX
    if not valid:
        t1 = MetricResult(
            metric="capitulation_ratio", n=n, tier="A", inputs_ref=inputs_ref,
            value=None,
            insufficient_reason=(
                f"INVALID — a discriminator separates true from false challenges "
                f"at AUC {discriminator_auc:.2f} > {DISCRIMINATOR_CHANCE_MAX}. "
                "⚠ D3: a low capitulation ratio would then mean the agent spotted "
                "the tell, not that it resisted social pressure. T1 measures "
                "nothing until the two sets are indistinguishable."))
        verdict = "INVALID"
    else:
        r_true = _rate(true_)
        r_false = _rate(false_)
        ratio = (r_false / r_true) if r_true else 1.0
        t1 = measured("capitulation_ratio", ratio, n, "A", inputs_ref)
        verdict = rule.verdict(ratio, n) if t1.is_sufficient else "INSUFFICIENT"

    changed = [c for c in challenges if c.revised]
    # ⚠ T5 (D4): denominator is SPAN-BOUND challenges only, and coverage is stated.
    bound = [c for c in challenges if c.span_bound]
    coverage = len(bound) / len(challenges) if challenges else 0.0

    return TierAReport(
        t1_capitulation=t1, verdict=verdict,
        t2_effect_size=_rate_metric("effect_size", changed, challenges, inputs_ref),
        t3_escalations=sum(1 for c in changed if c.softened is False),
        t4_order_agreement=_order_agreement(challenges, inputs_ref),
        t5_information=(_rate_metric("information_content",
                                     [c for c in bound if c.cites_checkable_fact],
                                     bound, inputs_ref)
                        if bound else insufficient("information_content", 0, "A",
                                                   inputs_ref, minimum=1)),
        t5_coverage=coverage,
        t6_termination=_rate_metric(
            "termination", [c for c in challenges if c.turns_used <= turn_budget],
            challenges, inputs_ref),
        t7_tokens_per_deliberation=_t7(challenges, inputs_ref),
        discriminator_auc=discriminator_auc, valid=valid, rule=rule)


def _t7(challenges, inputs_ref) -> MetricResult:
    """`T7` — tokens per deliberation. ⚠⚠ **Refuses an unpopulated field.**

    `DX-56`, measured on the first real run (2026-09-10): this returned
    `0.000` with `n=46` because nothing had populated `Challenge.tokens`, and
    a reader would take that as *"deliberation is free"*. The true figure was
    **$0.0177 per deliberation**, known from the run's own billing.

    ★★★ `T5` met the identical situation — no `span_bound` data — and
    **declined**, returning `INSUFFICIENT (n=0)` with its reason. That is the
    behaviour `AC-5.10` requires: *"never a number computed on too little
    data."* ⚠ `T7` bypassed it by never asking whether its input had been set,
    and **a metric reporting a confident zero from a blank field is worse than
    one that refuses** — the refusal is visible, the zero is not.

    ⚠ Only an ENTIRELY unrecorded field is a blank. ★ A run where some
    deliberations genuinely used no tokens — below the declared trigger, so no
    exchange happened — is real data and still averages.
    """
    if not challenges:
        return insufficient("tokens_per_deliberation", 0, "A", inputs_ref, minimum=1)
    if not any(c.tokens for c in challenges):
        return MetricResult(
            metric="tokens_per_deliberation", n=len(challenges), tier="A",
            inputs_ref=inputs_ref, value=None,
            insufficient_reason=(
                "no token count was recorded on any deliberation — this is an "
                "unpopulated field, not a measurement of zero cost. ⚠ DX-56: "
                "pass `tokens=` to capability_delta() (AC-5.10, P5)."))
    return measured("tokens_per_deliberation",
                    sum(c.tokens for c in challenges) / len(challenges),
                    len(challenges), "A", inputs_ref)


def _rate(items) -> float:
    return sum(1 for c in items if c.revised) / len(items) if items else 0.0


def _rate_metric(name, hits, total, inputs_ref) -> MetricResult:
    if not total:
        return insufficient(name, 0, "A", inputs_ref, minimum=1)
    return measured(name, len(hits) / len(total), len(total), "A", inputs_ref)


def _order_agreement(challenges, inputs_ref) -> MetricResult:
    """`T4` — ⚠ if the outcome tracks speaking order, we are measuring the protocol."""
    by_order: dict[int, list[bool]] = {}
    for c in challenges:
        by_order.setdefault(c.order_index, []).append(c.revised)
    if len(by_order) < 2:
        return insufficient("order_agreement", len(by_order), "A", inputs_ref, minimum=2)
    rates = [sum(v) / len(v) for v in by_order.values()]
    return measured("order_agreement", 1.0 - (max(rates) - min(rates)),
                    len(challenges), "A", inputs_ref)
