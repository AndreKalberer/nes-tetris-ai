"""NEXT box is read from the picture (bright samples), never from RAM."""
import unittest

from nes_original.preview import BLANK, UNKNOWN, classify

SHAPES = {2: ('xxx', '.x.'), 7: ('xxx', '..x'), 8: ('xx.', '.xx'), 10: ('xx', 'xx'),
          11: ('.xx', 'xx.'), 14: ('xxx', 'x..'), 18: ('xxxx',)}


def draw(rows):
    """Samples as the bridge produces them: 2 px stride over x=192.., y=112.. (cells are 8 px)."""
    grid = [['0'] * 16 for _ in range(16)]
    x0, y0 = (192, 124) if len(rows[0]) == 4 else (196, 120)   # I piece sits 4 px left / 4 px lower
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch == 'x':
                for dy in range(0, 8, 2):
                    for dx in range(0, 8, 2):
                        grid[(y0 + r * 8 + dy - 112) // 2][(x0 + c * 8 + dx - 192) // 2] = '1'
    return ''.join(''.join(r) for r in grid)


class PreviewTests(unittest.TestCase):
    def test_every_piece_is_recognised(self):
        for orientation, rows in SHAPES.items():
            self.assertEqual(classify(draw(rows)), orientation)

    def test_blank_box_is_blank_not_a_guess(self):
        self.assertEqual(classify('0' * 256), BLANK)

    def test_garbage_is_unknown(self):
        self.assertEqual(classify('1' * 256), UNKNOWN)
        self.assertEqual(classify('01'), UNKNOWN)
        self.assertEqual(classify(None), UNKNOWN)
        self.assertEqual(classify(draw(('x.x', '.x.'))), UNKNOWN)


if __name__ == '__main__':
    unittest.main()
