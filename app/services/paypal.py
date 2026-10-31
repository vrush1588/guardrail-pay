"""PayPal seam. Every function here is a stub that returns fake ids.

Flow it will implement: create an order with intent=AUTHORIZE, authorize it so the
funds are held, then either capture (guardian approves / shield allows) or void
(guardian cancels).
"""

import logging
import uuid

log = logging.getLogger("guardrail.paypal")


def _fake_id(prefix: str) -> str:
    return f"MOCK-{prefix}-{uuid.uuid4().hex[:10].upper()}"


def create_order(amount: float, currency: str, recipient_name: str) -> dict:
    # TODO: replace with real PayPal sandbox calls (POST /v2/checkout/orders, intent=AUTHORIZE)
    order_id = _fake_id("ORDER")
    log.info("create_order %s %.2f %s -> %s", recipient_name, amount, currency, order_id)
    return {"id": order_id, "status": "CREATED"}


def authorize_order(order_id: str) -> dict:
    # TODO: replace with real PayPal sandbox calls (POST /v2/checkout/orders/{id}/authorize)
    auth_id = _fake_id("AUTH")
    log.info("authorize_order %s -> %s (funds held)", order_id, auth_id)
    return {"authorization_id": auth_id, "status": "AUTHORIZED"}


def capture_authorization(authorization_id: str) -> dict:
    # TODO: replace with real PayPal sandbox calls (POST /v2/payments/authorizations/{id}/capture)
    capture_id = _fake_id("CAPTURE")
    log.info("capture_authorization %s -> %s (money sent)", authorization_id, capture_id)
    return {"capture_id": capture_id, "status": "COMPLETED"}


def void_authorization(authorization_id: str) -> dict:
    # TODO: replace with real PayPal sandbox calls (POST /v2/payments/authorizations/{id}/void)
    log.info("void_authorization %s (hold released, nothing sent)", authorization_id)
    return {"status": "VOIDED"}
