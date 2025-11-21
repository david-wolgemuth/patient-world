#!/usr/bin/env python3
"""Quick grid sanity harness (patient-world-nfu.8)."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, Tuple

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.environment import Cell
from core.environment.producers import CANOPY_LAYER, GROUND_LAYER, empty_producer_map
from core.model import GridState
from core.scheduler import tick_grid
from core.agents import HERBIVORE_TYPES

MAX_RABBITS = 600
MAX_FOXES = 200
PRODUCER_TOLERANCE = 2
HERBIVORE_SET = set(HERBIVORE_TYPES)


def build_fixture(width: int = 5, height: int = 5) -> GridState:
    """Create a deterministic grid with concentrated populations."""
    cells = []
    center_x = width // 2
    center_y = height // 2
    for y in range(height):
        for x in range(width):
            base = 60 if (x + y) % 2 == 0 else 40
            producers = empty_producer_map()
            producers["fast_grass"] = base
            producers["seasonal_annuals"] = base // 3
            producers["slow_shrubs"] = base // 4
            producers["deep_roots"] = base // 5
            if (x + y) % 3 == 0:
                producers["moss_carpet"] = base // 5
                producers["fungal_mat"] = base // 6
            if (x + y) % 4 == 0:
                producers["reed_beds"] = base // 4
            if (x + y) % 5 == 0:
                producers["succulent_cluster"] = base // 6
            producers["fruit_trees"] = base // 6
            producers["needle_conifers"] = base // 7
            producers["vine_canopy"] = base // 8
            cells.append(Cell(producers=producers))
    state = GridState(day=0, grid_width=width, grid_height=height, cells=cells, migration_version=2)
    for _ in range(40):
        state.spawn_entity("rabbit", center_x, center_y)
    for _ in range(8):
        state.spawn_entity("fox", center_x, center_y)
    return state


def assert_non_negative(state: GridState) -> None:
    for idx, cell in enumerate(state.cells):
        for name, amount in cell.producers.items():
            if amount < 0:
                raise AssertionError(f"Negative biomass for {name} detected in cell {idx}: {cell}")


def assert_caps(state: GridState) -> None:
    entities = state.entities
    for idx, cell in enumerate(state.cells):
        if cell.rabbits(entities) > MAX_RABBITS:
            raise AssertionError(f"Rabbit explosion in cell {idx}")
        if cell.foxes(entities) > MAX_FOXES:
            raise AssertionError(f"Fox explosion in cell {idx}")
        ground_cap = cell.layer_capacity(GROUND_LAYER)
        canopy_cap = cell.layer_capacity(CANOPY_LAYER)
        if cell.ground_cover() > ground_cap + PRODUCER_TOLERANCE:
            raise AssertionError(
                f"Ground layer cap violated in cell {idx}: {cell.ground_cover()} > {ground_cap}"
            )
        if cell.canopy_cover() > canopy_cap + PRODUCER_TOLERANCE:
            raise AssertionError(
                f"Canopy layer cap violated in cell {idx}: {cell.canopy_cover()} > {canopy_cap}"
            )


def assert_diffusion(previous: GridState, current: GridState) -> None:
    cx = previous.grid_width // 2
    cy = previous.grid_height // 2
    neighbor_coords = previous.neighbors(cx, cy)
    before_rabbits = _sum_species(previous, neighbor_coords, "rabbit")
    after_rabbits = _sum_species(current, neighbor_coords, "rabbit")
    before_foxes = _sum_species(previous, neighbor_coords, "fox")
    after_foxes = _sum_species(current, neighbor_coords, "fox")

    # Herbivores are now stationary and should NOT diffuse
    if "rabbit" in HERBIVORE_SET:
        if after_rabbits > before_rabbits:
            raise AssertionError("Herbivores unexpectedly diffused (should be stationary).")
    elif after_rabbits <= before_rabbits:
        raise AssertionError("Non-herbivore rabbits failed to diffuse outward from the center.")
    if after_foxes <= before_foxes:
        raise AssertionError("Foxes failed to diffuse outward from the center.")


def _sum_species(state: GridState, coords: Iterable[Tuple[int, int]], species: str) -> int:
    cells = (state.get_cell(x, y) for x, y in coords)
    entities = state.entities
    counter = 0
    for cell in cells:
        counter += cell.rabbits(entities) if species == "rabbit" else cell.foxes(entities)
    return counter


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
        f"🌱{final_state.total_biomass()} 🐇{final_state.total_rabbits()} 🦊{final_state.total_foxes()})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
