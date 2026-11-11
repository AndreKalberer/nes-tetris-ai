"""Keep runs/run-score-nextbox/live-scores.txt updated with each live game's real (uncapped) score.

The on-screen and status.json score stops at 999,999; this counts every line clear instead.
Reads resumable games (runs/watch-live/seed<N>/live.json) and older ones (runs/run-score-nextbox/seed<N>).
Usage: python nes-bot/tools/live_scores.py [SEED ...]  (default 300-303)
"""
import json, sys, time
from datetime import datetime
from pathlib import Path
from nes_original.theoretical_score import timeline

RUNS = Path(__file__).resolve().parents[2]/'runs'
OUT = RUNS/'run-score-nextbox'/'live-scores.txt'
seeds = [int(s) for s in sys.argv[1:]] or [300, 301, 302, 303]


def row(s):
    live = RUNS/'watch-live'/f'seed{s}'
    if (live/'live.json').is_file():
        d = json.loads((live/'live.json').read_text())
        state = 'ended' if (live/'DONE').is_file() else 'running'
        resumes = (live/'resumes.log').read_text().count('\n') if (live/'resumes.log').is_file() else 0
        return f'{s:>6} {state:>9} {d["level"]:>6} {d["laps"]:>5} {d["abs_lines"]:>7} {d["points"]:>14,} {resumes:>8}'
    folder = RUNS/'run-score-nextbox'/f'seed{s}'
    st = json.loads((folder/'status.json').read_text())
    ob = st.get('cached_observation') or {}
    t = timeline(folder/f'gameplay-seed-{s}-events.jsonl')
    return (f'{s:>6} {st.get("state","?"):>9} {ob.get("level","?"):>6} {"-":>5} {ob.get("lines","?"):>7} '
            f'{t[-1][1] if t else 0:>14,} {"no save":>8}')


while True:
    rows = [f'Updated {datetime.now():%H:%M:%S}  (refreshes every 10 s)', '',
            f'{"seed":>6} {"state":>9} {"level":>6} {"laps":>5} {"lines":>7} {"real score":>14} {"resumes":>8}']
    for s in seeds:
        try:
            rows.append(row(s))
        except Exception as error:
            rows.append(f'{s:>6} not readable yet ({type(error).__name__})')
    tmp = OUT.with_suffix('.tmp')
    tmp.write_text('\n'.join(rows)+'\n')
    tmp.replace(OUT)
    time.sleep(10)
