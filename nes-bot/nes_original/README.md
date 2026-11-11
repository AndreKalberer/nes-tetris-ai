# nes_original: the bot

Everything here runs against the original, unmodified game. The bot reads the board, the
current and next piece and the counters from RAM (read-only), and plays with controller input.

| Module | Role |
|---|---|
| `endurance.py` | Command-line entry point (`python -m nes_original.endurance`, used by the launchers): builds the selector, plays the games and writes journals, protocol and status files. |
| `runner.py` | Plays one game per seed to the target level, audits the game's own counters, then replays the inputs in a fresh emulator and requires an exact match. |
| `mesen.py`, `mesen_bridge.lua` | MesenCE 2.2.1 driver: genuine menus, input per frame, read-only RAM, exact replay. |
| `env.py` | RAM layout, observations and the ROM check (SHA-256 `acab10f2…3535`); also a nes-py core used by the tests. |
| `feedback.py`, `planner.py` | Controller: lists reachable placements and turns the chosen one into timed button presses (30 taps a second). |
| `sim.py`, `fast.py` | Fast simulator and the evaluator: board features, tetris/burn/safe weights, playouts, value net (`TunedSelector`, `tuned_selector`). |
| `crash_model.py`, `crash_cycle_model.py`, `crash_alerts.py`, `dellacherie.py` | Crash avoidance from level 150: the crash-timing model, the per-move Down and Select (next-box) choices, and the risk budget (`CrashMapPrioritizer`). |
| `progression.py` | The game's exact level and line counter rules, including the 255 → 0 wrap. |
| `theoretical_score.py` | Uncapped score of a played game (the cartridge stops at 999,999). |
| `verify_batch.py` | Re-verify saved games in parallel; CPU-affinity helper. |
| `weights/` | Weights for each bot version and the value nets (`value-net-v8b.npz` is in use). |

Setup and emulator details: [../docs/SETUP.md](../docs/SETUP.md).
