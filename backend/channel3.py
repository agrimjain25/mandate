"""Product search via Channel3 POST /v1/search. Falls back to labelled seeded data."""
import os
def _p(item, merchant, price, days): return dict(item=item, merchant=merchant, unit_price=price, delivery_days=days, seeded=True)
SEEDED = [
    _p("Folding table", "SeedMart", 79.0, 3), _p("Folding table", "BargainBox", 55.0, 9), _p("Folding table", "VoltCo", 85.0, 4),
    _p("Stackable chair", "SeedMart", 34.0, 3), _p("Stackable chair", "BargainBox", 28.0, 8),
    _p("Power strip", "VoltCo", 18.5, 7), _p("Power strip", "SeedMart", 22.0, 3),
    _p("Whiteboard", "SeedMart", 120.0, 4), _p("Whiteboard", "OfficeHub", 99.0, 5),
]
def _seed(q):
    return [p for p in SEEDED if q.lower() in p["item"].lower() or p["item"].lower() in q.lower()]
def search(q: str) -> list:
    key = os.getenv("CHANNEL3_API_KEY")
    if not key: return _seed(q)
    try:
        import httpx
        r = httpx.post("https://api.trychannel3.com/v1/search", headers={"x-api-key": key},
                       json={"query": q, "limit": 10}, timeout=20)
        r.raise_for_status(); out = []
        for p in r.json().get("products", []):
            for o in (p.get("offers") or [])[:2]:
                pr = o.get("price")
                if isinstance(pr, dict): pr = pr.get("price") or pr.get("amount")
                if pr is None: continue
                out.append(dict(item=p.get("title", q), merchant=o.get("domain", "unknown"), unit_price=float(pr),
                                delivery_days=int(os.getenv("DEFAULT_DELIVERY_DAYS", "4")),
                                delivery_estimated=True, url=o.get("url"), seeded=False))
        return out or _seed(q)
    except Exception:
        return _seed(q)
