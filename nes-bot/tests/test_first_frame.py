import json
import unittest
from pathlib import Path

from nes_original.feedback import FeedbackController

WEIGHTS = Path(__file__).resolve().parents[1]/'nes_original'/'weights'
TOOLS = Path(__file__).resolve().parents[1]/'tools'


class FirstFrameTests(unittest.TestCase):
    def test_first_frame_is_opt_in(self):
        self.assertFalse(FeedbackController(selector=None, first_frame=False).first_frame)
        self.assertTrue(FeedbackController(selector=None, first_frame=True).first_frame)

    def test_launcher_turns_on_first_frame_with_the_9_row_weights(self):
        script = (TOOLS/'run-score-ff.sh').read_text(encoding='utf-8')
        self.assertIn('NES_FIRST_FRAME=1 NES_SPAWN_SETTLE=0', script)
        self.assertIn('NUMBA_CACHE_DIR', script)
        self.assertIn('tetris-playout12-b9-vnet-ff.json', script)
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff.json').read_text(encoding='utf-8'))
        self.assertEqual(data['alt_below'], 9)
        self.assertEqual(data['value_net'], 'value-net-v3.npz')
        self.assertEqual(data['value_max_height'], 6)


if __name__ == '__main__':
    unittest.main()
