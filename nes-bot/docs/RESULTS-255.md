# Verified original-cartridge results

Every game below started at level 18 through the real menus with controller input only and was
replayed in a fresh MesenCE process from its recorded inputs, matching RAM, picture, clocks and
result exactly (`case_state: verified`). Seed = frames waited on the menu. Uncapped score =
`nes_original/theoretical_score.py` (the cartridge itself shows 999,999).

## Rebirth (level 255, wrap to 0, back to level 255)

| Bot | Seed | Absolute level | Lines | Uncapped score |
|---|---|---|---|---|
| v8b | 19211 | 511 | 6,651 | 43,047,996 |

## Score bot (level 255, score per lap)

| Bot | Seed | Lines | Uncapped score | Tetrises |
|---|---|---|---|---|
| score50 (`run-score50.sh`) | 957 | 3,290 | 58,187,903 | 185 |
| score50 (`run-score50.sh`) | 24340 | 3,290 | 55,723,090 | 190 |
| score80 (`run-score80.sh`) | 957 | 3,290 | 79,973,267 | 328 |
| score80 (`run-score80.sh`) | 15868 | 3,291 | 80,891,827 | 328 |
| score-vnet (`run-score-vnet.sh`) | 957 | 3,290 | 84,715,592 | 342 |
| score-vnet (`run-score-vnet.sh`) | 15868 | 3,290 | 81,917,158 | 343 |
| score-vnet (`run-score-vnet.sh`) | 24340 | 3,291 | 86,308,391 | 358 |
| score-ff (`run-score-ff.sh`) | 957 | 3,290 | 85,992,961 | 372 |
| score-ff (`run-score-ff.sh`) | 15868 | 3,290 | 86,068,887 | 359 |
| score-ff (`run-score-ff.sh`) | 24340 | 3,290 | 85,957,911 | 356 |
| score-wide (`run-score-wide.sh`) | 957 | 3,291 | 89,517,690 | 374 |
| score-wide (`run-score-wide.sh`) | 15868 | 3,290 | 90,311,839 | 378 |
| score-wide (`run-score-wide.sh`) | 24340 | 3,290 | 91,126,229 | 379 |
| score-holes (`run-score-holes.sh`) | 957 | 3,291 | 93,973,742 | 408 |
| score-holes (`run-score-holes.sh`) | 15868 | 3,290 | 90,516,059 | 386 |
| score-holes (`run-score-holes.sh`) | 24340 | 3,290 | 91,604,910 | 392 |
| score-top (`run-score-top.sh`) | 957 | 3,290 | 96,306,150 | 419 |
| score-top (`run-score-top.sh`) | 15868 | 3,290 | 93,717,958 | 402 |
| score-top (`run-score-top.sh`) | 24340 | 3,292 | 88,316,463 | 373 |
| score-start (`run-score-start.sh`) | 957 | 3,291 | 93,209,648 | 427 |
| score-start (`run-score-start.sh`) | 15868 | 3,293 | 97,029,860 | 450 |
| score-start (`run-score-start.sh`) | 24340 | 3,290 | 92,280,091 | 430 |
| score-safe157 (`run-score-safe157.sh`) | 957 | 3,291 | 93,173,075 | 433 |
| score-safe157 (`run-score-safe157.sh`) | 15868 | 3,293 | 96,176,174 | 450 |
| score-safe157 (`run-score-safe157.sh`) | 24340 | 3,291 | 95,253,832 | 437 |
| score-lowtop (`run-score-lowtop.sh`) | 957 | 3,290 | 93,217,055 | 428 |
| score-lowtop (`run-score-lowtop.sh`) | 15868 | 3,291 | 93,692,075 | 431 |
| score-lowtop (`run-score-lowtop.sh`) | 24340 | 3,290 | 88,374,750 | 408 |
| score-mid (`run-score-mid.sh`) | 957 | 3,291 | 94,045,717 | 433 |
| score-mid (`run-score-mid.sh`) | 15868 | 3,291 | 95,733,899 | 438 |
| score-mid (`run-score-mid.sh`) | 24340 | 3,292 | 92,823,256 | 421 |
| score-v8 (`run-score-v8.sh`) | 957 | 3,291 | 99,077,124 | 476 |
| score-v8 (`run-score-v8.sh`) | 15868 | 3,292 | 101,332,409 | 476 |
| score-v8 (`run-score-v8.sh`) | 24340 | 3,291 | 101,979,820 | 489 |
| score-v8 (`run-score-v8.sh`) | 7 | 3,291 | 97,304,200 | 473 |
| score-v8 (`run-score-v8.sh`) | 100 | 3,290 | 103,115,310 | 493 |
| score-v8 (`run-score-v8.sh`) | 200 | 3,292 | 103,426,918 | 497 |

