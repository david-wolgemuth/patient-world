#!/usr/bin/env python3
"""Patient World CLI."""
from __future__ import annotations

import argparse
import sys

from core import forecast, snapshot, world
from core import simulation


def normalize_args(argv: list[str]) -> list[str]:
    if not argv:
        return ["tick"]
    if argv[0] in {"tick", "forecast"}:
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
    forecast_p.add_argument("--days", type=int, required=True, help="Days to simulate ahead")
    forecast_p.add_argument("--step", type=int, default=30, help="Sampling interval in days")
    forecast_p.add_argument("--seed", type=int, help="Random seed for noisy projections")
    forecast_p.add_argument(
        "--format",
        choices=("table", "csv", "json"),
        default="table",
        help="Output format",
    )
    forecast_p.set_defaults(func=cmd_forecast)

    return parser


def cmd_tick(args: argparse.Namespace) -> None:
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
        if args.world not in {"prod", "staging"}:
            raise SystemExit("README updates are restricted to prod or staging")
        snapshot.update_readme(args.world)

    print(world.format_summary(args.world, state))


def cmd_forecast(args: argparse.Namespace) -> None:
    state = world.load_world(args.world)
    result = forecast.run(
        state,
        world_name=args.world,
        days=args.days,
        step=args.step,
        seed=args.seed,
    )

    if args.format == "table":
        print(forecast.render_table(result))
    elif args.format == "csv":
        print(forecast.render_csv(result))
    else:
        print(forecast.render_json(result))


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    argv = normalize_args(argv)
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
