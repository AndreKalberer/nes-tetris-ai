"""NEXT box is read from the picture (bright samples), never from RAM."""
import unittest

from nes_original.preview import BLANK, UNKNOWN, classify

SHAPES = {2: ('xxx', '.x.'), 7: ('xxx', '..x'), 8: ('xx.', '.xx'), 10: ('xx', 'xx'),
          11: ('.xx', 'xx.'), 14: ('xxx', 'x..'), 18: ('xxxx',)}


def draw(rows, body=True):
    """32x32 samples (one per pixel of x=192..223, y=112..143) as the bridge produces them."""
    grid = [['0'] * 32 for _ in range(32)]
    x0, y0 = (0, 12) if len(rows[0]) == 4 else (4, 8)   # I piece sits 4 px left / 4 px lower
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == 'x':
                for dy in range(8):
                    for dx in range(8):
                        if body or (dy == 0 and dx == 0):   # body=False: only the highlight pixel
                            grid[y0 + r * 8 + dy][x0 + c * 8 + dx] = '1'
    return ''.join(''.join(r) for r in grid)


class PreviewTests(unittest.TestCase):
    def test_every_piece_is_recognised(self):
        for orientation, rows in SHAPES.items():
            self.assertEqual(classify(draw(rows)), orientation)

    def test_blocks_that_are_only_a_highlight_pixel_are_still_recognised(self):
        # Glitched late-level palette (seen at level 148): body near-black, one lit pixel per block.
        for orientation, rows in SHAPES.items():
            self.assertEqual(classify(draw(rows, body=False)), orientation)

    def test_blank_box_is_blank_not_a_guess(self):
        self.assertEqual(classify('0' * 1024), BLANK)

    def test_garbage_is_unknown(self):
        self.assertEqual(classify('1' * 1024), UNKNOWN)
        self.assertEqual(classify('01'), UNKNOWN)
        self.assertEqual(classify(None), UNKNOWN)
        self.assertEqual(classify(draw(('x.x', '.x.'))), UNKNOWN)


if __name__ == '__main__':
    unittest.main()
