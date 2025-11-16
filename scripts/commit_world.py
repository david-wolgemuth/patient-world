#!/usr/bin/env python3
"""Stage and commit README + world data for a world."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core import repository


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Commit world data via git")
    parser.add_argument("world", help="World name to commit")
    parser.add_argument("--user", default="World", help="Git user.name")
    parser.add_argument("--email", default="bot@example.com", help="Git user.email")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    paths = repository.get_paths(args.world)
    required = [paths.state, paths.history, paths.snapshot]
    missing = [p for p in required if not p.exists()]
    if missing:
        raise SystemExit(f"Missing files for world '{args.world}': {', '.join(str(p) for p in missing)}")

    with paths.state.open() as fh:
        state = json.load(fh)
    day = state.get("day", 0)

    subprocess.run(["git", "config", "user.name", args.user], check=True)
    subprocess.run(["git", "config", "user.email", args.email], check=True)
    subprocess.run(["git", "add", "README.md", str(paths.state), str(paths.history)], check=True)
    subprocess.run(["git", "add", "-f", str(paths.snapshot)], check=True)

    if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode == 0:
        print("No changes to commit")
        return 0

    subprocess.run(["git", "commit", "-m", f"[{args.world}] Day {day}"], check=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
