# Devpost submission draft
**Tagline:** Let AI agents buy things without trusting them with your money.

**Problem:** Delegation is all-or-nothing. An agent either spends freely or a human approves every step. Intent has no machine-enforceable form, nothing independent stops a hallucinating or manipulated agent, and there is no audit trail.

**Solution:** Mandate turns a plain-English goal (budget, per-item cap, deadline, approval threshold) into a policy the user confirms. An LLM plans and sources purchases; a deterministic rules engine allows, blocks or escalates each one; the user authorizes; PayPal settles; every step is logged. Built for event organizers, student societies and small teams buying under fixed budgets.

**How it uses PayPal:** Orders API create, buyer approval, capture, and server-side verification of status, currency and amount; idempotency keys; signed webhooks. The agent never holds credentials or calls capture.
**How it uses AI:** Groq LLM drafts the policy, plans the purchase list and proposes quantities. It only proposes. It cannot widen its own permissions.
**Sponsors:** Channel3 (product search), AG Grid (ledger, audit), Render (hosting).

**Honesty:** payments settle to a sandbox merchant; the injection test is a controlled payload; seeded data is labelled.

## Video script (under 3 min)
0:00 problem. 0:15 type mandate, confirm policy. 0:40 run agent, ledger fills. 1:05 adversarial test blocked. 1:30 Decision Arena, choose plan, approve. 1:55 pay as sandbox buyer, verified. 2:25 audit CSV, stats, kill switch, close.
