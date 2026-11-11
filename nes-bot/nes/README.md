# nes: the NES rules engine

A Python model of Nintendo's NTSC A-Type Tetris rules: piece geometry and spawn
orientations, gravity per level, the piece randomizer, and the legal timed inputs
(`engine.py`, `actions.py`, `fast_paths.py`). The bot in `../nes_original/` imports these
tables and rules; the real game runs in MesenCE. See [RULES.md](RULES.md) for the exact
mechanics, the reference disassembly revision and the known fidelity gaps.

This engine is a model, not an emulator. Results only count when played on the original
cartridge in MesenCE and replay-verified.
