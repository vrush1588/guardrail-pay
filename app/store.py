"""In-memory store. Everything resets when the server restarts — no database."""

from datetime import datetime, timedelta

from app.models import Actor, AuditEntry, GuardianRules, Payment, utcnow

payments: dict[str, Payment] = {}
audit_log: list[AuditEntry] = []

guardian_rules = GuardianRules()

# Payees this family has paid before. Anything else counts as a new recipient.
KNOWN_RECIPIENTS = ("School Cafe", "GameWorld Store", "City Pharmacy", "Alex (grandson)")

# Each sender's usual payment size, so Shield can spot "much bigger than normal".
USUAL_AMOUNT = {"Grandma Rose": 40.0, "Leo (age 12)": 10.0}

# When each recipient was first paid (lower-cased name -> time). Drives the cooling-off rule.
recipient_first_seen: dict[str, datetime] = {}


def _known_since() -> dict[str, datetime]:
    long_ago = utcnow() - timedelta(days=365)
    return {name.lower(): long_ago for name in KNOWN_RECIPIENTS}


recipient_first_seen.update(_known_since())


def is_new_recipient(name: str) -> bool:
    return name.strip().lower() not in recipient_first_seen


def first_seen(name: str, at: datetime) -> datetime:
    """When this recipient was first paid; records `at` if this is the first time."""
    return recipient_first_seen.setdefault(name.strip().lower(), at)


def usual_amount(sender: str) -> float | None:
    return USUAL_AMOUNT.get(sender)


def save(payment: Payment) -> Payment:
    payments[payment.id] = payment
    return payment


def get(payment_id: str) -> Payment | None:
    return payments.get(payment_id)


def list_all() -> list[Payment]:
    return sorted(payments.values(), key=lambda p: p.created_at, reverse=True)


def audit(actor: Actor, action: str, payment_id: str, detail: str = "") -> None:
    audit_log.append(AuditEntry(actor=actor, action=action, payment_id=payment_id, detail=detail))


def reset() -> None:
    payments.clear()
    audit_log.clear()
    recipient_first_seen.clear()
    recipient_first_seen.update(_known_since())
