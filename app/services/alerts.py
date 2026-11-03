"""Guardian alerts through a Zapier webhook (a "Catch Hook" trigger in a Zap).

When a payment is held, or a hold expires unanswered, we POST a flat JSON summary to
ZAPIER_HOOK_URL; the Zap turns it into an email, SMS or chat message for the guardian.
Sending runs in a background thread so a slow or failing webhook never delays a payment.
Without ZAPIER_HOOK_URL, alerts are only logged.
"""

import logging
import threading

import httpx

from app.config import BASE_URL, ZAPIER_HOOK_URL
from app.models import Payment

log = logging.getLogger("guardrail.alerts")

ENABLED = ZAPIER_HOOK_URL.startswith("https://")

HEADLINES = {
    "payment_held": "{sender} is trying to send {amount} to {recipient}. Shield says {risk} risk.",
    "hold_expired": "No one answered in time, so {sender}'s {amount} payment to {recipient} was cancelled.",
}


def build_alert(payment: Payment, event: str) -> dict:
    """Flat fields only, so each one maps straight onto a Zap step."""
    amount = f"${payment.amount:,.2f} {payment.currency}"
    risk = payment.risk
    return {
        "event": event,
        "headline": HEADLINES[event].format(sender=payment.sender, amount=amount,
                                            recipient=payment.recipient_name,
                                            risk=risk.risk_level if risk else "unknown"),
        "payment_id": payment.id,
        "sender": payment.sender,
        "recipient": payment.recipient_name,
        "recipient_is_new": payment.recipient_is_new,
        "amount": amount,
        "note": payment.note,
        "risk_level": risk.risk_level if risk else "",
        "verdict": risk.verdict if risk else "",
        "reason": risk.reason if risk else "",
        "signals": "\n".join(f"- {s}" for s in risk.signals) if risk else "",
        "review_url": f"{BASE_URL}/guardian.html",
        "created_at": payment.created_at.isoformat(timespec="seconds"),
    }


def notify_guardian(payment: Payment, event: str) -> None:
    alert = build_alert(payment, event)
    if not ENABLED:
        log.info("Guardian alert (no ZAPIER_HOOK_URL, not sent): %s", alert["headline"])
        return
    threading.Thread(target=_post, args=(alert,), daemon=True).start()


def _post(alert: dict) -> None:
    try:
        res = httpx.post(ZAPIER_HOOK_URL, json=alert, timeout=10)
        res.raise_for_status()
        log.info("Guardian alert sent to Zapier (%s %s)", alert["event"], alert["payment_id"])
    except httpx.HTTPError as err:
        log.warning("Guardian alert to Zapier failed (%s %s): %s", alert["event"], alert["payment_id"], err)
