#!/usr/bin/env python3
"""Quick grid sanity harness (patient-world-nfu.8)."""
from __future__ import annotations

import argparse
from typing import Iterable, Tuple

from core.grid import Cell, GridState
from core.grid.tick import tick_grid

MAX_RABBITS = 600
MAX_FOXES = 200


def build_fixture(width: int = 5, height: int = 5) -> GridState:
    """Create a deterministic grid with concentrated populations."""
    cells = []
    center_x = width // 2
    center_y = height // 2
    for y in range(height):
        for x in range(width):
            grass = 60 if (x + y) % 2 == 0 else 40
            rabbits = 0
            foxes = 0
            if x == center_x and y == center_y:
                rabbits = 40
                foxes = 8
            cells.append(Cell(grass=grass, rabbits=rabbits, foxes=foxes))
    return GridState(day=0, grid_width=width, grid_height=height, cells=cells)


def assert_non_negative(state: GridState) -> None:
    for idx, cell in enumerate(state.cells):
        if cell.grass < 0 or cell.rabbits < 0 or cell.foxes < 0:
            raise AssertionError(f"Negative population detected in cell {idx}: {cell}")


def assert_caps(state: GridState) -> None:
    for idx, cell in enumerate(state.cells):
        if cell.rabbits > MAX_RABBITS:
            raise AssertionError(f"Rabbit explosion in cell {idx}: {cell.rabbits}")
        if cell.foxes > MAX_FOXES:
            raise AssertionError(f"Fox explosion in cell {idx}: {cell.foxes}")
        if cell.grass > 100:
            raise AssertionError(f"Grass cap violated in cell {idx}: {cell.grass}")


def assert_diffusion(previous: GridState, current: GridState) -> None:
    cx = previous.grid_width // 2
    cy = previous.grid_height // 2
    neighbor_coords = previous.neighbors(cx, cy)
    before_rabbits = _sum_species(previous, neighbor_coords, "rabbits")
    after_rabbits = _sum_species(current, neighbor_coords, "rabbits")
    before_foxes = _sum_species(previous, neighbor_coords, "foxes")
    after_foxes = _sum_species(current, neighbor_coords, "foxes")

    if after_rabbits <= before_rabbits:
        raise AssertionError("Rabbits failed to diffuse outward from the center.")
    if after_foxes <= before_foxes:
        raise AssertionError("Foxes failed to diffuse outward from the center.")


def _sum_species(state: GridState, coords: Iterable[Tuple[int, int]], attr: str) -> int:
    return sum(getattr(state.get_cell(x, y), attr) for x, y in coords)


def run_checks(ticks: int) -> GridState:
    state = build_fixture()
    diffusion_validated = False
    for step in range(ticks):
        previous = state
        state = tick_grid(state)
        assert_non_negative(state)
        assert_caps(state)
        if step == 0:
            assert_diffusion(previous, state)
            diffusion_validated = True
    if not diffusion_validated:
        raise AssertionError("Diffusion never validated.")
    return state


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sanity check the grid tick loop.")
    parser.add_argument("--ticks", type=int, default=25, help="Number of ticks to run (default: 25)")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    final_state = run_checks(max(1, args.ticks))
    print(
        f"Sanity checks passed after {args.ticks} ticks "
        f"(Day {final_state.day}, totals: "
        f"🌱{final_state.total_grass()} 🐇{final_state.total_rabbits()} 🦊{final_state.total_foxes()})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
