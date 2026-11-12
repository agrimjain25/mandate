import os, tempfile
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "t.db")
from datetime import date
import db, arena, channel3
from policy import Mandate
M = Mandate(1500, 200, 100, 40, date(2026, 11, 30), 5)
def test_cheapest_but_late_is_rejected():
    plans = arena.rank(M, channel3.search("Folding table"), 2, 0)
    cheapest = min(plans, key=lambda p: p["proposal"]["unit_price"])
    assert cheapest["verdict"] == "block" and plans[0]["verdict"] != "block"
def test_attack_quantity_gets_compliant_reduced_plan():
    plans = arena.rank(M, channel3.search("Folding table"), 5000, 0, include_reduced=True)
    assert all(p["verdict"] == "block" for p in plans if p["proposal"]["qty"] == 5000)
    assert any(p["verdict"] != "block" and p["proposal"]["qty"] <= 40 for p in plans)
def test_audit_and_ledger_persist():
    db.init(); db.log("x", "p", "d"); db.led_put({"id": "1", "status": "proposed"})
    assert db.audit_all()[-1]["event"] == "x" and db.led_get("1")["status"] == "proposed"

def test_unknown_item_returns_no_candidates():
    assert channel3.search("unicorn saddle") == []
