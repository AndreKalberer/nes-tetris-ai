"""verify_batch enforces the goal on the replayed state, not on the proof file."""
import json
import tempfile
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from nes_original import verify_batch


class FakeGame:
    level = 18
    def __enter__(self): return self
    def __exit__(self, *a): return False
    def load_replay(self, record): return SimpleNamespace(level=self.level)


class GoalTests(unittest.TestCase):
    def run_group(self, goal, level):
        FakeGame.level = level
        with tempfile.TemporaryDirectory() as d:
            proof = Path(d) / 'p.json'
            proof.write_text(json.dumps(dict(protocol='x', result=dict(level=255))))
            with patch('nes_original.verify_batch.limit_cpu'), patch('nes_original.env.OriginalGame', FakeGame):
                return verify_batch.verify_group([(0, str(proof))], 1, None, d, goal)[0]

    def test_replay_below_goal_fails_even_if_file_claims_more(self):
        row = self.run_group(255, 18)
        self.assertFalse(row['verified'])
        self.assertIn('Goal not reached', row['error'])
        self.assertIn('Traceback', row['traceback'])   # diagnostics kept, not replaced by a generic error

    def test_replay_reaching_goal_passes(self):
        self.assertTrue(self.run_group(255, 255)['verified'])

    def test_no_goal_keeps_old_behaviour(self):
        self.assertTrue(self.run_group(None, 18)['verified'])


if __name__ == '__main__':
    unittest.main()
