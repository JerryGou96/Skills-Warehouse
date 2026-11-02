#!/usr/bin/env python3
"""Exclusive durable claim; unknown sends require reconciliation, not retries."""
import sys, json, os, tempfile
from pathlib import Path
from datetime import datetime, timezone
from config import load_config, valid_date

cfg = load_config()
if len(sys.argv) < 3:
    raise SystemExit('usage: delivery.py status|claim|commit YYYY-MM-DD [hash|message_id]')
action, day, *args = sys.argv[1:]
valid_date(day)
if action not in ('status', 'claim', 'commit') or len(args) != (0 if action == 'status' else 1):
    raise SystemExit('Invalid action/argument count')
p = Path(cfg['output_dir']) / day / 'delivery.json'
if action == 'status':
    print(p.read_text() if p.exists() else '{"status":"not_sent"}')
else:
    p.parent.mkdir(parents=True, exist_ok=True)
    if action == 'claim':
        data = {'status':'pending', 'hash':args[0], 'at':datetime.now(timezone.utc).isoformat()}
        try:
            with p.open('x') as f:
                json.dump(data, f); f.flush(); os.fsync(f.fileno())
        except FileExistsError:
            raise SystemExit('ALREADY_CLAIMED: inspect delivery.json; never automatically resend')
        print('CLAIMED')
    else:
        # Exclusive commit lock prevents concurrent receipt replacement.
        lock=p.parent/'.delivery-commit-lock'
        try: lock.mkdir()
        except FileExistsError: raise SystemExit('COMMIT_LOCKED: reconcile before retry')
        tmp=None
        try:
            data=json.loads(p.read_text())
            if data['status']=='delivered':
                if data.get('message_id')!=args[0]: raise SystemExit('RECEIPT_CONFLICT')
            elif data['status']=='pending':
                data.update(status='delivered', message_id=args[0])
                with tempfile.NamedTemporaryFile(mode='w',dir=p.parent,delete=False) as f:
                    tmp=Path(f.name); json.dump(data,f,indent=2); f.flush(); os.fsync(f.fileno())
                tmp.replace(p)
            else: raise SystemExit('Invalid delivery state; reconcile manually')
            print('COMMITTED')
        finally:
            if tmp and tmp.exists(): tmp.unlink()
            lock.rmdir()
