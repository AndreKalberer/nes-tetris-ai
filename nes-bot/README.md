# nes-bot

The bot that plays the original NES Tetris cartridge in MesenCE 2.2.1 with controller input
only. How it works: [docs/NES-255.md](docs/NES-255.md). Every verified game:
[docs/RESULTS-255.md](docs/RESULTS-255.md). Setup: [docs/SETUP.md](docs/SETUP.md).

| Path | Contents |
|---|---|
| [`nes_original/`](nes_original/README.md) | The bot: evaluator and simulator, crash model, controller, MesenCE driver, game runner. Weights and value nets in `nes_original/weights/`. |
| [`nes/`](nes/README.md) | The NES rules engine (`engine.py`, `actions.py`) that `nes_original` builds on. |
| [`tools/`](tools/README.md) | Launchers, batch runner, simulator, value-net training, replay viewer. |
| `tests/` | Tests, with the simulator goldens and crash-model reference tables in `tests/data/`. |
| `docs/` | How it works, results, setup. |
| `requirements.txt`, `requirements-train.txt`, `setup.ps1` | The Python environment (`setup.ps1 -Train` adds PyTorch for value-net training). |

Run everything from the repository root, for example:

```bash
sh nes-bot/tools/run-score-nextbox.sh 957 255
python nes-bot/tools/zone_sim.py --zone early --games 400 --output runs/zone-early.json
PYTHONPATH=nes-bot python -m nes_original.endurance --help   # or `pip install -e .` once
```

To freeze a bot version for a long experiment, copy this whole folder and run
`python -m nes_original.endurance ...` from inside the copy.
