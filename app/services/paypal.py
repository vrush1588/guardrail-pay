"""PayPal seam: create an order with intent=AUTHORIZE, the payer approves it on PayPal,
authorize it so the funds are held, then either capture (guardian approves / shield
allows) or void (guardian cancels).

Every function takes mock=True/False. Mock calls return fake ids and skip the payer
approval step. Real calls go to PAYPAL_BASE (the Sandbox by default) and need
PAYPAL_CLIENT_ID + PAYPAL_SECRET. PAYPAL_MODE=sandbox picks real calls for new payments;
the seeded demo data always uses the mock.
"""

import logging
import time
import uuid

import httpx

from app.config import PAYPAL_BASE, PAYPAL_CLIENT_ID, PAYPAL_MODE, PAYPAL_SECRET

log = logging.getLogger("guardrail.paypal")

SANDBOX = PAYPAL_MODE == "sandbox"

_http = httpx.Client(base_url=PAYPAL_BASE, timeout=20)
_token: dict = {"value": "", "expires_at": 0.0}


class PayPalError(Exception):
    """A PayPal API call failed. The message includes PayPal's debug_id when there is one."""


def check_config() -> None:
    """Fail at startup, not mid-payment, if sandbox mode has no credentials."""
    if PAYPAL_MODE not in ("mock", "sandbox"):
        raise RuntimeError(f"PAYPAL_MODE must be 'mock' or 'sandbox', not {PAYPAL_MODE!r}")
    missing = [name for name, value in (("PAYPAL_CLIENT_ID", PAYPAL_CLIENT_ID), ("PAYPAL_SECRET", PAYPAL_SECRET))
               if not value or value.startswith("your-")]
    if SANDBOX and missing:
        raise RuntimeError(f"PAYPAL_MODE=sandbox but {', '.join(missing)} not set in .env")


def _fake_id(prefix: str) -> str:
    return f"MOCK-{prefix}-{uuid.uuid4().hex[:10].upper()}"


def _access_token() -> str:
    """OAuth 2.0 client-credentials token, cached until a minute before it expires."""
    if _token["value"] and time.time() < _token["expires_at"]:
        return _token["value"]
    res = _http.post("/v1/oauth2/token", auth=(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
                     data={"grant_type": "client_credentials"})
    if res.status_code != 200:
        raise PayPalError(f"OAuth token failed ({res.status_code}): {res.text[:300]}")
    body = res.json()
    _token["value"] = body["access_token"]
    _token["expires_at"] = time.time() + body.get("expires_in", 300) - 60
    return _token["value"]


def _call(path: str, json: dict | None = None, request_id: str | None = None) -> dict:
    headers = {"Authorization": f"Bearer {_access_token()}", "Prefer": "return=representation"}
    if request_id:
        headers["PayPal-Request-Id"] = request_id  # makes retries of the same call idempotent
    res = _http.post(path, json=json if json is not None else {}, headers=headers)
    if res.status_code >= 400:
        try:
            err = res.json()
            detail = f"{err.get('name')}: {err.get('message')} (debug_id {err.get('debug_id')})"
            details = err.get("details") or []
            if details:
                detail += " " + "; ".join(d.get("issue", "") for d in details)
        except ValueError:
            detail = res.text[:300]
        raise PayPalError(f"POST {path} failed ({res.status_code}) {detail}")
    return res.json() if res.content else {}


def create_order(amount: float, currency: str, recipient_name: str, *, mock: bool,
                 request_id: str = "", return_url: str = "", cancel_url: str = "") -> dict:
    """Returns {id, status, approve_url}. approve_url is None for mock orders (no payer step)."""
    if mock:
        order_id = _fake_id("ORDER")
        log.info("create_order %s %.2f %s -> %s (mock)", recipient_name, amount, currency, order_id)
        return {"id": order_id, "status": "APPROVED", "approve_url": None}

    order = _call("/v2/checkout/orders", request_id=request_id, json={
        "intent": "AUTHORIZE",
        "purchase_units": [{
            "reference_id": request_id or "guardrail",
            "description": f"Guardrail payment to {recipient_name}"[:127],
            "amount": {"currency_code": currency, "value": f"{amount:.2f}"},
        }],
        "payment_source": {"paypal": {"experience_context": {
            "brand_name": "Guardrail",
            "shipping_preference": "NO_SHIPPING",
            "user_action": "CONTINUE",  # funds are only held, not charged, when they approve
            "return_url": return_url,
            "cancel_url": cancel_url,
        }}},
    })
    approve_url = next((link["href"] for link in order.get("links", [])
                        if link["rel"] in ("payer-action", "approve")), None)
    log.info("create_order %s %.2f %s -> %s (%s)", recipient_name, amount, currency, order["id"], order["status"])
    return {"id": order["id"], "status": order["status"], "approve_url": approve_url}


def authorize_order(order_id: str, *, mock: bool) -> dict:
    """Call after the payer has approved the order. Holds the funds."""
    if mock:
        auth_id = _fake_id("AUTH")
        log.info("authorize_order %s -> %s (funds held, mock)", order_id, auth_id)
        return {"authorization_id": auth_id, "status": "AUTHORIZED"}

    order = _call(f"/v2/checkout/orders/{order_id}/authorize", request_id=f"authorize-{order_id}")
    auth = order["purchase_units"][0]["payments"]["authorizations"][0]
    log.info("authorize_order %s -> %s (%s)", order_id, auth["id"], auth["status"])
    return {"authorization_id": auth["id"], "status": auth["status"]}


def capture_authorization(authorization_id: str, *, mock: bool) -> dict:
    if mock:
        capture_id = _fake_id("CAPTURE")
        log.info("capture_authorization %s -> %s (money sent, mock)", authorization_id, capture_id)
        return {"capture_id": capture_id, "status": "COMPLETED"}

    capture = _call(f"/v2/payments/authorizations/{authorization_id}/capture",
                    request_id=f"capture-{authorization_id}", json={"final_capture": True})
    log.info("capture_authorization %s -> %s (%s)", authorization_id, capture["id"], capture["status"])
    return {"capture_id": capture["id"], "status": capture["status"]}


def void_authorization(authorization_id: str, *, mock: bool) -> dict:
    if mock:
        log.info("void_authorization %s (hold released, mock)", authorization_id)
        return {"status": "VOIDED"}

    _call(f"/v2/payments/authorizations/{authorization_id}/void", request_id=f"void-{authorization_id}")
    log.info("void_authorization %s (hold released, nothing sent)", authorization_id)
    return {"status": "VOIDED"}
