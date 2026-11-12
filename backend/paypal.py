"""PayPal Orders API v2 (sandbox). Credentials stay server-side."""
import os, httpx
BASE = os.getenv("PAYPAL_BASE", "https://api-m.sandbox.paypal.com")
def _token():
    r = httpx.post(f"{BASE}/v1/oauth2/token", data={"grant_type": "client_credentials"},
                   auth=(os.environ["PAYPAL_CLIENT_ID"], os.environ["PAYPAL_CLIENT_SECRET"]), timeout=20)
    r.raise_for_status(); return r.json()["access_token"]
def _h(rid=None):
    h = {"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"}
    if rid: h["PayPal-Request-Id"] = rid          # idempotency key
    return h
def create_order(amount, ref, request_id, return_url, cancel_url):
    body = {"intent": "CAPTURE",
            "purchase_units": [{"reference_id": ref, "amount": {"currency_code": "USD", "value": f"{amount:.2f}"}}],
            "payment_source": {"paypal": {"experience_context": {"return_url": return_url, "cancel_url": cancel_url, "user_action": "PAY_NOW"}}}}
    r = httpx.post(f"{BASE}/v2/checkout/orders", json=body, headers=_h(request_id), timeout=20)
    r.raise_for_status(); return r.json()
def approve_link(order):
    return next((l["href"] for l in order.get("links", []) if l["rel"] in ("payer-action", "approve")), None)
def capture_order(order_id, rid):
    r = httpx.post(f"{BASE}/v2/checkout/orders/{order_id}/capture", headers=_h(rid), timeout=20)
    r.raise_for_status(); return r.json()
def get_order(order_id):
    r = httpx.get(f"{BASE}/v2/checkout/orders/{order_id}", headers=_h(), timeout=20)
    r.raise_for_status(); return r.json()
def verify(order_id, expected):
    """Server-side check: COMPLETED, USD, and amount equals what policy approved."""
    o = get_order(order_id)
    a = o["purchase_units"][0]["amount"]
    return o["status"] == "COMPLETED" and a["currency_code"] == "USD" and abs(float(a["value"]) - expected) < 0.01
def verify_webhook(headers, event):
    wid = os.getenv("PAYPAL_WEBHOOK_ID")
    if not wid: return False
    h = {k.lower(): v for k, v in headers.items()}
    body = {"auth_algo": h.get("paypal-auth-algo"), "cert_url": h.get("paypal-cert-url"),
            "transmission_id": h.get("paypal-transmission-id"), "transmission_sig": h.get("paypal-transmission-sig"),
            "transmission_time": h.get("paypal-transmission-time"), "webhook_id": wid, "webhook_event": event}
    try:
        r = httpx.post(f"{BASE}/v1/notifications/verify-webhook-signature", json=body, headers=_h(), timeout=20)
        return r.json().get("verification_status") == "SUCCESS"
    except Exception:
        return False
