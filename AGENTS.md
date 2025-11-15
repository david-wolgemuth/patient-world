# Patient World – Agent Handbook

## Project Overview
Patient World is a minimal autonomous ecosystem sim. `sim.py` holds the entire loop: load JSON state, run `tick`, persist state, and optionally append prod history. GitHub Actions ticks prod daily at 12:00 UTC, committing `state_prod.json`, `history.csv`, `snapshot.md`, and README updates generated from the latest state.

## Knowledge Base (Basic Memory)
- Location: `docs/`
- Structure: folders such as `vision/` (project goals, constraints, architecture) and `agents/` (meta guides).
- Helpful entries:
  - `docs/vision/Preferred Development Approach.md`: iteration style, tooling, and guardrails.
  - `docs/agents/Basic Memory Usage.md`: CLI usage, project configuration, and observations.
  - `docs/agents/Beads Workflow Guide.md`: how to structure and size tasks in Beads.

Use `/Users/david/.local/bin/bm tool ... --project patient-world` to edit or read these notes. Snapshot markers in README reference `snapshot.md`, which is produced via `python sim.py --dev --snapshot`.

## Work Tracking (Beads)
- Example Recent epic: `[M][snapshot][automation] README Snapshot Publishing Epic` (closed) with child tasks for sim changes, README updates, workflow wiring, gitignore, and testing instructions.
- Create tasks with `bd create --title "[size][tags] Name" --type task` and link dependencies via `--parent`.

## Quick Start for Agents
1. Read `README.md` for snapshot/testing commands.
2. Review `docs/vision/` to understand constraints before proposing changes.
3. Check Beads (`bd list`) for open issues; size/tag new work accordingly.
4. Implement in `sim.py` + supporting scripts, keeping prod/dev separation and automation intact.
5. Update knowledge base entries if process rules change (e.g., new folders, tools).
