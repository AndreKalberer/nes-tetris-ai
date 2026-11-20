"""Spawn prediction (NES_SPAWN_PREDICT): the first input lands on the spawn frame.

Andre's condition (2026-11-19): the bot never reads the piece from memory before it is on screen. The piece type
of a predicted spawn must come only from the NEXT-box picture it already saw.
"""
import inspect
import unittest
from unittest.mock import patch

import numpy as np

from nes.engine import Phase
from nes_original import mesen, spawn_predict
from tests.test_picture_delay import MockGame


def run(seed, level, steps, picture, rng_seed=1):
    """Drive a mock game; `picture(game)` is what the NEXT-box picture reads at each poll."""
    rng = np.random.default_rng(rng_seed)
    choices = [0, 64, 128, 1, 2, 32, 65, 129]
    with patch.object(mesen, '_classify_preview', lambda bits: picture(game)):
        game = MockGame(seed=seed, level=level)
        game.spawn_predict = True
        game._spawner = spawn_predict.SpawnPredictor()
        game._seen_next, game._spawn_next, game.spawn_predictions = None, False, 0
        records = []
        for _ in range(steps):
            if game.engine.over:
                break
            obs = game.observe()
            if obs.spawn_predicted:
                records.append((obs, game.history[-1]))      # history[-1] = the real present frame
            game._step_raw(int(rng.choice(choices)) if obs.phase == 1 else 0)
    return game, records


def true_next(game):
    """What the drawn NEXT box shows for the frame on screen: the engine's upcoming piece."""
    return game.history[-2].next_orientation


class SpawnPredictTest(unittest.TestCase):
    def test_prediction_matches_the_real_spawn_frame(self):
        for level in (19, 29, 100, 200):
            with self.subTest(level=level):
                records = []
                for seed in range(3, 9):
                    game, got = run(seed, level, 4000, true_next, rng_seed=seed)
                    self.assertEqual(game.prediction_misses, 0)
                    records += got
                self.assertGreater(len(records), 20)
                for obs, now in records:
                    self.assertEqual(now.phase, Phase.ACTIVE)
                    c = now.control
                    self.assertEqual((obs.x, obs.y, obs.orientation), (c.x, c.y, c.orientation))
                    self.assertEqual((obs.fall, obs.soft, obs.das), (c.fall, c.soft, c.das))
                    self.assertTrue(obs.fresh_spawn)
                    self.assertEqual(obs.next_orientation, -1)

    def test_piece_type_comes_from_the_picture_not_from_memory(self):
        # The picture says piece 18 (I) while the game's RAM spawns something else: the observation must follow
        # the picture. If it read RAM, the orientation would be the real piece.
        game, records = run(3, 19, 3000, lambda g: 18)
        self.assertGreater(len(records), 10)
        self.assertTrue(any(now.control.orientation != 18 for _, now in records))
        for obs, _ in records:
            self.assertEqual(obs.orientation, 18)

    def test_no_prediction_without_a_picture_of_the_piece(self):
        game, records = run(3, 19, 3000, lambda g: -1)   # NEXT box unreadable the whole game
        self.assertEqual(records, [])

    def test_source_never_reads_the_piece_from_ram(self):
        # The predicted pose is built from _seen_next (picture) only: no RAM index appears in that branch.
        src = inspect.getsource(mesen.MesenGame._observe_shown)
        branch = src.split('spawn_predicted = False', 1)[1].split('elif phase == 1', 1)[0]
        self.assertIn('self._seen_next', branch)
        self.assertNotIn('r[0x', branch)
        self.assertNotIn('self._ram', branch)
        upd = inspect.getsource(mesen.MesenGame._update_spawn)
        self.assertNotIn('0xBF', upd)
        self.assertNotIn('0xbf', upd)


class ControllerEndToEnd(unittest.TestCase):
    def test_controller_plays_from_the_predicted_spawn_frame(self):
        import os
        from nes_original.feedback import FeedbackController
        for level in (19, 29):
            with self.subTest(level=level), patch.dict(os.environ, NES_FIRST_FRAME='1', NES_BLIND_FIRST='1'):
                with patch.object(mesen, '_classify_preview', lambda bits: true_next(game)):
                    game = MockGame(seed=4, level=level)
                    game.spawn_predict = True
                    game._spawner = spawn_predict.SpawnPredictor()
                    game._seen_next, game._spawn_next, game.spawn_predictions = None, False, 0
                    c = FeedbackController(fixed_reaction=True, tap_period=2, reaction_frames=0, late_plan='retarget')
                    obs = game.observe()
                    for _ in range(1500):
                        if game.engine.over:
                            break
                        buttons = c.command(obs)
                        game._step_raw(int(buttons) if False else _mesen_bits(buttons))
                        after = game.observe()
                        c.transition(obs, after)
                        obs = after
                self.assertGreater(game.spawn_predictions, 15)
                self.assertEqual(game.prediction_misses, 0)
                self.assertEqual(getattr(c, 'spawn_mispredicts', 0), 0)
                self.assertGreater(c.blind_replans, 10)
                self.assertLessEqual(c.target_misses, 1)


def _mesen_bits(buttons):
    return int(buttons)


if __name__ == '__main__':
    unittest.main()
