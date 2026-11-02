"""One authorized public RM04 run, <= $3 including conservative idle cost, canonical daily ledger."""
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import time
import threading
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from Build.api.room.objects import build_shell_files
from Build.gpu import sf3d
from Build.guardrails import daily_cap
from Build.reconstruction import live_room, shape_upgrade

CANONICAL = Path('C:/Users/HP/Documents/Hackathon/2026-10-26 - Meta Global AI Developer Hackathon')
OUT = ROOT / 'evidence/N63'
CAP = daily_cap.default_path()
JOB = OUT / 'live-data/rooms/n63_public_rm04' / ('63' * 16)
assert not JOB.exists(), 'One live attempt only; inspect the saved result before any retry'
video = CANONICAL / 'test-data/public/RM04.mp4'
assert hashlib.sha256(video.read_bytes()).hexdigest() == '8231fbca041d030f2fc39bd4281af6112e476bf811f548fc9019db53f7cb87ec'
start_spend = daily_cap.today(CAP)['spent_usd']
assert daily_cap.today(CAP)['headroom_usd'] >= 3, 'Need $3 global headroom, including outstanding reservations'
duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                 '-of', 'default=noprint_wrappers=1:nokey=1', str(video)], text=True))
JOB.mkdir(parents=True)
live_room.set_status(JOB, job_id=JOB.name, state='queued', sample=True, source='RM04 Pexels classroom')
started = time.time()
reserve = daily_cap.reserve
spend_lock = threading.Lock()


def row_spend():
    with sqlite3.connect(CAP) as con:
        units = con.execute("SELECT COALESCE(SUM(COALESCE(actual,reserved)),0) FROM spend "
                            "WHERE label LIKE 'N63 live %'").fetchone()[0]
    return Decimal(units) * daily_cap.UNIT


def row_reserve(provider, estimate, label='', **kwargs):
    with spend_lock:
        if row_spend() + Decimal(str(estimate)) > 3:
            raise daily_cap.CapExceeded('N63 row $3 limit (including outstanding reservations)')
        return reserve(provider, estimate, 'N63 live ' + label, **kwargs)


daily_cap.reserve = row_reserve
old_run = shape_upgrade.run
upgrades_finished = threading.Event()


def guarded_generate(png, **kwargs):
    if row_spend() + Decimal(str(sf3d.ESTIMATE_USD)) > 3:
        raise daily_cap.CapExceeded('N63 row $3 limit (including outstanding reservations)')
    return sf3d.generate_remote(png, **kwargs)


def upgrades(d, owner, **kwargs):
    ready_s = time.time() - started
    live_room._write(OUT / 'room-ready.json', {'room_ready_s': ready_s, 'job': str(JOB),
                     'status': json.loads((d / 'status.json').read_text())})
    print(json.dumps({'room_ready_s': ready_s}), flush=True)
    try:
        old_run(d, owner, generate=guarded_generate, **kwargs)
    finally:
        upgrades_finished.set()


shape_upgrade.run = upgrades
live_room.run_job(JOB, video, duration, 'n63_public_rm04', after=build_shell_files)
if json.loads((JOB / 'status.json').read_text())['state'] == 'done':
    assert upgrades_finished.wait(4 * (sf3d.BACKGROUND_BUDGET_S + 1800)), 'background supervisor did not finish'
result = {'source': 'RM04 public Pexels classroom', 'started_at_epoch': started,
          'all_finished_s': time.time() - started, 'status': json.loads((JOB / 'status.json').read_text())}
if (JOB / 'room.json').exists():
    result['kept'] = json.loads((JOB / 'room.json').read_text()).get('shell', {}).get('kept', [])
with sqlite3.connect(CAP) as con:
    result['ledger'] = [dict(zip(['id', 'provider', 'label', 'reserved_usd', 'actual_usd', 'reserved_at', 'settled_at'], row))
                       for row in con.execute('SELECT id,provider,label,reserved/1e8,actual/1e8,reserved_at,settled_at '
                                              "FROM spend WHERE label LIKE 'N63 live %' AND reserved_at >= ?",
                                              (time.strftime('%Y-%m-%dT%H:%M:%S', time.gmtime(started)),))]
result['spend_delta_upper_usd'] = float(daily_cap.today(CAP)['spent_usd'] - start_spend)
result['row_spend_upper_usd'] = float(row_spend())
assert row_spend() <= 3, 'row cap exceeded'
live_room._write(OUT / 'live-result.json', result)
print(json.dumps({'finished_s': result['all_finished_s'], 'spend_delta_upper_usd': result['spend_delta_upper_usd'],
                  'state': result['status']['state'], 'shapes': [o.get('upgrade') for o in result.get('kept', [])]}), flush=True)
