"""Uniform sampling of the menu wait (the only randomness a player controls).

An independent audit (2026-11-15, actual-ROM calibration) found the menu's RNG
state repeats every 7,598 distinct waits, so waits 0..32766 hit some phases 4-5
times and others 4 times. Drawing waits uniformly from 0..32766 therefore
over-weights part of the cycle (a sampling bias, not piece prediction).
Draw waits from ONE cycle instead. The cycle length is the auditor's measurement,
not re-measured here.
"""
MENU_CYCLE = 7598
MAX_WAIT = 32766


def uniform_menu_waits(count, rng):
    """`count` distinct waits, each phase of the menu cycle equally likely (rng: random.Random)."""
    if not 1 <= count <= MENU_CYCLE:
        raise ValueError(f'count must be 1..{MENU_CYCLE}')
    return sorted(rng.sample(range(MENU_CYCLE), count))


def aliased(waits):
    """Waits at or beyond one cycle: they repeat the phase of wait % MENU_CYCLE."""
    return [w for w in waits if w >= MENU_CYCLE]
