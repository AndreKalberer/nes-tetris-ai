# Tools

NES original-cartridge (level 255) work — see [docs/NES-255.md](../docs/NES-255.md):

| Tool | What it does |
|---|---|
| `run255.sh SEED [255\|511\|endless]` | Play one original-game attempt with the current best bot in MesenCE, then replay-verify it. |
| `run-score80.sh SEED [255\|511\|endless]` | The 80M score bot: 8-row tetris stack with 2-piece playouts. Needs 3 planner cores (default mask 13) and 1 emulator core, so one game per 4-core machine. |
| `run-score-vnet.sh SEED [255\|511\|endless]` | The 80M bot plus a learned leaf value (`value-net-v3.npz`) at levels 176-243 while the stack is at most 6 rows. Same cores as `run-score80.sh`. |
| `run-score-ff.sh SEED [255\|511\|endless]` | The value-net bot with its first input on the spawn frame (`NES_FIRST_FRAME=1`, `NES_SPAWN_SETTLE=0`) and a 9-row tetris stack. Same cores as `run-score80.sh`. |
| `run-score-wide.sh SEED [255\|511\|endless]` | `run-score-ff.sh` with tetris mode also at levels 159-167, 174-175 and 244-248 (no lowstack 246-249 zone). Same cores as `run-score80.sh`. |
| `run-score-holes.sh SEED [255\|511\|endless]` | `run-score-wide.sh` with the tetris-mode holes, hole_rows and covered weights doubled. Same cores as `run-score80.sh`. |
| `run-score-top.sh SEED [255\|511\|endless]` | `run-score-holes.sh` with tetris mode also at levels 250-252 and 254 and no Dellacherie 250-254 zone. Same cores as `run-score80.sh`. |
| `run-score-start.sh SEED [255\|511\|endless]` | `run-score-top.sh` with tetris mode also at the start levels 18-28. Same cores as `run-score80.sh`. |
| `run-score-safe157.sh SEED [255\|511\|endless]` | `run-score-start.sh` with `NES_RISK_BUDGET=17:.9,14:.5`: no risky crash-zone clears below a 14-row stack, which removes most level-157 deaths. Same cores as `run-score80.sh`. |
| `run-score-lowtop.sh SEED [255\|511\|endless]` | `run-score-safe157.sh` with an 8-row tetris stack (instead of 9) at levels 240-255, set by `alt_below_levels` in the weights file. Fewer top-outs near the end of a lap, at about 0.4M per lap less. Same cores as `run-score80.sh`. |
| `run-score-v8.sh SEED [255\|511\|endless]` | `run-score-mid.sh` with leaf value net v8b (rollout-averaged labels) at levels 18-153 and 176-243 up to a 9-row stack. Same cores as `run-score80.sh`. |
| `run-score-mid.sh SEED [255\|511\|endless]` | `run-score-lowtop.sh` with tetris mode also at levels 151-153, capped at a 6-row stack there (`alt_below_levels`) so the bot reaches the 154-158 zone low. Simulator: about +0.9M per lap against `run-score-lowtop.sh`. Same cores as `run-score80.sh`. |
| `value_net/gen.py`, `value_net/train.py` | Simulated 1G trajectories for value-net training, and the trainer that exports the `.npz` net (needs PyTorch). |
| `run-score50.sh SEED [255\|511\|endless]` | Same as `run255.sh` with the 50M score bot (CEM tetris weights, 3rd-piece expectation, no spawn wait). |
| `batch255.py` | Run a fixed list of seeds a few at a time with one launcher (status in `batch-status.json`). |
| `zone_sim.py` | Crash-zone simulator: plays levels 150–175 / 246–255 (both laps) with the real decision code; can start from a real board and piece sequence. `--stop-lines 3300` plays a whole lap; `--playout-top` turns on playouts; `--late-prob` makes a share of plans one frame late. |
| `tune_zone.py` | Tune zone weights on the crash-zone simulator. |
| `tune_low_stack_tetris.py` | Tune tetris-building weights used only while the stack is low (simulator). |
| `watch_replay.py` / `watch.cmd [speed] [record]` | Watch a recorded game in a Mesen window with an uncapped score / level / lines panel. |

Simulator tuning of the general evaluator: `python -m nes_original.tune` (tune / compare).

Older tools: `package_*.py` package checkpoints and releases; `verify_nes_reference.py` runs selected original 6502 routines (from the public disassembly) against the simulator.
