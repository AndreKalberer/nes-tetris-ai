"""Predict that the piece on screen's successor spawns on the very next frame.

Fair-play rule 2 lets the bot predict the present from the frame on screen plus its own inputs. After a lock the
ROM runs a fixed sequence of phases (lock, scan, clear, score, goal, receive, spawn). This module replays that
sequence with the Python engine (nes.engine.Game) from what the picture shows: the board, the locked piece's
row and the phase. It reads no RAM beyond what the delayed observation already uses, and it never sees the
next piece: which piece spawns comes only from the NEXT box picture (see nes_original/mesen.py).
"""
import copy

import numpy as np

from nes.engine import Game, Phase, Rules


class SpawnPredictor:
    def __init__(self):
        self.sim = None
        self.prev_phase = None
        self.hits = 0

    def update(self, phase, board, x, y, orientation, level=0):
        """One call per shown frame. Returns True if the next frame is the first active frame of a new piece.

        phase: phase byte of the frame on screen; board: bool 20x10 of that frame; x, y, orientation: the locked piece.
        """
        phase = int(phase)
        prev, self.prev_phase = self.prev_phase, phase
        if phase in (1, 10):
            self.sim = None
            return False
        if self.sim is None:
            if phase != 2 or prev != 1:
                return False          # not followed from the lock: make no prediction
            g = Game(0, Rules())
            g.phase = Phase.LOCK
            g.control = g.control.__class__(x=int(x), y=int(y), orientation=int(orientation))
            g.vram_row = min(32, max(0, int(y) - 2))
            g.level = int(level)
            self.sim = g
        g = self.sim
        g.board = (np.asarray(board) != 0).astype(np.uint8)
        try:
            g.phase = Phase(phase)
        except ValueError:
            self.sim = None
            return False
        probe = copy.deepcopy(g)
        probe.tick(0)
        nxt = probe.phase == Phase.ACTIVE
        g.tick(0)
        self.hits += bool(nxt)
        return bool(nxt)
