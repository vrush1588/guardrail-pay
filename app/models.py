from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

Status = Literal["pending_review", "held_for_guardian", "approved", "cancelled"]
Verdict = Literal["allow", "hold", "block"]
RiskLevel = Literal["low", "medium", "high"]
Actor = Literal["shield", "rules", "guardian"]


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class ShieldResult(BaseModel):
    """Shield's raw output. The AI's JSON must validate against this exactly."""
    risk_level: RiskLevel
    signals: list[str]
    reason: str = Field(min_length=1)


class Risk(BaseModel):
    """Final risk on a payment, after apply_guardrails."""
    risk_level: RiskLevel
    signals: list[str] = []
    reason: str
    verdict: Verdict


class PayPalRefs(BaseModel):
    order_id: str | None = None
    authorization_id: str | None = None
    capture_id: str | None = None


class GuardianRules(BaseModel):
    max_amount: float = 50.0
    allow_new_recipients: bool = False
    cooling_off_minutes: int = 30
    paused: bool = False


class AuditEntry(BaseModel):
    timestamp: datetime = Field(default_factory=utcnow)
    actor: Actor
    action: str
    payment_id: str
    detail: str = ""


class PaymentCreate(BaseModel):
    sender: str = "Grandma Rose"
    recipient_name: str = Field(min_length=1)
    amount: float = Field(gt=0)
    currency: str = "USD"
    note: str = ""


class Payment(BaseModel):
    id: str
    sender: str
    recipient_name: str
    recipient_is_new: bool
    amount: float
    currency: str
    note: str
    status: Status = "pending_review"
    risk: Risk | None = None
    paypal: PayPalRefs = Field(default_factory=PayPalRefs)
    created_at: datetime = Field(default_factory=utcnow)
