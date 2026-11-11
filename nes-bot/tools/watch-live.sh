#!/bin/sh
# Watch Orcacle play one live game in a normal Mesen window at real NES speed (60 fps).
#   sh nes-bot/tools/watch-live.sh [SEED] [TARGET]   (default seed 300 = 5 s on the level menu)
# Same bot and settings as run-score-nextbox.sh. The window attaches its script just after
# power-on, so this game is for watching only: its fresh replay check will not match.
# Closing the Mesen window ends the game.
export NES_MESEN_WINDOW=1
exec sh "$(dirname "$0")/run-score-nextbox.sh" "${1:-300}" "${2:-255}"
