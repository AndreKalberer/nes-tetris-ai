"""Read the NEXT box the way a player does: from the picture, not from RAM.

The bridge samples the last completed frame over x=192..223, y=112..143 at a
2-pixel stride (16x16 bright/dark samples). The box is a sprite image of the
piece in its spawn pose, drawn 4 px right of the I piece's left edge, so the
shape is found from the bounding box of the bright samples.

Measured against the original ROM: a new preview appears on screen 1 frame after
RAM changes (ordinary play) and 2 frames after Select shows a hidden box. This
reader only reports what is drawn, so it inherits those delays.
"""
SAMPLES = 16
# Spawn orientation id of each piece in the ROM/engine tables (nes.engine.SPAWN).
_SHAPES = {
    ('xxx', '.x.'): 2,    # T
    ('xxx', '..x'): 7,    # J
    ('xx.', '.xx'): 8,    # Z
    ('xx', 'xx'): 10,     # O
    ('.xx', 'xx.'): 11,   # S
    ('xxx', 'x..'): 14,   # L
    ('xxxx',): 18,        # I
}
BLANK, UNKNOWN = -1, -2


def classify(bits):
    """bits: 256 chars of '0'/'1'. Returns a spawn orientation id, BLANK or UNKNOWN."""
    if not isinstance(bits, str) or len(bits) != SAMPLES * SAMPLES:
        return UNKNOWN
    cells = [(i, j) for i in range(SAMPLES) for j in range(SAMPLES) if bits[i * SAMPLES + j] == '1']
    if not cells:
        return BLANK
    i0, i1 = min(c[0] for c in cells), max(c[0] for c in cells)
    j0, j1 = min(c[1] for c in cells), max(c[1] for c in cells)
    rows, cols = round((i1 - i0 + 1) / 4), round((j1 - j0 + 1) / 4)
    if not (1 <= rows <= 2 and 2 <= cols <= 4):
        return UNKNOWN
    lit = set(cells)
    shape = tuple(''.join('x' if (i0 + 4 * r + 1, j0 + 4 * c + 1) in lit else '.' for c in range(cols))
                  for r in range(rows))
    return _SHAPES.get(shape, UNKNOWN)
