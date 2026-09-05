"""Delivery — the email body is a NOTIFICATION, not the artifact (RP-35, RP-21…RP-24).

★ **RP-35.** The body carries the headline and points at the attachment.
*Decision-relevant content that exists only in the email body is content trapped
in the most constrained medium.*

⚠ **RP-23: a delivery failure is LOUD.** An email that did not send is not a
quiet log line — the whole point of P6 is that the artifact reaches the human,
and a silent failure is indistinguishable from a run that never happened.
"""

from __future__ import annotations

import hashlib
import smtplib
from dataclasses import dataclass
from datetime import datetime, timezone
from email.message import EmailMessage
from pathlib import Path

from src.reporting.errors import ArchiveMismatchError, DeliveryFailedError
from src.shared.secrets import Secret

#: Gmail's submission endpoint. A WORLD FACT with its check date (CN-2).
SMTP_HOST, SMTP_PORT = "smtp.gmail.com", 587      # checked 2026-08-23


@dataclass(frozen=True, slots=True)
class Delivery:
    """CT-9.3 — the delivery record. Append-only, and idempotent by digest."""

    delivery_id: str
    channel: str
    sent_at: datetime
    recipient_hash: str
    artifact_digests: dict
    archive_paths: dict
    outcome: str

    def to_json_obj(self) -> dict:
        return {"delivery_id": self.delivery_id, "channel": self.channel,
                "sent_at": self.sent_at.isoformat(),
                "recipient_hash": self.recipient_hash,
                "artifact_digests": dict(self.artifact_digests),
                "archive_paths": {k: str(v) for k, v in self.archive_paths.items()},
                "outcome": self.outcome}


def digest(payload: bytes) -> str:
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def delivery_id(card, renderings: dict) -> str:
    """Stable across re-sends of identical content — RP-22's idempotence.

    ⚠ A re-send must be *identifiable as one*: a silent duplicate is how a stale
    card gets acted on twice. Deriving the id from the content makes the
    duplicate visible instead of invisible.
    """
    material = "|".join([card.ticker, card.as_of.isoformat(),
                         *(digest(v) for _, v in sorted(renderings.items()))])
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def archive(renderings: dict, root: str | Path, delivery: str) -> dict:
    """RP-24 — archived bytes == delivered bytes, per rendering.

    Written BEFORE the send and verified after, so the archive is evidence of
    what was delivered rather than a second rendering that happens to match.
    """
    root = Path(root) / delivery
    root.mkdir(parents=True, exist_ok=True)
    out = {}
    for name, payload in sorted(renderings.items()):
        path = root / name
        path.write_bytes(payload)
        if path.read_bytes() != payload:
            raise ArchiveMismatchError(
                f"archived bytes for {name} differ from the delivered bytes. If they "
                f"can differ, the archive is not evidence of what was seen (RP-24)"
            )
        out[name] = path
    return out


def build_message(card, renderings: dict, *, sender: str, recipient: str) -> EmailMessage:
    """The notification body plus the artifact attachments (RP-35)."""
    msg = EmailMessage()
    status = "NOT ACTIONABLE" if not card.actionable else "ACTIONABLE"
    msg["Subject"] = f"[{status}] {card.ticker} discipline card — {card.as_of.isoformat()}"
    msg["From"] = sender
    msg["To"] = recipient
    verdict = card.field("verdict")
    body = [
        f"{card.ticker} — discipline card, as of {card.as_of.isoformat()}",
        "",
        f"Verdict: {verdict.value}   [{verdict.marker}, source {verdict.source}]",
        "",
    ]
    if not card.actionable:
        body += [f"⚠ NOT ACTIONABLE — {card.not_actionable_reason}", ""]
    body += [
        f"Risk status: {card.alerts_status}",
        "",
        "The artifact of record is the attached HTML. The markdown attachment is",
        "the diffable, permanent copy (RP-33). This body is a notification only.",
    ]
    msg.set_content("\n".join(body))
    for name, payload in sorted(renderings.items()):
        subtype = "html" if name.endswith(".html") else "markdown"
        msg.add_attachment(payload, maintype="text", subtype=subtype, filename=name)
    return msg


def send(message: EmailMessage, *, user: Secret, password: Secret,
         transport=None) -> str:
    """Send it, or raise loudly (RP-23).

    `transport` is injected so every test is hermetic; production passes `None`
    and gets real SMTP. ⚠ **The password is a `Secret`** — DE-8's rule applies
    here for the same reason it applies to an API key, and the wrapper's
    `__repr__` is what keeps it out of the traceback.
    """
    if not isinstance(password, Secret) or not isinstance(user, Secret):
        raise TypeError(
            "SMTP credentials must be Secret-wrapped, so a failed send cannot put "
            "them in an exception message"
        )
    try:
        if transport is not None:
            transport.send_message(message)
        else:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
                smtp.starttls()
                smtp.login(user.reveal(), password.reveal())
                smtp.send_message(message)
    except Exception as exc:
        raise DeliveryFailedError(
            f"delivery to {message['To']} failed: {type(exc).__name__}: {exc}. A "
            f"failed send is loud — an email that did not arrive is indistinguishable "
            f"from a run that never happened (RP-23, OR-19)"
        ) from exc
    return message["To"]


def deliver(card, renderings: dict, *, sender: str, recipient: str,
            user: Secret, password: Secret, archive_root: str | Path,
            transport=None) -> Delivery:
    """Archive, send, record. In that order — the archive is written first (RP-24)."""
    did = delivery_id(card, renderings)
    paths = archive(renderings, archive_root, did)
    message = build_message(card, renderings, sender=sender, recipient=recipient)
    send(message, user=user, password=password, transport=transport)
    return Delivery(
        delivery_id=did, channel="email", sent_at=datetime.now(timezone.utc),
        recipient_hash=hashlib.sha256(recipient.encode()).hexdigest()[:16],
        artifact_digests={n: digest(p) for n, p in sorted(renderings.items())},
        archive_paths=paths, outcome="SENT",
    )
