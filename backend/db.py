"""SQLite persistence: mandate, ledger and audit log survive restarts."""
import sqlite3, json, os, datetime as dt
PATH = os.getenv("DB_PATH", "mandate.db")
def _c(): return sqlite3.connect(PATH)
def init():
    with _c() as c:
        c.execute("create table if not exists kv(k text primary key, v text)")
        c.execute("create table if not exists ledger(id text primary key, n integer, v text)")
        c.execute("create table if not exists audit(id integer primary key autoincrement, ts text, event text, pid text, detail text)")
def kv_get(k, d=None):
    with _c() as c: r = c.execute("select v from kv where k=?", (k,)).fetchone()
    return json.loads(r[0]) if r else d
def kv_set(k, v):
    with _c() as c: c.execute("insert or replace into kv values(?,?)", (k, json.dumps(v)))
def led_put(e):
    with _c() as c:
        r = c.execute("select n from ledger where id=?", (e["id"],)).fetchone()
        n = r[0] if r else (c.execute("select coalesce(max(n),0)+1 from ledger").fetchone()[0])
        c.execute("insert or replace into ledger values(?,?,?)", (e["id"], n, json.dumps(e)))
def led_get(pid):
    with _c() as c: r = c.execute("select v from ledger where id=?", (pid,)).fetchone()
    return json.loads(r[0]) if r else None
def led_all():
    with _c() as c: return [json.loads(r[0]) for r in c.execute("select v from ledger order by n")]
def log(event, pid="", detail=""):
    with _c() as c: c.execute("insert into audit(ts,event,pid,detail) values(?,?,?,?)",
        (dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), event, pid, detail))
def audit_all():
    with _c() as c:
        return [dict(ts=r[0], event=r[1], pid=r[2], detail=r[3]) for r in
                c.execute("select ts,event,pid,detail from audit order by id")]

def reset():
    with _c() as c:
        for t in ("kv", "ledger", "audit"): c.execute(f"delete from {t}")
