#!/usr/bin/env python3
"""Helper script to bootstrap or clone world directories."""
import argparse
import json
import shutil
from pathlib import Path

DEFAULT_STATE = {"day": 0, "grass": 500, "rabbits": 50, "foxes": 10}
HISTORY_HEADER = "date,day,grass,rabbits,foxes"
WORLDS_DIR = Path("worlds")


def copy_file(src: Path, dest: Path):
    if src.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)


def write_default_files(world_dir: Path):
    state_file = world_dir / "state.json"
    history_file = world_dir / "history.csv"

    if not state_file.exists():
        state_file.write_text(json.dumps(DEFAULT_STATE, indent=2))
    if not history_file.exists():
        history_file.write_text(HISTORY_HEADER + "\n")


def main():
    parser = argparse.ArgumentParser(description="Create or clone a Patient World state directory")
    parser.add_argument("world", help="World name to create")
    parser.add_argument("--from", dest="source", help="Existing world to clone", metavar="WORLD")
    args = parser.parse_args()

    dest_dir = WORLDS_DIR / args.world
    dest_dir.mkdir(parents=True, exist_ok=True)

    if args.source:
        src_dir = WORLDS_DIR / args.source
        if not src_dir.exists():
            raise SystemExit(f"Source world '{args.source}' not found at {src_dir}")
        for filename in ("state.json", "history.csv", "snapshot.md"):
            copy_file(src_dir / filename, dest_dir / filename)
        print(f"✓ Cloned '{args.source}' into '{args.world}'")
    else:
        write_default_files(dest_dir)
        print(f"✓ Created '{args.world}' with default state")


if __name__ == "__main__":
    main()
