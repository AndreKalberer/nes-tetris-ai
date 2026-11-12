"""Uncapped real Mesen game with pause/resume (copied from the cloud 25-game run; also used by tools/watch-grid.sh).

Runs nes_original.endurance.main() with three local changes (nothing in the repo is edited):
1. No fresh replay check at the end (seed-N.json still holds every input from power-on for a later check).
2. Every CKPT_SECONDS, at a settled piece boundary, the emulator snapshot (bridge_resume.lua) and the bot's
   state (controller, selector, line/level audit) are saved to $RESUME_DIR/ckpt.
3. If $RESUME_DIR/ckpt exists, the game continues from it in a new emulator process instead of starting over.
   The resumed RAM must match the saved RAM hash, and the input log stays complete from power-on.
"""
import collections, hashlib, json, os, pickle, shutil, sys, time
from pathlib import Path

HERE = Path(__file__).resolve().parent
RESUME_DIR = Path(os.environ['RESUME_DIR'])
CKPT_SECONDS = float(os.environ.get('CKPT_SECONDS', 300))
FEED_SECONDS = float(os.environ.get('FEED_SECONDS', 4))
FEED_DIR = Path(os.environ['FEED_DIR']) if os.environ.get('FEED_DIR') else None  # dashboard feed (cloud run only)

from nes_original import runner
from nes_original.mesen import MesenGame

BRIDGE = HERE / 'bridge_resume.lua'
_init = MesenGame.__init__
def _init_resume(self, *a, **k):
    _init(self, *a, **k)
    self.bridge = BRIDGE
    self.identity['bridge_sha256'] = hashlib.sha256(BRIDGE.read_bytes()).hexdigest()
    self._save_next = False
MesenGame.__init__ = _init_resume

_publish = MesenGame._publish
def _publish_resume(self, text):
    if getattr(self, '_save_next', False) and ' action ' in text:
        text = text.replace(' action ', ' actsave ')
        self._save_next = False
    return _publish(self, text)
MesenGame._publish = _publish_resume

def _launch_from(game, snapshot):
    """Start a fresh Mesen that loads the snapshot at power-on; the first request is the next frame."""
    wrapper = RESUME_DIR / f'load-{os.getpid()}.lua'
    wrapper.write_text('MESEN_BRIDGE_LOAD=' + json.dumps(str(snapshot)) + '\n'
                       + 'dofile(' + json.dumps(BRIDGE.as_posix()) + ')\n', encoding='utf-8')
    real = game.bridge
    game.bridge = wrapper
    try:
        game._launch()
    finally:
        game.bridge = real

def _selector_cell(fn):
    names = fn.__code__.co_freevars
    return fn.__closure__[names.index('selector')] if 'selector' in names else None

