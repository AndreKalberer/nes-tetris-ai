# nes-bot

The bot that plays the original NES Tetris cartridge in MesenCE 2.2.1 with controller input
only. How it works: [docs/NES-255.md](docs/NES-255.md). Every verified game:
[docs/RESULTS-255.md](docs/RESULTS-255.md).

| Path | Contents |
|---|---|
| [`nes_original/`](nes_original/README.md) | The bot: MesenCE and nes-py adapters, Lua bridge, planner and evaluator (`sim.py`, `fast.py`), crash model, controller, game runner (`endurance.py`), replay and verification. Weights and value nets in `nes_original/weights/`. |
| [`nes/`](nes/README.md) | The NES rules engine (`engine.py`, `actions.py`) that `nes_original` builds on. |
| [`tools/`](tools/README.md) | Launchers, batch runner, crash-zone simulator, tuners, value-net training, replay viewer. |
| `tests/` | Tests, including the simulator regression goldens in `tests/data/`. |
| `docs/` | How it works, results, the MesenCE reference setup. |
| `evidence/` | Retained result files, protocols and research tables. |
| `requirements-nes*.txt`, `setup-nes-original.ps1` | Environments. |

Run everything from the repository root, for example:

```bash
sh nes-bot/tools/run-score-nextbox.sh 957 255
python nes-bot/tools/zone_sim.py --zone early --games 400 --output runs/zone-early.json
PYTHONPATH=nes-bot python -m nes_original.endurance --help   # or `pip install -e .` once
```

To freeze a bot version for a long experiment, copy this whole folder and run
`python -m nes_original.endurance ...` from inside the copy.
