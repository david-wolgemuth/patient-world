#!/usr/bin/env python3
"""Stage and commit snapshot/state for a specific world."""
import argparse
import json
import subprocess
from pathlib import Path


def run(cmd, check=True):
    subprocess.run(cmd, check=check)


def add_existing(paths):
    existing = [str(path) for path in paths if path.exists()]
    if existing:
        run(["git", "add", *existing])


def main():
    parser = argparse.ArgumentParser(description="Commit README + world data after a tick")
    parser.add_argument("world", help="World name to commit (prod, staging, etc.)")
    parser.add_argument("--user", default="World", help="Git user.name to set before committing")
    parser.add_argument("--email", default="bot@example.com", help="Git user.email to set before committing")
    args = parser.parse_args()

    world_dir = Path("worlds") / args.world
    state_file = world_dir / "state.json"
    history_file = world_dir / "history.csv"
    snapshot_file = world_dir / "snapshot.md"

    missing = [p for p in (state_file, history_file, snapshot_file) if not p.exists()]
    if missing:
        raise SystemExit(f"Missing files for world '{args.world}': {', '.join(str(p) for p in missing)}")

    state = json.loads(state_file.read_text())
    day = state.get("day", 0)

    run(["git", "config", "user.name", args.user])
    run(["git", "config", "user.email", args.email])

    add_existing([Path("README.md"), state_file, history_file])
    run(["git", "add", "-f", str(snapshot_file)])

    diff = subprocess.run(["git", "diff", "--cached", "--quiet"])
    if diff.returncode == 0:
        print("No changes to commit")
        return

    commit_msg = f"[{args.world}] Day {day}"
    run(["git", "commit", "-m", commit_msg])


if __name__ == "__main__":
    main()
