import logging
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from app import store
from app.config import BASE_URL, GEMINI_MODEL, PAYPAL_BASE
from app.guardrails import RULE_PREFIX, apply_guardrails
from app.models import AuditEntry, GuardianRules, Payment, PaymentCreate, utcnow
from app.services import paypal, shield

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(name)s  %(message)s")
log = logging.getLogger("guardrail")

FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


def _last_night_at(hour: int, minute: int) -> datetime:
    """Yesterday at the given local time, so seed (c) always reads as late at night."""
    local = datetime.now().astimezone() - timedelta(days=1)
    return local.replace(hour=hour, minute=minute, second=0, microsecond=0)


SEED_SCENARIOS = [
    (PaymentCreate(sender="Grandma Rose", recipient_name="Mike Turner", amount=800,
                   note="URGENT - your grandson needs bail money tonight, don't tell his parents"), None),
    (PaymentCreate(sender="Leo (age 12)", recipient_name="School Cafe", amount=5,
                   note="Lunch"), None),
    (PaymentCreate(sender="Leo (age 12)", recipient_name="GameWorld Store", amount=60,
                   note="Skin pack for my game"), lambda: _last_night_at(23, 40)),
]


@asynccontextmanager
async def lifespan(_: FastAPI):
    paypal.check_config()
    shield_mode = f"Gemini {GEMINI_MODEL}" if shield.USE_GEMINI else "mock (no GEMINI_API_KEY)"
    paypal_mode = f"sandbox {PAYPAL_BASE}" if paypal.SANDBOX else "mock"
    print(f"\n  guardrail is running (PayPal: {paypal_mode}, Shield: {shield_mode})")
    print(f"    Senior:   {BASE_URL}/senior.html")
    print(f"    Guardian: {BASE_URL}/guardian.html\n", flush=True)
    yield


app = FastAPI(title="guardrail", lifespan=lifespan)


def process_payment(data: PaymentCreate, created_at: datetime | None = None,
                    mock: bool | None = None) -> Payment:
    """Create the PayPal order. Mock orders go straight on to hold_and_check(); sandbox
    orders wait as awaiting_payer until the payer approves them on PayPal (/api/paypal/return)."""
    payment = Payment(
        id=uuid.uuid4().hex[:12],
        recipient_is_new=store.is_new_recipient(data.recipient_name),
        created_at=created_at or utcnow(),
        **data.model_dump(),
    )
    payment.paypal.mock = not paypal.SANDBOX if mock is None else mock

    try:
        order = paypal.create_order(
            payment.amount, payment.currency, payment.recipient_name, mock=payment.paypal.mock,
            request_id=payment.id,
            return_url=f"{BASE_URL}/api/paypal/return?payment_id={payment.id}",
            cancel_url=f"{BASE_URL}/api/paypal/cancel?payment_id={payment.id}",
        )
    except paypal.PayPalError as err:
        log.error("PayPal create_order failed: %s", err)
        raise HTTPException(502, f"PayPal could not create the order: {err}")
    payment.paypal.order_id = order["id"]
    store.save(payment)

    if order["approve_url"]:
        payment.paypal.approve_url = order["approve_url"]
        payment.status = "awaiting_payer"
        store.audit("paypal", "order_created", payment.id, f"{order['id']} waiting for payer approval")
        return payment
    return hold_and_check(payment)


def hold_and_check(payment: Payment) -> Payment:
    """The pipeline: hold funds -> Shield scores -> guardrails -> send or wait for guardian."""
    payment.status = "pending_review"
    payment.paypal.approve_url = None
    first_seen = store.first_seen(payment.recipient_name, payment.created_at)
    payment.paypal.authorization_id = paypal.authorize_order(
        payment.paypal.order_id, mock=payment.paypal.mock)["authorization_id"]

    try:
        ai_verdict = shield.score(payment, store.usual_amount(payment.sender))
        store.audit("shield", f"scored_{ai_verdict.risk_level}", payment.id, ai_verdict.reason)
    except shield.ShieldError as err:
        ai_verdict = None
        store.audit("shield", "failed", payment.id, str(err))

    payment.risk = apply_guardrails(payment, ai_verdict, store.guardian_rules,
                                    first_seen=first_seen, now=payment.created_at)
    rule_hits = [s for s in payment.risk.signals if s.startswith(RULE_PREFIX)]
    store.audit("rules", f"verdict_{payment.risk.verdict}", payment.id,
                "; ".join(rule_hits) or "no family rule triggered")

    if payment.risk.verdict == "allow":
        try:
            payment.paypal.capture_id = paypal.capture_authorization(
                payment.paypal.authorization_id, mock=payment.paypal.mock)["capture_id"]
            payment.status = "approved"
            return payment
        except paypal.PayPalError as err:
            # Funds are still held, so the guardian can retry the capture with Approve.
            store.audit("paypal", "capture_failed", payment.id, str(err))
    payment.status = "held_for_guardian"
    log.info("Guardian notified: %s -> %s $%.2f (%s)", payment.sender,
             payment.recipient_name, payment.amount, payment.risk.verdict)
    return payment


