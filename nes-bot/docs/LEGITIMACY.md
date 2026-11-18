# Legitimacy rule and what the Mesen bot may see

Rule (Andre, 2026-11-17): anything a regular player can't see on screen must not be available to the bot.

## Fair-play rules (binding for all future work, Andre 2026-11-18)

Every change to the bot, the bridge, the simulators or the result tools must follow these. **If a change is not
clearly allowed, ask Andre before building it.**

1. **Next piece only from screen pixels.** NEXT comes from the drawn NEXT box (`mesen_bridge.lua` pixels,
   `preview.py`), never from RAM `$BF` or any other byte.
2. **Board, piece, level, lines, score from RAM only with a 1-frame delay**, so the bot acts only on the state the
   picture shows (`NES_PICTURE_DELAY=1`). The current frame of the falling piece may be predicted from that state
   plus the bot's own last input.
3. **No RNG or hidden bytes.** No RNG state, no hidden timers (rebuild them from own inputs), no other RAM a player
   cannot see. **No prediction of real future pieces** and **no drought rules**. Weighting by the game's fixed,
   published randomizer odds is allowed.
4. **No RAM or ROM writes.** Savestates only as crash checkpoints for long runs (resume after a machine restart),
   never to retry or undo a game outcome.
5. **Allowed:** the Select trick (hiding the NEXT box) as long as it never reveals a piece that would otherwise be
   hidden; reading faint pixels on glitched late-level palettes; up to 30 taps per second.
6. **Results count only if replay-verified** (fresh exact replay from power-on). Numbers from before these fixes
   (PR #33 and the 1-frame delay) are upper bounds, not current results.

## Fixed after the 2026-11-15 external audit

| Finding | Fix |
|---|---|
| Next piece read from RAM `$BF` 1 frame (ordinary play) / 2 frames (Select hide/show) before it is drawn | The bridge samples the **drawn NEXT box** (`mesen_bridge.lua`, all 32x32 pixels of the last completed frame; lit = RGB sum > 12, so the glitched palettes of levels 146/148/160 still read) and `nes_original/preview.py` classifies the shape. `$BF` is no longer read by the policy path. The preview is reported as `-1` while the box is blank (hidden with Select) and on the frame a piece first appears (the picture is still the old one). After 12 unreadable frames the controller plans one-ply without NEXT (the selector no longer treats `-1` as an I piece). In the seed-957 games unreadable pictures appeared only during line clears at level 160, never as a misread. In the Select branch it now presses Select and waits for the box to be drawn **before** planning. |
| Hidden timers `$65 $66 $6E $6F` (and `$B6`) passed to the policy | Rebuilt by `nes_original/timers.py` from the bot's own inputs plus visible board/piece/level, using the same frame rules as `nes.engine.control_frame`. RAM is not read for them. Check: 0 mismatches against real RAM on 6,862 active frames of 9 random-input games (levels 0, 9, 17, 18, 19) and 353 more live frames; `tests/test_nes_timers.py` replays a committed 2,785-frame recording. |
| Menu delay sampling bias (waits 0..32766 vs a 7,598-phase cycle) | `nes_original/menu_cycle.py` gives `uniform_menu_waits()` (one cycle, uniform). `endurance.py` warns on waits >= 7598. The 7,598 figure is the auditor's measurement and was not re-measured here. |
| Checker trusted the claimed goal / start frame, overwrote diagnostics | The audit's `independent-audit/verify.py` is not in this repo, so it was not edited. The repo's own `verify_batch.py` now takes `--goal-level`, enforced on the **replayed** state (never read from the proof), and keeps the full traceback per failed proof. `load_replay` already rebuilds the start frame from the inputs and compares it. |

## Spawn-frame move (NES_BLIND_FIRST=1, on in run-score-nextbox.sh)

Waiting for the drawn NEXT box puts the first input 1 frame after spawn (2 after a hide). At 1G that cost a lot of survival:
5-lap sim on the same 31 seeds (`/mnt/project-files/benchmark/`), deaths before 5 laps:

| Arm | Deaths | Points/lap |
|---|---|---|
| Old (first input on spawn frame, NEXT from RAM) | 2/31 | 87.6M |
| Wait 1 frame for NEXT (`NES_SPAWN_SETTLE=1`) | 13/31 | 88.8M |
| Spawn-frame move from the current piece only, then replan with NEXT | 5/31 (1 is a level-255 crash) | 88.1M |

The spawn-frame move uses only what is on screen at that frame (the board and the falling piece, which was already shown
in NEXT the turn before). It plans one-ply, plays that plan's first input, and replans with NEXT once it is drawn,
continuing the same button schedule (`ActionRules.start_frame`; restarting the schedule loses tap/rotation frames and
killed 29/31 sim games). Launcher projections use `NES_SPAWN_SETTLE=0` again.

Real games, seed 957 to level 255 on the screen-only bridge: with the 1-frame wait, alive, replay verified (exact RAM +
picture, 0 target misses). With the spawn-frame move: alive, 8,230 pieces, every piece replanned with NEXT (0 unresolved), replay verified,
but 97 pieces (1.2%) landed off target: when the blind plan kept the spawn pose the controller started dropping on
frame 0 and kept dropping after the replan chose another spot. Fixed (the replan clears the drop flag;
`test_blind_spawn_pose_then_move_still_lands_on_target`). `NES_MISS_LOG=path` writes each target miss as it happens.

## One-frame delay (NES_PICTURE_DELAY=1, on in run-score-nextbox.sh)

Audit 2 measured that the picture shows exactly what RAM held one frame earlier (2,877/2,877 active frames). Andre
chose option (b): observations are built from the previous poll's RAM (the frame on screen), and the falling
piece's current frame is predicted with `nes.engine.control_frame` from that state plus the bot's last input
(`nes_original/mesen.py` `_observe_shown`; `NES_PREDICTION_LOG` records any frame where the prediction differs).
A new piece is seen one frame after it spawns, so the first input comes 1 frame after spawn, the same as the
"wait 1 frame" sim arm above (13/31 deaths in 5 laps vs 5/31 for the spawn-frame move). Andre accepted this cost.

## Still open (not fixed here, do not overstate)

- The older nes-py path (`nes_original/env.py`, `OriginalGame`) still reads `$BF` and the timers from RAM. It is a development/simulation backend, not the Mesen gameplay path; do not use it for legitimacy claims.
- Board, active piece pose, level, lines and score are still read from RAM. They are drawn on screen, but RAM can lead the picture by a frame or two (the audit only measured the preview). Not audited here.
- The bridge still sends all 2 KB of RAM to the host process. Nothing in the Python policy path uses the hidden bytes, but this is not an OS-level isolation boundary.
- Real-time: Mesen waits for Python while it plans, so this is paused/instrumented play, not verified real-time play. The controller charges measured planning time as neutral frames in some paths only.
- Seed-160 result is unverified (replay did not reproduce the recorded final RAM/clock; root cause unknown).
- Replays recorded before this change use the old bridge and won't load (bridge identity changed). To re-verify old games (e.g. RESULTS-255), check out branch `pre-legitimacy-bridge` (the commit before this change) and run `verify_batch.py` there.
- `--goal-level` compares the game's level byte (0-255), so it cannot enforce a rebirth goal such as 511.
