# How work gets into this repository

This page is the house system for branches, pull requests, merges and documentation. It
applies to anyone (person or Claude) adding work.

## 1. Where new work goes

All bot code lives in `nes-bot/`. Put new files next to the code they belong to.

| You are adding | Put it in |
|---|---|
| NES bot logic (planner, evaluator, crash model, controller, endurance runner) | `nes-bot/nes_original/` |
| NES rules engine changes | `nes-bot/nes/` |
| Tuned weights for the NES bot | `nes-bot/nes_original/weights/` (one JSON per weight set, named by what it is for, e.g. `tetris-lowstack-r0.json`) |
| Launchers, simulators, tuners, batch runners for the NES bot | `nes-bot/tools/` (add a line to `nes-bot/tools/README.md`) |
| Value-net data and training scripts | `nes-bot/tools/value_net/` |
| Tests | `nes-bot/tests/` |
| Docs about the bot | `nes-bot/docs/` or a folder README |
| Small retained result files (protocols, summaries, research tables) | `nes-bot/evidence/<topic>/` |
| Docs about the whole project | the root `README.md` or `docs/` |

Never commit: `runs/` (game output, logs), game images (`*.nes`), large checkpoints
(`*.pt`), API keys or `.env` files. `runs/` lives at the
repository root and stays untracked.

**One launcher per bot version that is in use.** When a new score-bot version replaces the
current one, its launcher replaces the old launcher in `nes-bot/tools/` (git history keeps
the old one). Weights files stay: each one is the record of a version, and the tests check
how each differs from the one before.

## 2. Branches

- Never commit to `main` directly. One branch per goal, made from the latest `main`.
- Name: `<area>/<short-topic>`, lowercase with hyphens. Areas used so far:

| Area | For |
|---|---|
| `score/` | score and rebirth work on the NES bot |
| `nes/` | other NES bot features (evaluator, crash zones, controller) |
| `fix/` | bug fixes |
| `perf/` | speed-ups with no behaviour change |
| `tests/` | tests only |
| `docs/` | documentation only |
| `cloud/` | running on cloud machines (Linux, headless MesenCE) |
| `repo/` | layout, tooling, CI, this file |

Examples: `score/third-piece-expectimax`, `fix/keep-late-plan`, `repo/bot-folders`.

## 3. Pull requests

- **One goal per PR.** If a PR needs a cleanup first, open the cleanup as its own PR.
- **Moves separate from edits.** When moving or renaming files, put the pure moves in one
  commit and the edits in another, so git can follow every file through a rebase.
- **Fill in the template** (`.github/pull_request_template.md`): what, why, results with their
  source, checklist, overlaps.
- **Results language.** Say "sim" for simulator estimates and "verified" only for real MesenCE
  games that replayed exactly. A goal counts as reached only after both.
- **Tests.** Run `python -m pytest -q` from the repository root before opening the PR. If
  simulator behaviour changes on purpose, check the survival floors first
  (`SIM_FULL_BASELINE=1`, about 10 minutes), then re-record the goldens with
  `python nes-bot/tools/sim_golden.py --write` in the same PR, and say so in the PR.
- **Draft PRs** are fine for work that still needs real-game checks; mark ready when done.

## 4. Merging

- Andre merges on GitHub with **"Create a merge commit"** (not squash or rebase), so each
  PR's commits, including file moves, stay intact in history.
- **Order when PRs overlap:** merge the one whose results are ready first. Every other open PR
  then updates from `main` (`git fetch origin && git rebase origin/main`, or merge `main` in)
  and re-runs the tests before it is merged.
- Delete the branch on GitHub after the merge (the button on the merged PR).
- After merging, everyone's local checkout updates with `git pull` on `main`.

## 5. Keeping the README and docs current

Update in the same PR as the change, not later:

| When | Update |
|---|---|
| New verified NES games (level 255, rebirth, score) | `nes-bot/docs/RESULTS-255.md` (bot version, seed, lines, uncapped score) |
| A new headline result is verified | the "Headline results" table in the root `README.md` |
| New file or folder in a bot | that bot folder's `README.md` table |
| New tool | `nes-bot/tools/README.md` |
| How the bot works changed | `nes-bot/docs/NES-255.md` |
| Any notable step | a dated line at the top of `progress.md` |

The root README keeps only verified results and the folder map; details go in the bot folders.

## 6. Pushing from Andre's PC

Cloud sessions without GitHub access hand over a patch file; Andre pushes it from his PC.
Use a separate worktree so the main checkout (and any paused runs in `runs/`) is never
switched to another branch:

```powershell
cd C:\Users\andre\Documents\Projects\Tetris\work\Tetris-rl-dqn
git fetch origin
git worktree add ..\Tetris-rl-dqn-pr -b <area>/<topic> origin/main
cd ..\Tetris-rl-dqn-pr
git am -3 <path-to>\change.patch
git push -u origin <area>/<topic>
gh pr create --fill --base main
cd ..\Tetris-rl-dqn
git worktree remove ..\Tetris-rl-dqn-pr
```

After the PR is merged on GitHub, update the main checkout:

```powershell
cd C:\Users\andre\Documents\Projects\Tetris\work\Tetris-rl-dqn
git pull origin main
```

## 7. Running code

`nes-bot/` is the import root. The launchers and `pytest.ini` set the path themselves.
For hand-typed `python -m ...` commands, run once per Python environment, from the
repository root: `python -m pip install -e .` (or set `PYTHONPATH=nes-bot`). A frozen copy of
the bot is just a copy of `nes-bot/`; run `python -m nes_original.endurance ...` from inside
the copy.