def _get_or_404(payment_id: str) -> Payment:
    payment = store.get(payment_id)
    if payment is None:
        raise HTTPException(404, "Payment not found")
    return payment


def _require_held(payment: Payment) -> None:
    if payment.status != "held_for_guardian":
        raise HTTPException(409, f"Payment is {payment.status}, not held_for_guardian")


@app.post("/api/payments", response_model=Payment, status_code=201)
def create_payment(data: PaymentCreate):
    return process_payment(data)


@app.get("/api/payments", response_model=list[Payment])
def list_payments():
    return store.list_all()


@app.get("/api/payments/{payment_id}", response_model=Payment)
def get_payment(payment_id: str):
    return _get_or_404(payment_id)


@app.post("/api/payments/{payment_id}/approve", response_model=Payment)
def approve_payment(payment_id: str):
    payment = _get_or_404(payment_id)
    _require_held(payment)
    try:
        payment.paypal.capture_id = paypal.capture_authorization(
            payment.paypal.authorization_id, mock=payment.paypal.mock)["capture_id"]
    except paypal.PayPalError as err:
        store.audit("paypal", "capture_failed", payment.id, str(err))
        raise HTTPException(502, f"PayPal capture failed: {err}")
    payment.status = "approved"
    store.audit("guardian", "approved", payment.id, f"captured {payment.paypal.capture_id}")
    return payment


@app.post("/api/payments/{payment_id}/cancel", response_model=Payment)
def cancel_payment(payment_id: str):
    payment = _get_or_404(payment_id)
    _require_held(payment)
    try:
        paypal.void_authorization(payment.paypal.authorization_id, mock=payment.paypal.mock)
    except paypal.PayPalError as err:
        store.audit("paypal", "void_failed", payment.id, str(err))
        raise HTTPException(502, f"PayPal void failed: {err}")
    payment.status = "cancelled"
    store.audit("guardian", "cancelled", payment.id, f"voided {payment.paypal.authorization_id}")
    return payment


@app.get("/api/paypal/return", include_in_schema=False)
def paypal_return(payment_id: str, token: str = ""):
    """PayPal sends the payer here after they approve the order (token = the order id)."""
    payment = _get_or_404(payment_id)
    if payment.status == "awaiting_payer":  # a page refresh must not authorize twice
        if token and token != payment.paypal.order_id:
            raise HTTPException(400, "PayPal token does not match this payment's order")
        store.audit("paypal", "payer_approved", payment.id, payment.paypal.order_id)
        try:
            hold_and_check(payment)
        except paypal.PayPalError as err:
            log.error("PayPal authorize failed: %s", err)
            payment.status = "cancelled"
            store.audit("paypal", "authorize_failed", payment.id, str(err))
    return RedirectResponse(f"/senior.html?payment={payment.id}", status_code=303)


@app.get("/api/paypal/cancel", include_in_schema=False)
def paypal_cancel(payment_id: str):
    """The payer clicked cancel on PayPal. Nothing was authorized, so there is nothing to void."""
    payment = _get_or_404(payment_id)
    if payment.status == "awaiting_payer":
        payment.status = "cancelled"
        payment.paypal.approve_url = None
        store.audit("paypal", "payer_cancelled", payment.id, payment.paypal.order_id)
    return RedirectResponse(f"/senior.html?payment={payment.id}", status_code=303)


@app.get("/api/rules", response_model=GuardianRules)
def get_rules():
    return store.guardian_rules


@app.get("/api/audit", response_model=list[AuditEntry])
def get_audit():
    return store.audit_log


@app.post("/api/seed", response_model=list[Payment])
def seed():
    """Reset the store and load the three demo scenarios. Always mock PayPal: no payer
    is there to approve sandbox orders."""
    store.reset()
    return [process_payment(data, at() if at else None, mock=True) for data, at in SEED_SCENARIOS]


@app.get("/", include_in_schema=False)
def root():
    return RedirectResponse("/guardian.html")


# Mounted last so the /api routes above take priority.
app.mount("/", StaticFiles(directory=FRONTEND_DIR, html=True), name="frontend")
