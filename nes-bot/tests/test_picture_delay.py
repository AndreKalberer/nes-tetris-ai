"""NES_PICTURE_DELAY: observations are the frame on screen (previous poll's RAM) plus a predicted present.

A mock emulator serves RAM frames from the Python engine (nes.engine.Game), so no Mesen is needed.
"""
import unittest

import numpy as np

from nes.engine import Game, Phase, Rules
from nes_original import mesen
from nes_original.timers import TimerTracker, game_bits


def ram_of(g):
    r = np.zeros(2048, np.uint8)
    r[0x400:0x4C8] = np.where(np.asarray(g.board).reshape(-1) != 0, 0x7B, 0xEF)
    k = g.control
    r[0x60], r[0x61], r[0x62] = k.x, k.y, k.orientation
    r[0x64], r[0x68], r[0xC0] = g.level % 256, int(g.phase), 4
    return r


class MockGame(mesen.MesenGame):
    """MesenGame with the emulator replaced by the Python engine (one poll = one engine frame)."""
    def __init__(self, seed, level=19):
        self.picture_delay = True
        self._shown = self._pending_track = self._predicted = None
        self._shown_placements = self._last_buttons = 0
        self.predictions = self.prediction_misses = 0
        self.inputs, self.start_frame, self.start_level, self.placements = bytearray(), 0, 18, 0
        self._unknown_previews, self._active_age = 0, 0
        self.engine = Game(seed, Rules(start_level=18))
        self.engine.level = level
        self.history = [self.engine]       # engine state of every poll, for the checks
        self._ram, self._request = ram_of(self.engine), dict(sequence=0, preview=None)
        c = self.engine.control
        self._tracker = TimerTracker()
        self._tracker.fall, self._tracker.das, self._tracker.soft, self._tracker.soft_points = c.fall, c.das, c.soft, c.soft_points
        self.started = True
        self._step_raw(0)                  # as reset() does in delay mode

    def _publish(self, text):
        self._sent = int(text.split()[-1])

    def _wait_request(self, sequence=None):
        import copy
        self.engine = copy.deepcopy(self.engine)
        self.engine.tick(game_bits(self._sent) & 0xC7)
        self.history.append(self.engine)
        self._ram, self._request = ram_of(self.engine), dict(sequence=len(self.history), preview=None)

    def _watchdog(self, before):
        pass


class PictureDelayTest(unittest.TestCase):
    def test_default_is_on(self):
        self.assertTrue(mesen.PICTURE_DELAY)

    def test_observation_is_the_frame_on_screen_and_the_prediction_is_exact(self):
        rng = np.random.default_rng(5)
        choices = [0, 64, 128, 1, 2, 32, 65, 129]          # Mesen order: Left 64, Right 128, A 1, B 2, Down 32
        for level in (19, 29):
            with self.subTest(level=level):
                game = MockGame(seed=3, level=level)
                fresh_seen = spawns = 0
                for _ in range(3000):
                    if game.engine.over:
                        break
                    obs = game.observe()
                    shown = game.history[-2]          # one poll behind = the picture
                    np.testing.assert_array_equal(obs.board, np.asarray(shown.board) != 0)
                    now = game.history[-1]
                    if shown.phase == Phase.ACTIVE and now.phase == Phase.ACTIVE:
                        self.assertEqual((obs.x, obs.y, obs.orientation),
                                         (now.control.x, now.control.y, now.control.orientation))
                        self.assertEqual((obs.fall, obs.das), (now.control.fall, now.control.das))
                    if obs.fresh_spawn:
                        fresh_seen += 1
                    if shown.phase == Phase.ACTIVE and (len(game.history) == 2 or game.history[-3].phase != Phase.ACTIVE):
                        spawns += 1
                        self.assertTrue(obs.fresh_spawn)  # first frame of a piece on screen
                    game._step_raw(int(rng.choice(choices)) if obs.phase == 1 else 0)
                self.assertGreater(spawns, 8)
                self.assertEqual(fresh_seen, spawns)
                self.assertGreater(game.predictions, 100)
                self.assertEqual(game.prediction_misses, 0)


if __name__ == '__main__':
    unittest.main()
