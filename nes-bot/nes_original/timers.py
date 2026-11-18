"""Rebuild the ROM's control timers from what a player can know.

The game keeps gravity, auto-repeat (DAS) and soft-drop counters in RAM ($65, $66,
$6E, $6F, previous buttons $B6). They are not drawn on screen, so the policy must
not read them. They are fully determined by the bot's own controller inputs since
the game started, the visible board/piece/level, and the ROM's documented rules,
which `nes.engine.control_frame` implements (the rebuilt timers matched real Mesen RAM on 6,862 active
frames of random-input games at start levels 0, 9, 17, 18, 19; see tests/test_nes_timers.py).

Start-of-game state (observed on the original ROM at the first active frame, same
at start levels 0, 9, 17, 18, 19): fall=1, das=0, soft=0xA1, soft_points=0.
Every later spawn: fall=0, soft=0, soft_points=0; DAS carries over from the last
active frame, including the lock frame's own update.
"""
from nes.engine import Control, control_frame

FIRST_FRAME = dict(fall=1, das=0, soft=0xA1, soft_points=0)


def game_bits(mesen_buttons):
    """Controller byte as sent through Mesen (A=1..Right=128) -> the ROM's bit order (all 8 buttons)."""
    return int(f'{int(mesen_buttons) & 255:08b}'[::-1], 2)


class TimerTracker:
    def __init__(self):
        self.fall, self.das, self.soft, self.soft_points = (FIRST_FRAME[k] for k in
                                                           ('fall', 'das', 'soft', 'soft_points'))
        self.previous = 0

    def step(self, before, buttons, after_phase):
        """before: dict(active, board, x, y, orientation, level) of the last observation.
        buttons: controller byte sent this frame. after_phase: phase seen after the frame."""
        bits = game_bits(buttons)
        if before['active']:
            c = Control(before['x'], before['y'], before['orientation'], self.fall, self.das,
                        self.soft, self.soft_points, self.previous)
            n, _ = control_frame(before['board'], c, bits & 0xC7, before['level'])
            self.fall, self.das, self.soft, self.soft_points = n.fall, n.das, n.soft, n.soft_points
        if after_phase == 1 and not before['active']:
            self.fall = self.soft = self.soft_points = 0   # new piece spawned; DAS carries
        self.previous = bits

    def values(self):
        return dict(fall=self.fall, das=self.das, soft=self.soft, soft_points=self.soft_points,
                    previous=self.previous)
