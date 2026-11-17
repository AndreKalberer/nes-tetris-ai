"""Blind first input (NES_BLIND_FIRST=1): plan without NEXT on the spawn frame, replan once it is drawn."""
import os
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from nes.actions import ActionRules
from nes.engine import Game, Phase, Rules
from nes_original.feedback import FeedbackController
from nes_original.timers import game_bits


def play(pieces, seed, hidden_frames, level=19):
    """Drive the controller on the Python engine; NEXT reads -1 for the first `hidden_frames` active frames."""
    with patch.dict(os.environ, NES_FIRST_FRAME='1', NES_BLIND_FIRST='1'):
        c = FeedbackController(fixed_reaction=True, tap_period=2, reaction_frames=0, late_plan='retarget')
    g = Game(seed, Rules(start_level=18))
    g.level = level
    age, misses, locks = 0, 0, 0
    while locks < pieces and not g.over:
        active = g.phase == Phase.ACTIVE
        k = g.control
        obs = SimpleNamespace(board=g.board != 0, x=k.x, y=k.y, orientation=k.orientation,
            next_orientation=-1 if active and age < hidden_frames else g.next_orientation,
            fall=k.fall, das=k.das, soft=k.soft, soft_points=k.soft_points, previous=k.previous, pending=0,
            input_pipeline=0, phase=int(g.phase), level=g.level, lines=g.lines, score=0,
            placements=g.placements, frames=g.frames, start_level=18, over=g.over)
        buttons = c.command(obs)
        plan, selected = getattr(c, 'plan', None), getattr(c, 'selected', None)
        g.tick(game_bits(buttons) & 0xC7)
        age = age+1 if active and g.phase == Phase.ACTIVE else 0
        if active and g.phase != Phase.ACTIVE:
            locks += 1
            want = plan.actions.controls[selected]
            misses += (g.control.x, g.control.y, g.control.orientation) != (want.x, want.y, want.orientation)
            c.stage = None
    return c, locks, misses


class BlindFirstTests(unittest.TestCase):
    def test_schedule_offset_is_opt_in(self):
        self.assertEqual(ActionRules().start_frame, 0)
        with self.assertRaises(ValueError):
            ActionRules(start_frame=-1)

    def test_replanned_piece_lands_where_the_second_plan_says(self):
        for hidden in (1, 2):   # 2 = box just shown again after a Select hide
            with self.subTest(hidden=hidden):
                c, locks, misses = play(40, seed=3, hidden_frames=hidden)
                self.assertEqual(locks, 40)
                self.assertEqual(misses, 0)
                self.assertEqual(c.blind_starts, 40)
                self.assertEqual(c.blind_replans, 40)

    def test_fast_and_python_paths_agree_with_an_offset(self):
        from nes import actions
        fast = actions._fast_module()
        if not fast:
            self.skipTest('numba not installed')
        g = Game(4, Rules(start_level=19))
        while g.phase != Phase.ACTIVE:
            g.tick(0)
        obs = g.observe()
        for start in (0, 1, 2, 3):
            rules = ActionRules(reaction_frames=0, horizontal_period=2, start_frame=start)
            piece = actions.TYPE[obs.control.orientation]
            self.assertEqual(actions._timed_paths(obs, rules, piece), actions._timed_paths_python(obs, rules, piece))

    def test_off_by_default(self):
        with patch.dict(os.environ, NES_FIRST_FRAME='1'):
            os.environ.pop('NES_BLIND_FIRST', None)
            self.assertFalse(FeedbackController(tap_period=2).blind_first)


if __name__ == '__main__':
    unittest.main()
