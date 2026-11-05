import json
import os
import subprocess
import sys
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

    def test_wide_launcher_adds_tetris_levels_and_drops_the_lowstack_zone(self):
        script = (TOOLS/'run-score-wide.sh').read_text(encoding='utf-8')
        self.assertIn('NES_FIRST_FRAME=1 NES_SPAWN_SETTLE=0', script)
        self.assertIn('tetris-playout12-b9-vnet-ff-wide.json', script)
        self.assertNotIn('lowstack-246-249', script)
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-wide.json').read_text(encoding='utf-8'))
        self.assertEqual(data['alt_levels'], [[29, 150], [159, 167], [174, 248]])
        self.assertEqual(data['alt_below'], 9)

    def test_holes_launcher_doubles_only_the_tetris_hole_weights(self):
        script = (TOOLS/'run-score-holes.sh').read_text(encoding='utf-8')
        self.assertIn('NES_FIRST_FRAME=1 NES_SPAWN_SETTLE=0', script)
        self.assertIn('tetris-playout12-b9-vnet-ff-holes.json', script)
        self.assertNotIn('lowstack-246-249', script)
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-holes.json').read_text(encoding='utf-8'))
        wide = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-wide.json').read_text(encoding='utf-8'))
        doubled = {'holes', 'hole_rows', 'covered'}
        for name, new, old in zip(data['features'], data['alt_weights'], wide['alt_weights']):
            self.assertAlmostEqual(new, 2*old if name in doubled else old, msg=name)
        self.assertEqual({k: v for k, v in data.items() if k not in ('alt_weights', 'scope')},
                         {k: v for k, v in wide.items() if k not in ('alt_weights', 'scope')})

    def test_top_launcher_adds_tetris_mode_at_250_252_and_254(self):
        script = (TOOLS/'run-score-top.sh').read_text(encoding='utf-8')
        self.assertIn('NES_FIRST_FRAME=1 NES_SPAWN_SETTLE=0', script)
        self.assertIn('tetris-playout12-b9-vnet-ff-top.json', script)
        self.assertNotIn('250 254', script)
        self.assertIn('168 172 28 2', script)
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-top.json').read_text(encoding='utf-8'))
        holes = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-holes.json').read_text(encoding='utf-8'))
        self.assertEqual(data['alt_levels'], [[29, 150], [159, 167], [174, 248], [250, 252], [254, 254]])
        self.assertEqual({k: v for k, v in data.items() if k not in ('alt_levels', 'scope')},
                         {k: v for k, v in holes.items() if k not in ('alt_levels', 'scope')})

    def test_start_launcher_adds_tetris_mode_from_level_18(self):
        script = (TOOLS/'run-score-start.sh').read_text(encoding='utf-8')
        self.assertIn('NES_FIRST_FRAME=1 NES_SPAWN_SETTLE=0', script)
        self.assertIn('tetris-playout12-b9-vnet-ff-start.json', script)
        self.assertEqual(script.replace('-start', '-top').replace('levels 18-28, the 1G', 'the 1G'),
                         (TOOLS/'run-score-top.sh').read_text(encoding='utf-8'))
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-start.json').read_text(encoding='utf-8'))
        top = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-top.json').read_text(encoding='utf-8'))
        self.assertEqual(data['alt_levels'], [[18, 150], [159, 167], [174, 248], [250, 252], [254, 254]])
        self.assertEqual({k: v for k, v in data.items() if k not in ('alt_levels', 'scope')},
                         {k: v for k, v in top.items() if k not in ('alt_levels', 'scope')})

    def test_safe157_launcher_only_adds_the_risk_budget(self):
        script = (TOOLS/'run-score-safe157.sh').read_text(encoding='utf-8')
        self.assertIn('export NES_RISK_BUDGET=17:.9,14:.5', script)
        start = (TOOLS/'run-score-start.sh').read_text(encoding='utf-8')
        kept = [l for l in script.splitlines() if 'NES_RISK_BUDGET' not in l and not l.startswith('#')]
        self.assertEqual('\n'.join(kept).replace('-safe157', '-start'),
                         '\n'.join(l for l in start.splitlines() if not l.startswith('#')))

    def test_lowtop_launcher_only_swaps_the_weights(self):
        script = (TOOLS/'run-score-lowtop.sh').read_text(encoding='utf-8')
        safe = (TOOLS/'run-score-safe157.sh').read_text(encoding='utf-8')
        code = lambda text: [l for l in text.splitlines() if not l.startswith('#')]
        self.assertEqual([l.replace('-lowtop', '-safe157').replace('ff-safe157.json', 'ff-start.json') for l in code(script)],
                         code(safe))
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-lowtop.json').read_text(encoding='utf-8'))
        start = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-start.json').read_text(encoding='utf-8'))
        self.assertEqual(data['alt_below_levels'], [[240, 255, 8]])
        self.assertEqual({k: v for k, v in data.items() if k not in ('alt_below_levels', 'scope')},
                         {k: v for k, v in start.items() if k != 'scope'})

    def test_alt_below_levels_lowers_the_tetris_stack_cap(self):
        from nes_original.sim import tuned_selector
        sel = tuned_selector('dellacherie', alt_weights=str(WEIGHTS/'tetris-playout12-b9-vnet-ff-lowtop.json'))
        self.assertEqual(sel.alt[1], 9)
        self.assertEqual(sel.alt_below_levels, ((240, 255, 8),))
        plain = tuned_selector('dellacherie', alt_weights=str(WEIGHTS/'tetris-playout12-b9-vnet-ff-start.json'))
        self.assertEqual(plain.alt_below_levels, ())

    def test_risk_budget_env_override(self):
        code = ('from nes_original import crash_model as c; print(c.RISK_BUDGET)')
        env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1]))
        env.pop('NES_RISK_BUDGET', None)
        base = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(base, '((17, 0.9), (14, 0.5), (11, 0.3))')
        env['NES_RISK_BUDGET'] = '17:.9,14:.5'
        fixed = subprocess.run([sys.executable, '-c', code], env=env, capture_output=True, text=True, check=True).stdout.strip()
        self.assertEqual(fixed, '((17, 0.9), (14, 0.5))')

    def test_other_spawn_settings_get_their_own_numba_cache(self):
        probe = ('import numba.core.config as c; from nes_original import sim; '
                 'print(sim.SPAWN_SETTLE, c.CACHE_DIR)')
        env = {k: v for k, v in os.environ.items() if k != 'NUMBA_CACHE_DIR'}
        env['PYTHONPATH'] = str(Path(__file__).resolve().parents[1])
        out = {}
        for settle in ('0', '2'):
            env['NES_SPAWN_SETTLE'] = settle
            out[settle] = subprocess.run([sys.executable, '-c', probe], env=env, check=True,
                                         capture_output=True, text=True).stdout.split()
        self.assertEqual(out['0'][0], '0')
        self.assertTrue(out['0'][1].endswith('settle0'))
        self.assertEqual(out['2'], ['2'])  # default: numba's own cache location, untouched


if __name__ == '__main__':
    unittest.main()
