"""Hidden ROM timers are rebuilt from our own inputs + visible state, and match real RAM.

tests/data/timer_trace.npz is a recording of 4 real random-input games on the original ROM
(Mesen) at start levels 0, 9, 18, 19: per frame the RAM timers, the visible board/piece,
and the controller byte sent. The tracker never sees the RAM timers.
"""
from pathlib import Path
import unittest

import numpy as np

from nes_original.timers import TimerTracker, game_bits

TRACE = Path(__file__).parent / 'data' / 'timer_trace.npz'


class TimerTrackerTests(unittest.TestCase):
    def test_matches_real_rom_timers_on_every_active_frame(self):
        d = np.load(TRACE)
        board = np.unpackbits(d['board'], axis=1)[:, :200].reshape(-1, 20, 10).astype(bool)
        tracker, checked = None, 0
        for i in range(len(d['f'])):
            if d['f'][i] == 0:
                tracker = TimerTracker()
            else:
                p = i - 1
                tracker.step(dict(active=d['phase'][p] == 1, board=board[p], x=int(d['pose'][p][0]),
                    y=int(d['pose'][p][1]), orientation=int(d['pose'][p][2]), level=int(d['pose'][p][3])),
                    int(d['sent'][p]), int(d['phase'][i]))
            if d['phase'][i] == 1:
                v = tracker.values()
                self.assertEqual((v['fall'], v['das'], v['soft'], v['soft_points'], v['previous']),
                                 tuple(int(x) for x in d['timers'][i]), f'frame {i}')
                checked += 1
        self.assertGreater(checked, 1500)

    def test_button_bits_are_reversed_to_rom_order(self):
        self.assertEqual(game_bits(1), 0x80)      # A
        self.assertEqual(game_bits(128), 0x01)    # Right
        self.assertEqual(game_bits(32), 0x04)     # Down


if __name__ == '__main__':
    unittest.main()
