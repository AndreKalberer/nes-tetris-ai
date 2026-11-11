# Documentation

Start with the [project README](../README.md). This page lists every document by topic.
All bot documents live under `nes-bot/`.

## NES Tetris on the original cartridge (current work)

| Document | What it covers |
|---|---|
| [NES-255.md](../nes-bot/docs/NES-255.md) | How the level-255 bot works, why level 255 is hard, how to run, watch and test it, known limits. |
| [RESULTS-255.md](../nes-bot/docs/RESULTS-255.md) | Every verified level-255 and rebirth game (bot version, seed, lines, uncapped score) and where games were lost. |
| [NES-ORIGINAL-REFERENCE.md](../nes-bot/docs/NES-ORIGINAL-REFERENCE.md) | The MesenCE 2.2.1 reference path: emulator setup, game image check, play / replay / train / compare commands. |
| [nes-bot/tools/README.md](../nes-bot/tools/README.md) | Launcher, batch runner, crash-zone simulator, tuners and replay viewer. |
| [nes-bot/nes_original/README.md](../nes-bot/nes_original/README.md) | The original-game environment adapter (nes-py core) and its fidelity limits. |
| [nes-bot/nes_original/ENDURANCE.md](../nes-bot/nes_original/ENDURANCE.md) | Development notes on long original-game runs toward level 255. |
| [nes-bot/nes_original/LOOKAHEAD.md](../nes-bot/nes_original/LOOKAHEAD.md) | Faster legal controls and visible-next search (first level-29 clear). |
| [nes-bot/nes_original/TRAINING.md](../nes-bot/nes_original/TRAINING.md) | Original-game level-29 training experiments. |

## Rules engine

| Document | What it covers |
|---|---|
| [nes-bot/nes/README.md](../nes-bot/nes/README.md) | The NES rules engine the bot builds on, and how to check it against the original 6502 routines. |
| [nes-bot/nes/RULES.md](../nes-bot/nes/RULES.md) | The engine's mechanics, sources and fidelity gaps. |

The nes-py core was later found to keep executing after a CPU JAM instruction, so late-game
crash and rebirth results are only claimed from the MesenCE reference path.

## History and evidence

- [../progress.md](../progress.md) — the dated, unedited development log (newest first). It
  stays at the repository root because some experiment scripts update it in place.
- Retained result files, protocols and audits: [nes-bot/evidence/](../nes-bot/evidence/)
  (NES reference, crash-model research tables, original-game learning experiments).
- Earlier bots (the Offline Sprint modern-rules game and its learned DQN bot, the first
  Stable-Baselines3 bot, and the NES simulator learning pilot) were removed in November 2026.
  Their code, documents and evidence are in git history up to commit `6d85b58`.
