# Legitimacy rule and what the Mesen bot may see

Rule (Andre, 2026-11-17): anything a regular player can't see on screen must not be available to the bot.

## Fixed after the 2026-11-15 external audit

| Finding | Fix |
|---|---|
| Next piece read from RAM `$BF` 1 frame (ordinary play) / 2 frames (Select hide/show) before it is drawn | The bridge samples the **drawn NEXT box** (`mesen_bridge.lua`, 16x16 samples of the last completed frame) and `nes_original/preview.py` classifies the shape. `$BF` is no longer read by the policy path. The preview is reported as `-1` while the box is blank (hidden with Select) and on the frame a piece first appears (the picture is still the old one). The controller waits for it, up to 12 frames, then fails loudly. In the Select branch it now presses Select and waits for the box to be drawn **before** planning. |
| Hidden timers `$65 $66 $6E $6F` (and `$B6`) passed to the policy | Rebuilt by `nes_original/timers.py` from the bot's own inputs plus visible board/piece/level, using the same frame rules as `nes.engine.control_frame`. RAM is not read for them. Check: 0 mismatches against real RAM on 6,862 active frames of 9 random-input games (levels 0, 9, 17, 18, 19) and 353 more live frames; `tests/test_nes_timers.py` replays a committed 2,785-frame recording. |
| Menu delay sampling bias (waits 0..32766 vs a 7,598-phase cycle) | `nes_original/menu_cycle.py` gives `uniform_menu_waits()` (one cycle, uniform). `endurance.py` warns on waits >= 7598. The 7,598 figure is the auditor's measurement and was not re-measured here. |
| Checker trusted the claimed goal / start frame, overwrote diagnostics | The audit's `independent-audit/verify.py` is not in this repo, so it was not edited. The repo's own `verify_batch.py` now takes `--goal-level`, enforced on the **replayed** state (never read from the proof), and keeps the full traceback per failed proof. `load_replay` already rebuilds the start frame from the inputs and compares it. |

## Still open (not fixed here, do not overstate)

- The older nes-py path (`nes_original/env.py`, `OriginalGame`) still reads `$BF` and the timers from RAM. It is a development/simulation backend, not the Mesen gameplay path; do not use it for legitimacy claims.
- Board, active piece pose, level, lines and score are still read from RAM. They are drawn on screen, but RAM can lead the picture by a frame or two (the audit only measured the preview). Not audited here.
- The bridge still sends all 2 KB of RAM to the host process. Nothing in the Python policy path uses the hidden bytes, but this is not an OS-level isolation boundary.
- Real-time: Mesen waits for Python while it plans, so this is paused/instrumented play, not verified real-time play. The controller charges measured planning time as neutral frames in some paths only.
- Seed-160 result is unverified (replay did not reproduce the recorded final RAM/clock; root cause unknown).
- Waiting for the picture costs 1 frame per piece (2 after a hide). The effect on score and survival has **not** been measured; all testing was paused.
- Replays recorded before this change use the old bridge and won't load (bridge identity changed). To re-verify old games (e.g. RESULTS-255), check out branch `pre-legitimacy-bridge` (the commit before this change) and run `verify_batch.py` there.
- `--goal-level` compares the game's level byte (0-255), so it cannot enforce a rebirth goal such as 511.
- Simulator/launchers still assume `NES_SPAWN_SETTLE=0`; the real controller now acts 1 frame after the piece appears (2 after a Select hide). Re-run the paired sim with the matching delay before quoting 101M / 98.5%.
