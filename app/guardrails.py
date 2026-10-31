"""The stricter-only rule.

Shield (the AI) gives a risk level. The guardian's rules give their own verdict. The
final verdict is whichever is STRICTER. Rules can tighten what Shield says, never
loosen it; Shield can never approve a payment the rules would hold or block; and if
Shield fails, the payment is held for manual review.
"""

from datetime import datetime

from app.models import GuardianRules, Payment, Risk, ShieldResult, utcnow

STRICTNESS = {"allow": 0, "hold": 1, "block": 2}

# How Shield's risk level maps to a verdict before the rules have their say.
SHIELD_VERDICT = {"low": "allow", "medium": "hold", "high": "block"}

RULE_PREFIX = "Family rule:"


def stricter(a: str, b: str) -> str:
    return a if STRICTNESS[a] >= STRICTNESS[b] else b


def rules_verdict(payment: Payment, rules: GuardianRules, first_seen: datetime,
                  now: datetime) -> tuple[str, list[str]]:
    """What the guardian's rules alone say about this payment."""
    verdict, signals = "allow", []

    def hold(why: str) -> None:
        nonlocal verdict
        verdict = stricter(verdict, "hold")
        signals.append(f"{RULE_PREFIX} {why}")

    if rules.paused:
        hold("all payments are paused by a guardian.")
    if payment.amount > rules.max_amount:
        hold(f"payments over ${rules.max_amount:,.0f} need a guardian.")
    if payment.recipient_is_new and not rules.allow_new_recipients:
        hold("new recipients need a guardian.")
    else:
        minutes_known = (now - first_seen).total_seconds() / 60
        if minutes_known < rules.cooling_off_minutes:
            hold(f"{payment.recipient_name} was added less than {rules.cooling_off_minutes} minutes ago.")
    return verdict, signals


def apply_guardrails(payment: Payment, ai_verdict: ShieldResult | None, rules: GuardianRules,
                     first_seen: datetime, now: datetime | None = None) -> Risk:
    """Combine Shield's verdict with the guardian's rules. Can only get stricter.

    ai_verdict is None when Shield failed; that holds the payment for manual review.
    """
    if ai_verdict is None:
        ai_verdict = ShieldResult(
            risk_level="medium",
            signals=["Shield could not check this payment."],
            reason="We could not check this payment, so a family member needs to review it.",
        )
        shield_verdict = "hold"
    else:
        # Fail closed: a level we don't recognise is treated as a block.
        shield_verdict = SHIELD_VERDICT.get(ai_verdict.risk_level, "block")

    rule_verdict, rule_signals = rules_verdict(payment, rules, first_seen, now or utcnow())
    final = stricter(shield_verdict, rule_verdict)

    signals = list(ai_verdict.signals) + rule_signals
    reason = ai_verdict.reason
    risk_level = ai_verdict.risk_level
    if STRICTNESS[final] > STRICTNESS[shield_verdict]:
        # The rules overruled Shield; explain with the rule, not Shield's "looks fine".
        reason = rule_signals[0].removeprefix(RULE_PREFIX).strip().capitalize()
        risk_level = "medium" if risk_level == "low" else risk_level

    # Not `assert`: this check must survive `python -O`.
    if STRICTNESS[final] < max(STRICTNESS[rule_verdict], STRICTNESS[shield_verdict]):
        raise RuntimeError("apply_guardrails loosened a verdict")
    return Risk(risk_level=risk_level, signals=signals, reason=reason, verdict=final)
