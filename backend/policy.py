"""Deterministic policy engine. The LLM proposes; this code decides."""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional

@dataclass(frozen=True)
class Mandate:
    budget: float
    per_item_cap: float            # hard limit on unit price
    approval_threshold: float      # line total above this needs a human
    max_qty_per_item: int
    deadline: date
    max_delivery_days: int
    allowed_merchants: Optional[frozenset] = None  # None = any

@dataclass(frozen=True)
class Proposal:
    item: str
    merchant: str
    unit_price: float
    qty: int
    delivery_days: int
    today: date = field(default_factory=date.today)

@dataclass
class Decision:
    verdict: str                   # allow | block | escalate
    reasons: list

def evaluate(m: Mandate, p: Proposal, spent: float = 0.0) -> Decision:
    block, esc = [], []
    total = round(p.unit_price * p.qty, 2)
    if p.qty < 1 or p.unit_price <= 0:
        block.append("invalid quantity or price")
    if p.qty > m.max_qty_per_item:
        block.append(f"quantity {p.qty} exceeds max {m.max_qty_per_item}")
    if p.unit_price > m.per_item_cap:
        block.append(f"unit price ${p.unit_price} exceeds per-item cap ${m.per_item_cap}")
    if spent + total > m.budget:
        block.append(f"total ${spent + total:.2f} exceeds budget ${m.budget}")
    if p.delivery_days > m.max_delivery_days:
        block.append(f"delivery {p.delivery_days}d exceeds {m.max_delivery_days}d")
    if p.today.toordinal() + p.delivery_days > m.deadline.toordinal():
        block.append("would arrive after the deadline")
    if m.allowed_merchants is not None and p.merchant not in m.allowed_merchants:
        block.append(f"merchant {p.merchant} not allowed")
    if block:
        return Decision("block", block)
    if total > m.approval_threshold:
        esc.append(f"line total ${total} above approval threshold ${m.approval_threshold}")
        return Decision("escalate", esc)
    return Decision("allow", ["all checks passed"])

def can_pay(decision: Decision, human_approved: bool) -> bool:
    """The only gate to payment. Blocked proposals can never pass."""
    if decision.verdict == "block":
        return False
    if decision.verdict == "escalate":
        return human_approved
    return True
