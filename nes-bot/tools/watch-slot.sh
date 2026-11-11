#!/bin/sh
# One live, uncapped Orcacle game in a Mesen window, with a checkpoint every 5 minutes.
#   sh nes-bot/tools/watch-slot.sh SEED PLANNER_MASK EMULATOR_MASK MESEN_EXE
# If runs/watch-live/seed<SEED> already holds a checkpoint (PC shut down, window closed, crash),
# the game continues from it as a new part; once it has ended (DONE) nothing is started.
# Same bot settings as run-score-nextbox.sh; the pause/resume code is the cloud run's (tools/live_resume).
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
NES="$ROOT/nes-bot"; W="$NES/nes_original/weights"
SEED=${1:?seed}; PM=${2:?planner mask}; EM=${3:?emulator mask}; MESEN=${4:?Mesen.exe copy}
PY=${PY:-"$ROOT/../nes-original-env/.venv/Scripts/python.exe"}
JIT_DEPS=${JIT_DEPS:-"$ROOT/../nes-lookahead-deps"}
export RESUME_DIR="$ROOT/runs/watch-live/seed$SEED"; mkdir -p "$RESUME_DIR"
[ -f "$RESUME_DIR/DONE" ] && { echo "seed $SEED already finished"; exit 0; }
K=1; while [ -e "$RESUME_DIR/part$K" ]; do K=$((K+1)); done
cd "$ROOT"
export PYTHONPATH="$NES" NES_HIDE_BOX=1 NES_FIRST_FRAME=1 NES_SPAWN_SETTLE=0 NES_RISK_BUDGET=17:.9,14:.5
export NUMBA_CACHE_DIR=${NUMBA_CACHE_DIR:-"$ROOT/.numba-cache/settle0"} NUMBA_NUM_THREADS=${NUMBA_NUM_THREADS:-3}
export NES_MESEN_WINDOW=1 SLOT=$SEED
exec "$PY" "$NES/tools/live_resume/play_resume.py" --output "$RESUME_DIR/part$K" --mesen "$MESEN" --jit-deps "$JIT_DEPS" \
  --selector tuned-crash-map --weights dellacherie --beam 5 --reaction-frames 0 --late-plan retarget \
  --alt-weights "$W/v8-wide154.json" --seeds "$SEED" --endless --max-frames 100000000 --process-timeout 1209600 \
  --zone-weights "$W/nosingles-156-158.json" --zone-levels 300 300 --zone-ban 2 --zone-expect 4 \
  --extra-zone "$W/dellacherie.json" 168 172 28 2 --extra-zone "$W/dellacherie.json" 173 173 4 2 \
  --cpu-mask "$PM" --emulator-cpu-mask "$EM" --transport pipe-blocking --verification-transport pipe \
  --nonactive-input neutral --stall-rescue-input a --stall-rescue-after 120 --stall-rescue-fallback right \
  --stall-rescue-primary-frames 8 --stall-grace-frames 2400 \
  --no-softdrop-levels $(seq 155 248) 250 251 252 254
