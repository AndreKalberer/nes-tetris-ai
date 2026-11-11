#!/bin/sh
# Watch several live Orcacle games at once, each in its own Mesen window at real speed, tiled in a grid.
#   sh nes-bot/tools/watch-grid.sh [FIRST_SEED] [COUNT] [TARGET]   (defaults: 300, 4, endless = uncapped until death)
# Game i uses seed FIRST_SEED+i and 4 cores (3 planner + 1 emulator), so 16 threads fit 4 games.
# Each game gets its own Mesen copy (nes-late-fidelity/mesence-live<i>) with single-instance mode
# off; otherwise a new window hands its game to the first one and that game crashes.
# Games already running in a copy are left alone. Re-tile later with: powershell -File nes-bot/tools/tile-mesen.ps1
# Watching only: the windows attach just after power-on, so these games fail the fresh replay check.
ROOT=$(cd "$(dirname "$0")/../.." && pwd)
FIRST=${1:-300}; COUNT=${2:-4}; TARGET=${3:-endless}
BASE="$ROOT/../nes-late-fidelity/mesence-2.2.1"
i=0
while [ $i -lt "$COUNT" ]; do
  n=$((i+1)); COPY="$ROOT/../nes-late-fidelity/mesence-live$n"
  if [ ! -d "$COPY" ]; then
    cp -r "$BASE" "$COPY" && rm -rf "$COPY/SaveStates"
    echo '{"Preferences":{"SingleInstance":false}}' > "$COPY/settings.json"
  fi
  if tasklist //V //FI "IMAGENAME eq Mesen.exe" 2>/dev/null | grep -q . && \
     powershell -NoProfile -Command "@(Get-Process Mesen -EA 0 | ? Path -like '*mesence-live$n\*').Count" | grep -q '^[1-9]'; then
    echo "game $n already running in mesence-live$n, left alone"
  else
    SEED=$((FIRST+i)); C=$((i*4))
    PLANNER=$(( (1<<C) | (1<<(C+2)) | (1<<(C+3)) )); EMU=$((1<<(C+1)))
    echo "game $n: seed $SEED, log $ROOT/../watch-live-seed$SEED.log"
    NES_MESEN_WINDOW=1 MESEN="$COPY/Mesen.exe" nohup sh "$ROOT/nes-bot/tools/run-score-nextbox.sh" \
      "$SEED" "$TARGET" "$PLANNER" "$EMU" > "$ROOT/../watch-live-seed$SEED.log" 2>&1 &
  fi
  i=$n
done
echo "Waiting for the windows, then tiling them..."
sleep 60
powershell -NoProfile -ExecutionPolicy Bypass -File "$ROOT/nes-bot/tools/tile-mesen.ps1"