All played headless on a Linux cloud machine; the uncapped score matched the real counter at
every check (0 mismatches). A third score80 game (seed 24340) topped out at level 235 with
52,874,509; the simulator, given the same pieces, makes the same 6,458 placements and tops out
at the same point.
The score-vnet bot (learned leaf value, gated) reached level 255 on all three seeds, including
24340. Simulator: 82.4M per lap with 98/100 laps survived (score80 on the same 100 laps: 80.4M, 98/100).
The score-ff bot (first input on the spawn frame, 9-row stack) reached level 255 on all three
seeds with 0 target misses; every piece took the first-frame path. Simulator: 86.1M per lap
with 74/75 laps survived (score-vnet on the same 75 laps: 83.5M, 75/75).
The score-wide bot (tetris mode also at 159-167, 174-175 and 244-248) reached level 255 on all
three seeds with 0 target misses. Simulator: 89.7M per lap with 75/75 laps survived.
The score-holes bot (tetris-mode hole weights doubled) reached level 255 on all three seeds
with 0 target misses, beating score-wide on each seed. Simulator: about 92.0M per lap with
100/100 laps survived (score-wide on the same 100 laps: 89.6M).
The score-top bot (tetris mode also at 250-252 and 254) reached level 255 on all three seeds
with 0 target misses, averaging 92.8M (score-holes on the same seeds: 92.0M). Simulator:
about +1.45M per lap over score-holes, and 35/40 five-lap games survived (score-holes 32/40).
The score-start bot (tetris mode also at levels 18-28) reached level 255 on all three seeds
with 0 target misses, averaging 94.2M (score-top on the same seeds: 92.8M).
The score-safe157 bot (no risky crash-zone clears below 14 rows) averaged 94.9M on the same
three seeds with 0 target misses. Its first seed-957 attempt crashed at level 253 with a
15-row stack after a drought (verified replay, 3,273 lines, 93.4M). The rerun above reached 255.
The score-lowtop bot (8-row stack at 240-255) reached level 255 on all three seeds with 0 target
misses, averaging 91.8M. Real games are not paired: planning time shifts the frame on which each
piece locks, and the NES picks pieces by frame, so the games differ from the first pieces on and
three games cannot measure a 0.4M change. The sim estimate above (-0.37M per lap, 97.6% vs 96.0%
of laps survived) is the comparison to use.
The score-mid bot (tetris mode also at 151-153, 6-row stack there) reached level 255 on all three
seeds with 0 target misses, averaging 94.2M. Sim, 100 paired one-lap seeds against score-lowtop:
+0.90 ±0.32M per lap, 97/100 vs 98/100 laps survived (the extra deaths are at levels 194 and 235).
The score-v8 bot (value net v8b at levels 18-153 and 176-243 up to a 9-row stack) reached level
255 on all six seeds with 0 target misses, averaging 101.04M (score-mid on 957, 15868 and 24340:
94.2M), with 473-497 tetrises per game. Planning is slower (about 7,000 of 8,230 plans overran
the frame budget and were retargeted, against about 1,900 before), but no target was missed
and at most 2 plans per game changed board.

## Level 255

| Bot version | Seed | Lines | Uncapped score |
|---|---|---|---|
| crash-map-v5 | 129 | 3,290 | 22,219,561 |
| crash-map-v5 | 145 | 3,290 | 22,302,336 |
| crash-map-v5 | 177 | 3,290 | 22,479,627 |
| v7 | 49 | 3,290 | 22,374,551 |
| v7 | 193 | 3,290 | 22,529,980 |
| v7 | 209 | 3,290 | 22,454,000 |
| v7 | 225 | 3,290 | 22,453,239 |
| v7-test25 | 10329 | 3,290 | 22,128,474 |
| v7-test25 | 19211 | 3,290 | 22,247,779 |
| v7-test25 | 26300 | 3,290 | 22,526,987 |
| v7-test25 | 27885 | 3,290 | 22,252,154 |
| v7-test25 | 30418 | 3,290 | 22,330,550 |
| v8 | 13858 | 3,290 | 22,374,633 |
| v8b | 8600 | 3,290 | 22,311,367 |
| v8b | 10298 | 3,290 | 22,301,265 |
| v8b | 29716 | 3,290 | 22,505,255 |
| v8b | 30189 | 3,290 | 22,405,322 |
| v8b | 30804 | 3,290 | 22,127,456 |
| v8c | 5700 | 3,290 | 22,380,135 |
| v8c | 17452 | 3,290 | 22,369,620 |

20 games; uncapped score mean 22,353,715 (range 22,127,456–22,529,980).

## Where games were lost (versions v5 and later)

Most losses were top-outs at levels 157–158, where every single carries at least 25% crash
risk; earlier versions also lost games at 169–170 (singles only) and to pushdown crashes at 249.
Two v8 games lost to a one-off 2.4 s compile stall at level 156 (fixed in v8c). Run folders
(`runs/`, not in git) hold every case, including failures, with their verification status.
