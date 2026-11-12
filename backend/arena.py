"""Decision Arena: compare competing plans, explain keep/reject, show budget impact."""
from policy import Proposal, evaluate
RANK = {"allow": 0, "escalate": 1, "block": 2}
def rank(m, cands, qty, committed, include_reduced=False):
    plans = []
    for c in cands:
        qs = [(qty, "full quantity")]
        if include_reduced:
            room = max(0, int((m.budget - committed) // c["unit_price"]))
            q = min(qty, m.max_qty_per_item, room)
            if 0 < q < qty: qs.append((q, f"reduced to {q}"))
        for q, label in qs:
            b = dict(item=c["item"], merchant=c["merchant"], unit_price=c["unit_price"], qty=q, delivery_days=c["delivery_days"])
            d = evaluate(m, Proposal(**b), committed); t = round(b["unit_price"] * q, 2)
            plans.append(dict(proposal=b, verdict=d.verdict, reasons=d.reasons, total=t,
                              budget_after=round(m.budget - committed - t, 2),
                              label=f"{c['merchant']}, {label}", seeded=c.get("seeded", False)))
    plans.sort(key=lambda p: (RANK[p["verdict"]], p["total"]))
    first = True
    for p in plans:
        if p["verdict"] == "block": p["why"] = "Rejected: " + "; ".join(p["reasons"])
        elif first: p["why"], first = "Kept: best compliant plan (" + p["verdict"] + ", lowest cost)", False
        else: p["why"] = "Alternative: compliant but ranks lower"
    return plans
