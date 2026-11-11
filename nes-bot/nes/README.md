# nes: the NES rules engine

A Python model of Nintendo's NTSC A-Type Tetris rules: piece geometry and spawn
orientations, gravity per level, the piece randomizer, and the legal timed inputs
(`engine.py`, `actions.py`, `fast_paths.py`). The bot in `../nes_original/` imports these
tables and rules; the real game runs in MesenCE. See [RULES.md](RULES.md) for the exact
mechanics, the reference disassembly revision and the known fidelity gaps.

This engine is a model, not an emulator. Results only count when played on the original
cartridge in MesenCE and replay-verified.

## Independent routine validation

Optional developer validation uses py65 separately from the normal runtime:

```powershell
.\.venv\Scripts\python.exe -m pip install -r nes-bot/requirements-nes-validation.txt
.\.venv\Scripts\python.exe nes-bot/tools/verify_nes_reference.py --reference-dir PATH_TO_REFERENCE --cases 3000 --output runs/nes-reference-check.json
```

Supply `main.asm` and `constants.asm` from the pinned public disassembly revision
linked in RULES.md. The verifier checks their hashes first. It compares all 19
geometries and the rotation/spawn/gravity tables, plus 3,000 piece draws and
3,000 active control states against selected 6502 routines assembled in memory.
It does not certify the complete frame scheduler, ROM, PPU or late-game behavior.
