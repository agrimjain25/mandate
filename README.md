# Mandate: the trust layer for agentic commerce
*AI proposes. Policy disposes. Humans authorize. PayPal settles. The audit trail proves it.*

Agents can plan purchases, but nobody trusts them with money. Mandate turns a plain-English goal into a **confirmed policy**, lets an AI agent plan and source items, and enforces the policy in **deterministic code** before any PayPal payment. Even a manipulated model cannot spend outside the mandate.

## Features
- **Mandate Studio:** LLM drafts a policy, shows which values it assumed, and nothing runs until you confirm.
- **Agent:** LLM plans the purchase list; items are sourced from Channel3 and checked by the policy engine.
- **Policy gate (`policy.py`):** allow / block / escalate with stated reasons. Re-checked again at payment time. Blocked proposals can never reach PayPal, even if a human clicks approve.
- **Decision Arena:** when a plan fails (cheapest supplier is late, quantity too high), competing plans are compared with keep/reject reasons and budget impact.
- **Adversarial purchase test:** a poisoned listing tries to inflate the order; the gate blocks it. We do not claim to detect every prompt injection; the guarantee is that spending stays inside the confirmed mandate.
- **PayPal sandbox:** Orders API create, buyer approval, capture, server-side verification (status, currency, amount), idempotency keys, signed webhook endpoint.
- **AG Grid ledger and audit trail**, CSV export, **kill switch**, SQLite persistence, live impact stats.

## Run it
    cd backend
    python -m venv .venv
    .venv\Scripts\Activate.ps1        # macOS/Linux: source .venv/bin/activate
    pip install -r requirements.txt
    copy ..\.env.example .env         # macOS/Linux: cp ../.env.example .env  (then fill in keys)
    python -m uvicorn main:app
Open http://127.0.0.1:8000. Run tests with `python -m pytest`.

**Keys:** PayPal sandbox client ID and secret (required), Groq key (AI; app falls back to labelled demo mode without it), Channel3 key (optional; seeded data is labelled).
**Pay as a test buyer:** use a US *Personal* sandbox account from developer.paypal.com (Testing Tools > Sandbox Accounts). Payments are fake sandbox money.

## Demo path
1. Draft and confirm the mandate. 2. Run agent: ledger fills, some items escalate or block. 3. Adversarial test: blocked; Arena offers compliant plans. 4. Use a plan, approve, pay as sandbox buyer; payment returns verified. 5. Export the audit CSV.

## Real vs simulated
- **Real:** Channel3 prices (when a key is set), LLM planning, policy enforcement, PayPal sandbox orders, capture and server-side verification.
- **Simulated:** settlement goes to a PayPal *sandbox merchant*; no goods are bought. The injection payload is a controlled test.
- **Seeded:** fallback product data is labelled "seeded" in the UI.

## Tools used
PayPal Developer (Orders API v2, webhooks), Groq (LLM), Channel3 (product search), AG Grid Community (ledger and audit grids), Render (hosting), FastAPI, SQLite.

## Deploy on Render
Push to GitHub, create a Blueprint from `render.yaml`, set env vars (`BASE_URL` = your Render URL), and add a PayPal webhook to `<BASE_URL>/webhooks/paypal` for `PAYMENT.CAPTURE.COMPLETED`, then set `PAYPAL_WEBHOOK_ID`. Free-tier disk is ephemeral, so data resets on redeploy.
Licence: MIT.
