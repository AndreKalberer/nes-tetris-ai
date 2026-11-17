"""Read the NEXT box the way a player does: from the picture, not from RAM.

The bridge sends lit/dark samples of the last completed frame over x=192..223,
y=112..143 (32x32, one per pixel). The box shows the piece as sprite blocks of
8x8 px in its spawn pose. A block counts as drawn if any pixel of its 8x8 cell is
lit (at late-level palettes the body can be near-black with only a highlight at the
cell's top-left corner). The grid is anchored at the top-left lit pixel.

Measured against the original ROM: a new preview appears on screen 1 frame after
RAM changes (ordinary play) and 2 frames after Select shows a hidden box. This
reader only reports what is drawn, so it inherits those delays.
"""
SIDE = 32
CELL = 8
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
    """bits: 1024 chars of '0'/'1'. Returns a spawn orientation id, BLANK or UNKNOWN."""
    if not isinstance(bits, str) or len(bits) != SIDE * SIDE:
        return UNKNOWN
    lit = {(i, j) for i in range(SIDE) for j in range(SIDE) if bits[i * SIDE + j] == '1'}
    if not lit:
        return BLANK
    i0, j0 = min(p[0] for p in lit), min(p[1] for p in lit)
    i1, j1 = max(p[0] for p in lit), max(p[1] for p in lit)
    rows, cols = (i1 - i0) // CELL + 1, (j1 - j0) // CELL + 1
    if not (1 <= rows <= 2 and 2 <= cols <= 4):
        return UNKNOWN
    shape = tuple(''.join('x' if any((i0 + CELL * r + a, j0 + CELL * c + b) in lit
                                     for a in range(CELL) for b in range(CELL)) else '.'
                          for c in range(cols)) for r in range(rows))
    return _SHAPES.get(shape, UNKNOWN)
