"""Play original-game attempts to a target level and verify each one by exact replay.

evaluate() drives one game per seed through the feedback controller, audits the game's own
level and line counters at every settled piece, then replays the recorded inputs in a fresh
emulator and requires RAM, picture and clocks to match.
"""
from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np

from nes.actions import ActionRules
from nes_original.feedback import FeedbackController


def write_json(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True,exist_ok=True)
    temporary = path.with_suffix(path.suffix+'.tmp')
    temporary.write_text(json.dumps(data,indent=2)+'\n',encoding='utf-8')
    temporary.replace(path)


@dataclass
class Config:
    tap_period: int = 0
    reaction_frames: int = 3
    late_plan: str = 'replan'

    def __post_init__(self):
        ActionRules(horizontal_period=self.tap_period,reaction_frames=self.reaction_frames)
        if self.late_plan not in ('replan','keep','retarget'):
            raise ValueError("Late plan handling must be 'replan', 'keep' or 'retarget'")


def heuristic_choice(observation, plan):
    """Default selector: the planner's geometric heuristic (clipped as the old feature prior was)."""
    return int(np.clip(np.asarray(plan.actions.heuristic)/10,-10,2).astype(np.float32).argmax())


ENDLESS = 10**9  # target level that is never reached: play until the game ends


def evaluate(output, *, seeds=(1001,1013), runtime=False, max_frames=120000,config=None,
             game_factory=None,target_level=30,context_selector=None,no_softdrop_at_1g=False,
             stop_on_success=False,no_softdrop_levels=(),nonactive_input=0,
             stall_rescue_input=0,stall_rescue_after=120,
             stall_rescue_fallback_input=0,stall_rescue_primary_frames=8):
    """Reach a native level from18 at a settled controller boundary and replay.

    target_level255 means reaching255, not clearing it or certifying rebirth.
    It requires the first-cycle line window3290..3293 and valid per-piece
    original counter transitions; replaying corrupted RAM cannot certify it.
    Targets above 255 are absolute levels across rebirths (level 255 -> 0):
    256*cycles+level from audited wraps; 511 = level 255 on the second lap.
    ENDLESS (a huge target) plays until the game ends or the frame budget runs out.
    max_frames bounds gameplay frames after menu entry, not reconstruction time.
    context_selector(observation, plan) returns the index of the chosen proposal; without
    one, the planner's geometric heuristic picks.
    """
    if isinstance(target_level,bool) or not isinstance(target_level,int) or not 19<=target_level<=ENDLESS:
        raise ValueError('target_level must be an integer from19 (absolute levels count rebirths; '
                         f'{ENDLESS} = endless) for a level18 start')
    if isinstance(max_frames,bool) or not isinstance(max_frames,int) or max_frames<1:
        raise ValueError('max_frames must be a positive integer gameplay-frame budget')
    if context_selector is not None and not callable(context_selector):
        raise ValueError('context_selector must be callable')
    if not isinstance(no_softdrop_at_1g,bool):
        raise ValueError('no_softdrop_at_1g must be a boolean control-profile choice')
    if not isinstance(stop_on_success,bool):
        raise ValueError('stop_on_success must be a boolean')
    try:
        no_softdrop_levels=tuple(no_softdrop_levels)
    except TypeError as exc:
        raise ValueError('no_softdrop_levels must be an iterable of levels') from exc
    from nes_original.mesen import SuspectedCrash
    from nes_original.progression import MarathonProgress
    config=config or Config()
    if game_factory is None:
        from nes_original.env import OriginalGame  # nes-py core, used by the tests
        game_factory=OriginalGame
    rows = []
    for seed in seeds:
        controller = FeedbackController(fixed_reaction=not runtime,tap_period=config.tap_period,
            reaction_frames=getattr(config,'reaction_frames',3),
            late_plan=getattr(config,'late_plan','replan'),
            no_softdrop_at_1g=no_softdrop_at_1g,
            no_softdrop_levels=no_softdrop_levels,
            nonactive_input=nonactive_input,
            stall_rescue_input=stall_rescue_input,stall_rescue_after=stall_rescue_after,
            stall_rescue_fallback_input=stall_rescue_fallback_input,
            stall_rescue_primary_frames=stall_rescue_primary_frames,
            context_selector=context_selector if context_selector is not None else heuristic_choice)
        with game_factory() as game:
            o = game.reset(start_level=18,seed=int(seed))
            error = None
            observed_fault = None
            peak_level = o.level
            target_reached = False
            progress = MarathonProgress(18,0,o.placements)
            progress_counters = progress.update(o.level,o.lines,o.placements)
            while not o.over and not target_reached and o.frames < max_frames:
                before = o
                try:
                    o = game.step(controller.command(o))
                    controller.transition(before,o)
                    if controller.stage is None and o.phase==1 and not o.over:
                        try:
                            if o.placements-progress.placements>1:
                                raise ValueError('Missed a settled piece boundary')
                            progress_counters = progress.update(o.level,o.lines,o.placements)
                        except ValueError as exc:
                            raise RuntimeError(f'Progress counter audit failed: {exc}') from exc
                        absolute_level = 256*progress.level_cycles+progress.level
                        peak_level = max(peak_level,absolute_level)
                        if target_level<=255:
                            target_reached = progress.level>=target_level and progress.level_cycles==0 and (
                                target_level!=255 or 3290<=progress.absolute_lines<=3293)
                        else:
                            target_reached = absolute_level>=target_level
                except (AssertionError,RuntimeError) as exc:
                    error = str(exc)
                    if type(exc) is SuspectedCrash:
                        observed_fault = dict(type='SuspectedCrash',reason=str(exc).split(';',1)[0])
                    # Both native backends expose a non-advancing observation.
                    # A transition may fail after a successful frame; retain
                    # that latest cached/native state without stepping again.
                    try:
                        o = game.observe()
                    except Exception:
                        pass
                    break
            path = Path(output)/f'seed-{seed}.json'
            backend=type(game).__name__
            case_path = Path(output)/f'seed-{seed}-case.json'
            row = dict(seed=int(seed),level=o.level,lines=o.lines,score=o.score,backend=backend,
                placements=o.placements,success=False,
                over=o.over,error=error,censored=not o.over and not target_reached and error is None,
                observed_fault=observed_fault,fault_reproduced=False,
                termination_kind=('suspected_original_crash' if observed_fault else
                    'controller_error' if error else 'top_out' if o.over else
                    'target_reached' if target_reached else 'frame_limit'),
                exact_ram_rgb_replay=False,controller=controller.stats(),
                case_state='verification_pending',start_level=18,target_level=target_level,
                target_reached=target_reached,peak_level=peak_level,
                frames=o.frames,max_frames=max_frames,
                progress=progress_counters,
                target_criterion='Audited native counters at a settled active-piece controller boundary')
            # Write gameplay telemetry before screen capture/core shutdown or
            # fresh-process reconstruction can fail or be interrupted.
            write_json(case_path,row)
            try:
                record = game.replay()
                if observed_fault:
                    record['observed_fault'] = observed_fault
                write_json(path,record)
            except Exception as exc:
                row.update(case_state='verification_failed',verification_error=repr(exc),
                           verification_failure_phase='replay_capture')
                write_json(case_path,row)
                write_json(Path(output)/f'seed-{seed}-raw-inputs.json',
                    dict(input_hex=game.inputs.hex(),backend=backend,
                         exact_replay_verified=False,error=error,capture_error=repr(exc)))
                raise
        try:
            with game_factory() as other:
                if observed_fault:
                    other.load_replay(record,expected_fault=observed_fault)
                else:
                    other.load_replay(record)
        except Exception as exc:
            row.update(case_state='verification_failed',verification_error=repr(exc),
                       verification_failure_phase='fresh_replay')
            write_json(case_path,row)
            raise
        row.update(case_state='verified',exact_ram_rgb_replay=True,
                   success=target_reached and not error,fault_reproduced=observed_fault is not None)
        write_json(case_path,row)
        rows.append(row)
        write_json(Path(output)/'results.json',rows)
        if stop_on_success and row['success']:
            break
    write_json(Path(output)/'results.json',rows)
    return rows
