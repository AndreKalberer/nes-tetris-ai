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

    def test_first_frame_weights_use_a_9_row_stack(self):
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff.json').read_text(encoding='utf-8'))
        self.assertEqual(data['alt_below'], 9)
        self.assertEqual(data['value_net'], 'value-net-v3.npz')
        self.assertEqual(data['value_max_height'], 6)

    def test_wide_weights_add_tetris_levels(self):
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-wide.json').read_text(encoding='utf-8'))
        self.assertEqual(data['alt_levels'], [[29, 150], [159, 167], [174, 248]])
        self.assertEqual(data['alt_below'], 9)

    def test_holes_weights_double_only_the_tetris_hole_weights(self):
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-holes.json').read_text(encoding='utf-8'))
        wide = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-wide.json').read_text(encoding='utf-8'))
        doubled = {'holes', 'hole_rows', 'covered'}
        for name, new, old in zip(data['features'], data['alt_weights'], wide['alt_weights']):
            self.assertAlmostEqual(new, 2*old if name in doubled else old, msg=name)
        self.assertEqual({k: v for k, v in data.items() if k not in ('alt_weights', 'scope')},
                         {k: v for k, v in wide.items() if k not in ('alt_weights', 'scope')})

    def test_top_weights_add_tetris_mode_at_250_252_and_254(self):
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-top.json').read_text(encoding='utf-8'))
        holes = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-holes.json').read_text(encoding='utf-8'))
        self.assertEqual(data['alt_levels'], [[29, 150], [159, 167], [174, 248], [250, 252], [254, 254]])
        self.assertEqual({k: v for k, v in data.items() if k not in ('alt_levels', 'scope')},
                         {k: v for k, v in holes.items() if k not in ('alt_levels', 'scope')})

    def test_start_weights_add_tetris_mode_from_level_18(self):
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-start.json').read_text(encoding='utf-8'))
        top = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-top.json').read_text(encoding='utf-8'))
        self.assertEqual(data['alt_levels'], [[18, 150], [159, 167], [174, 248], [250, 252], [254, 254]])
        self.assertEqual({k: v for k, v in data.items() if k not in ('alt_levels', 'scope')},
                         {k: v for k, v in top.items() if k not in ('alt_levels', 'scope')})

    def test_lowtop_weights_only_add_the_8_row_cap(self):
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

    def test_mid_weights_add_tetris_mode_at_151_153(self):
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-mid.json').read_text(encoding='utf-8'))
        lowtop = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-lowtop.json').read_text(encoding='utf-8'))
        self.assertEqual(data['alt_levels'][0], [18, 153])
        self.assertEqual(data['alt_levels'][1:], lowtop['alt_levels'][1:])
        self.assertEqual(data['alt_below_levels'], [[151, 153, 6], [240, 255, 8]])
        self.assertEqual({k: v for k, v in data.items() if k not in ('alt_levels', 'alt_below_levels', 'scope')},
                         {k: v for k, v in lowtop.items() if k not in ('alt_levels', 'alt_below_levels', 'scope')})

    def test_mid_caps_the_stack_at_151_153_only(self):
        from nes_original.sim import tuned_selector
        sel = tuned_selector('dellacherie', alt_weights=str(WEIGHTS/'tetris-playout12-b9-vnet-ff-mid.json'))
        self.assertEqual(sel.alt[1], 9)
        self.assertEqual(sel.alt[3][0], (18, 153))
        self.assertEqual(sel.alt_below_levels, ((151, 153, 6), (240, 255, 8)))

    def test_v8_weights_only_swap_the_value_net(self):
        data = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-v8.json').read_text(encoding='utf-8'))
        base = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-mid.json').read_text(encoding='utf-8'))
        changed = {'value_net': 'value-net-v8b.npz', 'value_lam': 40.0, 'value_levels': [[18, 153], [176, 243]], 'value_max_height': 9}
        self.assertEqual({k: data[k] for k in changed}, changed)
        self.assertEqual({k: v for k, v in data.items() if k not in changed and k != 'scope'},
                         {k: v for k, v in base.items() if k not in changed and k != 'scope'})

    def test_v8_value_net_loads(self):
        from nes_original.sim import tuned_selector
        sel = tuned_selector('dellacherie', alt_weights=str(WEIGHTS/'tetris-playout12-b9-vnet-ff-v8.json'))
        self.assertEqual(sel.value_levels, ((18, 153), (176, 243)))
        self.assertEqual(sel.value_max_height, 9)
        self.assertEqual([w.shape for w in sel.value_net[::2]], [(256, 210), (256, 256), (1, 256)])

    def test_nextbox_launcher_settings(self):
        script = (TOOLS/'run-score-nextbox.sh').read_text(encoding='utf-8')
        for setting in ('NES_HIDE_BOX=1', 'NES_FIRST_FRAME=1', 'NES_SPAWN_SETTLE=0',
                        'NES_RISK_BUDGET=17:.9,14:.5', 'NUMBA_CACHE_DIR', '--late-plan retarget'):
            self.assertIn(setting, script)
        data = json.loads((WEIGHTS/'v8-wide154.json').read_text(encoding='utf-8'))
        v8 = json.loads((WEIGHTS/'tetris-playout12-b9-vnet-ff-v8.json').read_text(encoding='utf-8'))
        self.assertEqual(data['alt_levels'][0], [18, 167])
        self.assertEqual(data['value_net'], v8['value_net'])
        self.assertEqual(data['alt_weights'], v8['alt_weights'])

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
