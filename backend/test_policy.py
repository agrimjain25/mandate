from datetime import date
from policy import Mandate, Proposal, evaluate, can_pay

T = date(2026, 11, 1)
M = Mandate(1500, 200, 100, 40, date(2026, 11, 30), 5)
def P(**k):
    d = dict(item="chair", merchant="shopA", unit_price=50, qty=2, delivery_days=3, today=T)
    d.update(k); return Proposal(**d)

def test_allow(): assert evaluate(M, P()).verdict == "allow"
def test_escalate_over_threshold(): assert evaluate(M, P(unit_price=60, qty=2)).verdict == "escalate"
def test_injected_quantity_blocked():
    d = evaluate(M, P(qty=5000)); assert d.verdict == "block"
def test_over_budget_blocked(): assert evaluate(M, P(), spent=1480).verdict == "block"
def test_item_cap_blocked(): assert evaluate(M, P(unit_price=250, qty=1)).verdict == "block"
def test_late_delivery_blocked(): assert evaluate(M, P(delivery_days=9)).verdict == "block"
def test_deadline_blocked(): assert evaluate(M, P(today=date(2026, 11, 29), delivery_days=4)).verdict == "block"
def test_blocked_never_pays():
    d = evaluate(M, P(qty=5000)); assert not can_pay(d, human_approved=True)
def test_escalate_needs_human():
    d = evaluate(M, P(unit_price=60, qty=2))
    assert not can_pay(d, False) and can_pay(d, True)
