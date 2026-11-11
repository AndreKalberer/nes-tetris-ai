"""Keep runs/run-score-nextbox/live-scores.txt updated with each live game's real (uncapped) score.

The on-screen and status.json score stops at 999,999; this totals every line clear from the
events log instead.  Usage: python nes-bot/tools/live_scores.py [SEED ...]  (default 300-303)
"""
import json, sys, time
from datetime import datetime
from pathlib import Path
from nes_original.theoretical_score import timeline

ROOT = Path(__file__).resolve().parents[2]/'runs'/'run-score-nextbox'
seeds = [int(s) for s in sys.argv[1:]] or [300, 301, 302, 303]
while True:
    rows = [f'Updated {datetime.now():%H:%M:%S}  (refreshes every 10 s)', '',
            f'{"seed":>6} {"state":>9} {"level":>6} {"lines":>7} {"real score":>14}']
    for s in seeds:
        folder = ROOT/f'seed{s}'
        try:
            st = json.loads((folder/'status.json').read_text())
            ob = st.get('cached_observation') or {}
            t = timeline(folder/f'gameplay-seed-{s}-events.jsonl')
            score = t[-1][1] if t else 0
            rows.append(f'{s:>6} {st.get("state","?"):>9} {ob.get("level","?"):>6} {ob.get("lines","?"):>7} {score:>14,}')
        except Exception as error:
            rows.append(f'{s:>6} not readable yet ({type(error).__name__})')
    tmp = ROOT/'live-scores.tmp'
    tmp.write_text('\n'.join(rows)+'\n')
    tmp.replace(ROOT/'live-scores.txt')
    time.sleep(10)
