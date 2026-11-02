"""N49: summarise the daily_cap ledger rows of this run (provider, count, settled USD, first/last UTC). python ledger.py <spend.sqlite3>"""
import sqlite3, sys
c = sqlite3.connect(sys.argv[1])
for t in [r[0] for r in c.execute("select name from sqlite_master where type = 'table'")]:
    cols = [r[1] for r in c.execute(f"pragma table_info({t})")]
    print(t, cols, c.execute(f"select count(*) from {t}").fetchone())
    if "provider" in cols:
        amt = [x for x in cols if "actual" in x or "settled" in x or "usd" in x]
        print(c.execute(f"select provider, count(*), {', '.join(f'sum({a})' for a in amt)} from {t} group by provider").fetchall(), amt)