def _save_ckpt(game, controller, progress, peak_level, ram_sha):
    snap = game.session_dir / 'checkpoint.mss'
    if not snap.is_file():
        return False
    new = RESUME_DIR / 'ckpt.new'
    shutil.rmtree(new, ignore_errors=True); new.mkdir(parents=True)
    shutil.copyfile(snap, new / 'state.mss')
    (new / 'inputs.bin').write_bytes(bytes(game.inputs))
    ctx = controller.context_selector
    cell = _selector_cell(ctx) if ctx is not None else None
    controller.context_selector = None
    try:
        blob = pickle.dumps(dict(controller=controller, progress=progress,
                                 selector=cell.cell_contents if cell else None))
    finally:
        controller.context_selector = ctx
    (new / 'bot.pkl').write_bytes(blob)
    meta = dict(seed=game.seed, start_level=game.start_level, start_frame=game.start_frame,
                placements=game.placements, inputs=len(game.inputs), peak_level=peak_level, ram_sha256=ram_sha,
                time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    (new / 'meta.json').write_text(json.dumps(meta, indent=2))
    old, cur = RESUME_DIR / 'ckpt.old', RESUME_DIR / 'ckpt'
    shutil.rmtree(old, ignore_errors=True)
    if cur.exists(): cur.rename(old)
    new.rename(cur)
    snap.unlink()
    return True

def _load_ckpt():
    for name in ('ckpt', 'ckpt.old'):
        d = RESUME_DIR / name
        if (d / 'meta.json').is_file():
            return d
    return None


def evaluate(output, *, seeds=(1001,), runtime=False, max_frames=120000, config=None, game_factory=None,
             target_level=30, context_selector=None, no_softdrop_at_1g=False, stop_on_success=False,
             no_softdrop_levels=(), nonactive_input=0, stall_rescue_input=0, stall_rescue_after=120,
             stall_rescue_fallback_input=0, stall_rescue_primary_frames=8):
    """runner.evaluate for one endless game, with checkpoints and resume, and no fresh replay check."""
    from nes_original.mesen import SuspectedCrash
    from nes_original.progression import MarathonProgress
    from nes_original.feedback import FeedbackController
    write_json = runner.write_json
    (seed,) = seeds
    game = game_factory()
    ck = _load_ckpt()
    (RESUME_DIR / 'DONE').unlink(missing_ok=True)  # a re-opened game (e.g. after a bot bug fix) is not done
    if ck is None:
        controller = FeedbackController(fixed_reaction=not runtime, tap_period=config.tap_period,
            reaction_frames=getattr(config, 'reaction_frames', 3), late_plan=getattr(config, 'late_plan', 'replan'),
            no_softdrop_at_1g=no_softdrop_at_1g, no_softdrop_levels=tuple(no_softdrop_levels),
            nonactive_input=nonactive_input, stall_rescue_input=stall_rescue_input,
            stall_rescue_after=stall_rescue_after, stall_rescue_fallback_input=stall_rescue_fallback_input,
            stall_rescue_primary_frames=stall_rescue_primary_frames, context_selector=context_selector)
        o = game.reset(start_level=18, seed=int(seed))
        progress = MarathonProgress(18, 0, o.placements)
        progress_counters = progress.update(o.level, o.lines, o.placements)
        peak_level = o.level
    else:
        meta = json.loads((ck / 'meta.json').read_text())
        bot = pickle.loads((ck / 'bot.pkl').read_bytes())
        controller, progress = bot['controller'], bot['progress']
        controller.context_selector = context_selector
        cell = _selector_cell(context_selector)
        if cell is not None and bot['selector'] is not None:
            cell.cell_contents = bot['selector']
        game.started = False
        game.inputs = bytearray((ck / 'inputs.bin').read_bytes())
        assert len(game.inputs) == meta['inputs']
        game.placements, game.start_frame = meta['placements'], meta['start_frame']
        game.start_level, game.seed = meta['start_level'], meta['seed']
        game._nmi_stalled = game._semantic_stalled = 0
        game.stall_events = []
        game.journal_fault = None
        _launch_from(game, ck / 'state.mss')
        game.started = True
        got = hashlib.sha256(game._ram.tobytes()).hexdigest()
        if got != meta['ram_sha256']:
            raise RuntimeError(f'Resumed RAM differs from checkpoint {ck}')
        game.persist()
        o = game.observe()
        progress_counters = None
        peak_level = meta['peak_level']
        with (RESUME_DIR / 'resumes.log').open('a') as f:
            f.write(f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} resumed from {ck.name} at input "
                    f"{meta['inputs']} level {o.level} lines {o.lines}\n")
    error = observed_fault = None
    last_ckpt = last_live = last_feed_write = time.monotonic()
    last_feed_pl = -1
    feed = collections.deque(maxlen=200)
    with game:
        while not o.over and o.frames < max_frames:
            before = o
            try:
                boundary = controller.stage is None and o.phase == 1
                save = boundary and time.monotonic() - last_ckpt >= CKPT_SECONDS
                if save:
                    game._save_next = True
                o = game.step(controller.command(o))
                controller.transition(before, o)
                if controller.stage is None and o.phase == 1 and not o.over:
                    if o.placements - progress.placements > 1:
                        raise RuntimeError('Progress counter audit failed: Missed a settled piece boundary')
                    try:
                        progress_counters = progress.update(o.level, o.lines, o.placements)
                    except ValueError as exc:
                        raise RuntimeError(f'Progress counter audit failed: {exc}') from exc
                    peak_level = max(peak_level, 256 * progress.level_cycles + progress.level)
                if controller.stage is None and o.phase == 1 and not o.over and o.placements != last_feed_pl:
                    last_feed_pl = o.placements
                    feed.append([round(time.time(), 2), ''.join('1' if v else '0' for v in o.board.reshape(-1)),
                                 o.level, progress.absolute_lines, getattr(progress, 'points', 0), progress.level_cycles])
                    if time.monotonic() - last_feed_write >= FEED_SECONDS:
                        write_feed(game, feed); last_feed_write = time.monotonic()
                if boundary and time.monotonic() - last_live >= 20:
                    write_live(game, progress, o); last_live = time.monotonic()
                if save:
                    game._save_next = False
                    if _save_ckpt(game, controller, progress, peak_level,
                                  hashlib.sha256(game._ram.tobytes()).hexdigest()):
                        last_ckpt = time.monotonic()
            except (AssertionError, RuntimeError) as exc:
                error = str(exc)
                if type(exc) is SuspectedCrash:
                    observed_fault = dict(type='SuspectedCrash', reason=str(exc).split(';', 1)[0])
                try: o = game.observe()
                except Exception: pass
                break
        row = dict(seed=int(seed), level=o.level, lines=o.lines, score=o.score, backend=type(game).__name__,
            placements=o.placements, success=False, over=o.over, error=error,
            censored=not o.over and error is None, observed_fault=observed_fault, fault_reproduced=False,
            termination_kind=('suspected_original_crash' if observed_fault else 'controller_error' if error
                              else 'top_out' if o.over else 'frame_limit'),
            exact_ram_rgb_replay=False, controller=controller.stats(), case_state='replay_check_skipped',
            start_level=18, target_level=target_level, target_reached=False, peak_level=peak_level,
            laps=getattr(progress, 'level_cycles', None), points=getattr(progress, 'points', 0),
            lap_points=getattr(progress, 'lap_points', []), absolute_lines=getattr(progress, 'absolute_lines', None),
            frames=o.frames, max_frames=max_frames, progress=progress_counters,
            resumes=(RESUME_DIR / 'resumes.log').read_text().count('\n') if (RESUME_DIR / 'resumes.log').exists() else 0)
        write_json(Path(output) / f'seed-{seed}-case.json', row)
        record = game.replay()
        if observed_fault:
            record['observed_fault'] = observed_fault
        record['note'] = 'played with bridge_resume.lua (snapshot pause/resume); inputs are complete from power-on'
        write_json(Path(output) / f'seed-{seed}.json', record)
    write_live(game, progress, o, alive=False, note=row['termination_kind'])
    (RESUME_DIR / 'DONE').write_text(json.dumps(row) + '\n')
    return [row]


