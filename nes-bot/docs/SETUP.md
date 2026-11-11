# Setup

## Windows (Andre's PC)

1. Python 3.13. From the repository root: `.\nes-bot\setup.ps1` creates `.venv-original` with
   `nes-bot/requirements.txt` and runs the tests. Add `-Train` for PyTorch (only needed to train
   a new value net).
2. A dedicated portable [MesenCE 2.2.1](https://github.com/nesdev-org/MesenCE/releases/tag/2.2.1).
   Its folder must hold `settings.json` containing `{}`, `MesenCore.dll` and `MesenNesDB.txt`.
   Don't reuse a customised emulator profile: the bot freezes NTSC, zeroed power-on RAM and
   CPU/PPU alignment, and hashes the emulator files and the Lua bridge.
3. The game image comes from the installed `gym-tetris` package (USA, SHA-256
   `acab10f2dbad4d4ef5d56b31cd4cea208bb6e2e2c5dba5eb339d711ec04e3535`). No game image is in
   this repository. To use a copy elsewhere, set `NES_ROM_PATH`.

The launchers read three variables, or fall back to folders next to the repository:
`MESEN` (Mesen.exe), `PY` (the environment's python) and `JIT_DEPS` (a folder added to the
import path, for an isolated numba install; any folder works if numba is in `PY`).

```bash
sh nes-bot/tools/run-score-nextbox.sh 957
```

## Linux cloud machine (headless)

Build MesenCE 2.2.1 from source (needs `libsdl2-dev` and `dotnet-sdk-8.0`; about 10 minutes):

```bash
git clone --depth 1 --branch 2.2.1 https://github.com/nesdev-org/mesence && cd mesence
sed -i 's#https://nuget-feed-nightly.avaloniaui.net/v3/index.json;##' UI/UI.csproj   # if the nightly feed is blocked
make -j"$(nproc)"
mkdir -p ~/mesen && cp bin/linux-x64/Release/linux-x64/publish/* ~/mesen/ && echo '{}' > ~/mesen/settings.json
python3 -m venv ~/venv && ~/venv/bin/pip install numpy==2.2.6 numba==0.68.0 llvmlite==0.50.0 pytest
```

Then run with `MESEN=~/mesen/Mesen PY=~/venv/bin/python JIT_DEPS=~/jit NES_ROM_PATH=/path/Tetris.nes`.
The launcher's last two arguments are CPU masks (planner, emulator); on a 4-core machine use the
defaults for one game at a time.

## How a game is checked

Every game is replayed from boot in a fresh emulator from its recorded inputs. All 2 KiB of RAM,
the picture, CPU cycles and PPU/frame clocks must match exactly, and the level and line counters
are audited at every settled piece. A crash or a timeout never counts as a success. Re-check saved
games later with `python -m nes_original.verify_batch`.

The nes-py core (`env.OriginalGame`) is used only by the tests: it keeps executing after a CPU
JAM, so it can't certify late-game crashes or the 255 → 0 wrap.

Opt-in emulator tests:

```powershell
$env:NES_MESEN_EXE = 'C:/path/Mesen.exe'
python -m pytest -q nes-bot/tests -k mesen
```
