#!/usr/bin/env python3
"""Patient World - Simple CLI."""
from __future__ import annotations

import argparse
import sys

from core import simulation, snapshot, world


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Patient World Simulation")
    parser.add_argument(
        "world",
        nargs="?",
        default="dev",
        help="World name (dev, prod, staging-*, etc.)",
    )
    parser.add_argument("--count", type=int, default=1, help="Number of ticks to run")
    parser.add_argument("--snapshot", action="store_true", help="Write snapshot.md after ticking")
    parser.add_argument("--log", action="store_true", help="Append the resulting state to history.csv")
    parser.add_argument(
        "--update-readme",
        action="store_true",
        help="Update README snapshot block using the generated snapshot",
    )
    return parser.parse_args(argv)


def run(args: argparse.Namespace) -> None:
    state = world.load_world(args.world)

    for _ in range(max(args.count, 0)):
        state = simulation.tick(state)

    world.save_world(args.world, state)

    if args.snapshot:
        snap_text = snapshot.generate_snapshot(state)
        snapshot.save_snapshot(args.world, snap_text)

    if args.log:
        world.log_history(args.world, state)

    if args.update_readme:
        snapshot.update_readme(args.world)

    print(world.format_summary(args.world, state))


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)
    run(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