# Points are counted from line clears (the game's own score display stops at 999,999).
from nes_original import progression
_update = progression.MarathonProgress.update
POINTS = {0: 0, 1: 40, 2: 100, 3: 300, 4: 1200}
def _update_points(self, level, raw_lines, placements):
    lvl, cycles, delta = self.level, self.level_cycles, (raw_lines - self.raw_lines) % 25600
    out = _update(self, level, raw_lines, placements)
    self.points = getattr(self, 'points', 0) + POINTS.get(delta, 0) * (lvl + 1)
    if self.level_cycles > cycles:
        self.lap_points = getattr(self, 'lap_points', []) + [self.points]
    return out
progression.MarathonProgress.update = _update_points

def write_live(game, progress, o, alive=True, note=None):
    board = ''.join('1' if v else '0' for v in o.board.reshape(-1))
    data = dict(seed=game.seed, slot=os.environ.get('SLOT'), alive=alive, note=note, level=o.level,
                laps=progress.level_cycles, abs_lines=progress.absolute_lines, points=getattr(progress, 'points', 0),
                lap_points=getattr(progress, 'lap_points', []), board=board, frames=o.frames,
                time_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    tmp = RESUME_DIR / 'live.json.tmp'; tmp.write_text(json.dumps(data)); tmp.replace(RESUME_DIR / 'live.json')

def write_feed(game, feed):
    # Last ~200 settled boards (one per piece) with wall-clock times, for the dashboard's live player.
    if FEED_DIR is None:
        return
    try:
        FEED_DIR.mkdir(exist_ok=True)
        tmp = FEED_DIR / f'.seed{game.seed}.{os.getpid()}.tmp'
        tmp.write_text(json.dumps(dict(seed=game.seed, written=round(time.time(), 2), frames=list(feed))))
        tmp.replace(FEED_DIR / f'seed{game.seed}.json')
    except OSError:
        pass

runner.evaluate = evaluate
from nes_original.endurance import main
sys.argv[0] = 'endurance'
main()
