# Tools

How the bot works: [docs/NES-255.md](../docs/NES-255.md). Run every tool from the repository root.

## Play on the real cartridge (MesenCE)

| Tool | What it does |
|---|---|
| `run-score-nextbox.sh SEED [255\|511\|endless]` | **The current score bot.** One original-game attempt in MesenCE, then replay verification. Tetris mode with playouts and the v8b leaf value net, first input on the spawn frame, crash-zone risk budget, and the next-box option (`NES_HIDE_BOX=1`: Select hides the next box before clears the crash model rates safer that way). Needs 3 planner cores (default mask 13) and 1 emulator core, so one game per 4-core machine. |
| `run255.sh SEED [255\|511\|endless]` | The survival bot (v8c): Dellacherie weights with next-piece search and crash avoidance, no score play. |
| `batch255.py` | Run a fixed list of seeds a few at a time with one launcher (status in `batch-status.json`). |
| `watch_replay.py` / `watch.cmd [speed] [record]` | Watch a recorded game in a Mesen window with an uncapped score / level / lines panel. |

Earlier score-bot launchers (score50 through score-v8) were removed in November 2026; their
weights files are still in `nes_original/weights/`, and the launchers are in git history
(for example `git show 6d85b58:nes-bot/tools/run-score-v8.sh`).

## Simulate and train

| Tool | What it does |
|---|---|
| `zone_sim.py` | Simulator with the real decision code. Plays the crash zones (levels 150–175, 246–255, both laps) or, with `--stop-lines 3300`, a whole lap; can start from a real board and piece sequence. `--playout-top` turns on playouts; `--late-table` replays measured late-plan rates. |
| `sim_golden.py` | Record or check the simulator regression goldens (`tests/data/sim_golden.json`). |
| `value_net/gen8.py`, `label8.py`, `train8.py` | Value-net pipeline: boards from simulated games, rollout-averaged labels (16 greedy 60-piece rollouts per board), and the trainer that exports the `.npz` net (needs `requirements-train.txt`). |
