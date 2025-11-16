#!/usr/bin/env python3
"""Patient World CLI."""
from __future__ import annotations

import argparse
import sys
from typing import List

import core.analysis as analysis
import core.repository as repository
import core.scheduler as scheduler
import core.visualization as visualization
from core.model import GridState
from migrations import runner

COMMANDS = {"tick", "forecast", "init-grid", "migrate"}


def normalize_args(argv: List[str]) -> List[str]:
    if not argv:
        return ["tick"]
    if "-h" in argv or "--help" in argv:
        return argv
    if argv[0].startswith("-"):
        if argv[0] in {"-h", "--help"}:
            return argv
        return ["tick", *argv]
    if argv[0] in COMMANDS:
        return argv
    return ["tick", *argv]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Patient World Simulation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    tick_p = subparsers.add_parser("tick", help="Run simulation and save state")
    tick_p.add_argument("world", nargs="?", default="dev", help="World name (default: dev)")
    tick_p.add_argument("--count", type=int, default=1, help="Number of ticks to run")
    tick_p.add_argument("--snapshot", action="store_true", help="Generate snapshot.md after ticking")
    tick_p.add_argument("--log", action="store_true", help="Append final state to history.csv")
    tick_p.add_argument(
        "--update-readme",
        action="store_true",
        help="Update README snapshot for this world",
    )
    tick_p.set_defaults(func=cmd_tick)

    forecast_p = subparsers.add_parser("forecast", help="Forecast world evolution (read-only)")
    forecast_p.add_argument("world", nargs="?", default="dev", help="World name (default: dev)")
    forecast_p.add_argument("--days", type=int, default=365, help="Days to simulate ahead (default: 365)")
    forecast_p.add_argument("--step", type=int, default=30, help="Sampling interval in days (default: 30)")
    forecast_p.add_argument("--seed", type=int, help="Random seed for noisy projections")
    forecast_p.add_argument(
        "--format",
        choices=("table", "csv", "json"),
        default="table",
        help="Output format",
    )
    forecast_p.set_defaults(func=cmd_forecast)

    init_p = subparsers.add_parser("init-grid", help="Create a fresh grid-based world")
    init_p.add_argument("world", help="World name to initialize")
    init_p.add_argument("--width", type=int, default=10, help="Grid width (default: 10)")
    init_p.add_argument("--height", type=int, default=10, help="Grid height (default: 10)")
    init_p.add_argument("--rabbits", type=int, default=20, help="Initial rabbit population (default: 20)")
    init_p.add_argument("--foxes", type=int, default=5, help="Initial fox population (default: 5)")
    init_p.set_defaults(func=cmd_init_grid)

    migrate_p = subparsers.add_parser("migrate", help="Run pending migrations for a world")
    migrate_p.add_argument("world", nargs="?", default="dev", help="World name (default: dev)")
    migrate_p.set_defaults(func=cmd_migrate)

    return parser


def cmd_tick(args: argparse.Namespace) -> None:
    runner.run_pending(args.world)
    state = repository.load_world(args.world)

    for _ in range(max(args.count, 0)):
        state = scheduler.tick_grid(state)

    repository.save_world(args.world, state)

    if args.snapshot:
        snap_text = visualization.generate_snapshot(state)
        visualization.save_snapshot(args.world, snap_text)

    if args.log:
        repository.log_history(args.world, state)

    if args.update_readme:
        if args.world not in {"prod", "staging"}:
            raise SystemExit("README updates are restricted to prod or staging")
        visualization.update_readme(args.world)

    print(repository.format_summary(args.world, state))


def cmd_forecast(args: argparse.Namespace) -> None:
    runner.run_pending(args.world, silent=True)
    state = repository.load_world(args.world)
    result = analysis.run(
        state,
        world_name=args.world,
        days=args.days,
        step=args.step,
        seed=args.seed,
    )

    if args.format == "table":
        print(analysis.render_table(result))
    elif args.format == "csv":
        print(analysis.render_csv(result))
    else:
        print(analysis.render_json(result))


def cmd_init_grid(args: argparse.Namespace) -> None:
    state = repository.init_grid_world(
        args.world,
        width=max(1, args.width),
        height=max(1, args.height),
        total_rabbits=max(0, args.rabbits),
        total_foxes=max(0, args.foxes),
    )
    snap_text = visualization.generate_snapshot(state)
    visualization.save_snapshot(args.world, snap_text)
    print(f"Initialized {args.world} as {state.grid_width}x{state.grid_height} grid.")


def cmd_migrate(args: argparse.Namespace) -> None:
    changed = runner.run_pending(args.world)
    if changed:
        print(f"Applied migrations for {args.world}.")
    else:
        print(f"No migrations needed for {args.world}.")


def main(argv: List[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    argv = normalize_args(argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
