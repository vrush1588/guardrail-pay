from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field

Status = Literal["awaiting_payer", "pending_review", "held_for_guardian", "approved", "cancelled", "refunded"]
Verdict = Literal["allow", "hold", "block"]
RiskLevel = Literal["low", "medium", "high"]
Actor = Literal["paypal", "shield", "rules", "guardian"]


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
    mock: bool = True
    order_id: str | None = None
    approve_url: str | None = None  # sandbox only: where the payer approves the order
    authorization_id: str | None = None
    capture_id: str | None = None
    refund_id: str | None = None


class CallScript(BaseModel):
    """What the guardian can say when they phone the sender about a held payment."""
    opening: str = Field(min_length=1)
    questions: list[str] = Field(min_length=1)
    if_scam: str = Field(min_length=1)


class GuardianRules(BaseModel):
    max_amount: float = 50.0
    allow_new_recipients: bool = False
    cooling_off_minutes: int = 30
    paused: bool = False
    hold_expiry_minutes: int = 24 * 60  # unanswered holds are voided after this


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
    call_script: CallScript | None = None
    created_at: datetime = Field(default_factory=utcnow)
    held_at: datetime | None = None  # when it started waiting for the guardian
