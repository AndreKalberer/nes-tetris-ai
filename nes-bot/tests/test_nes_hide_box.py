"""Next-box (Select) option in the crash model: the hide flag follows the kept Down choice."""
import unittest
from unittest import mock

from nes_original import crash_model
from tests.test_nes_crash_model import control, observation, plan


class HideBoxTest(unittest.TestCase):
    def rows(self, cleared, soft_points):
        obs = observation(172, 1661)
        obs.board = None   # unknown rows: worst case
        with mock.patch.object(crash_model, 'HIDE_BOX', True), mock.patch.object(crash_model, 'USE_CYCLE_MODEL', True):
            return crash_model.crash_map_alerts(obs, plan([cleared], [control(soft_points=soft_points)]), counts=[0]*5)

    def test_safe_double_without_down_keeps_box(self):
        # Shown box and no Down: safe. Down would need the box hidden, but Down is not kept,
        # so the box must stay shown (hidden with no Down is risky). Real seed 957 crashed here.
        row = self.rows(2, 5)[0]
        self.assertEqual(row['modelled_crash_probability'], 0)
        self.assertFalse(row.get('use_down'))
        self.assertFalse(row.get('hide_box'))

    def test_triple_hides_box(self):
        row = self.rows(3, 0)[0]
        self.assertTrue(row.get('hide_box'))


if __name__ == '__main__':
    unittest.main()
