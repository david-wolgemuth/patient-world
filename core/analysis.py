"""Forecasting utilities for grid worlds."""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import Dict, List, Literal

from core.grid import tick
from core.model import GridState

SPECIES = ("grass", "rabbits", "foxes")
EXTINCTION_THRESHOLD = 0.5


@dataclass
class Sample:
    day: int
    grass: float
    rabbits: float
    foxes: float

    def as_dict(self) -> Dict[str, float]:
        return {"day": self.day, "grass": self.grass, "rabbits": self.rabbits, "foxes": self.foxes}


@dataclass
class MetricSummary:
    start: float
    end: float
    min: float
    max: float
    extinct_days: int = 0
    first_extinction_day: int | None = None

    def as_dict(self) -> Dict[str, float | int | None]:
        return {
            "start": self.start,
            "end": self.end,
            "min": self.min,
            "max": self.max,
            "extinct_days": self.extinct_days,
            "first_extinction_day": self.first_extinction_day,
        }


@dataclass
class ForecastResult:
    world: str
    days: int
    step: int
    seed: int | None
    initial_state: Dict[str, float]
    samples: List[Sample]
    summary: Dict[str, MetricSummary]

    def as_dict(self) -> Dict[str, object]:
        return {
            "world": self.world,
            "days": self.days,
            "step": self.step,
            "seed": self.seed,
            "initial_state": self.initial_state,
            "samples": [sample.as_dict() for sample in self.samples],
            "summary": {k: v.as_dict() for k, v in self.summary.items()},
        }


def run(state: GridState, *, world_name: str, days: int, step: int, seed: int | None = None) -> ForecastResult:
    if days <= 0:
        raise ValueError("--days must be positive")
    if step <= 0:
        raise ValueError("--step must be positive")

    current = state.clone()
    start_day = current.day
    end_day = start_day + days
    rng = random.Random(seed) if seed is not None else None

    def totals_dict(st: GridState) -> Dict[str, float]:
        return {
            "day": float(st.day),
            "grass": float(st.total_grass()),
            "rabbits": float(st.total_rabbits()),
            "foxes": float(st.total_foxes()),
        }

    def init_summary(species: str, totals: Dict[str, float]) -> MetricSummary:
        value = totals[species]
        return MetricSummary(start=value, end=value, min=value, max=value)

    initial_totals = totals_dict(current)
    summary = {species: init_summary(species, initial_totals) for species in SPECIES}
    samples: List[Sample] = []

    def record_sample(totals: Dict[str, float]) -> None:
        samples.append(
            Sample(day=int(totals["day"]), grass=totals["grass"], rabbits=totals["rabbits"], foxes=totals["foxes"])
        )

    record_sample(initial_totals)

    while current.day < end_day:
        current = tick.tick_grid(current)

        if rng is not None:
            _apply_noise(current, rng)

        totals = totals_dict(current)
        for species in SPECIES:
            value = totals[species]
            metric = summary[species]
            metric.min = min(metric.min, value)
            metric.max = max(metric.max, value)
            if value <= EXTINCTION_THRESHOLD:
                metric.extinct_days += 1
                if metric.first_extinction_day is None:
                    metric.first_extinction_day = int(totals["day"])

        if current.day >= end_day or ((current.day - start_day) % step == 0):
            record_sample(totals)

    totals = totals_dict(current)
    for species in SPECIES:
        summary[species].end = totals[species]

    return ForecastResult(
        world=world_name,
        days=days,
        step=step,
        seed=seed,
        initial_state=initial_totals,
        samples=samples,
        summary=summary,
    )


def _apply_noise(state: GridState, rng: random.Random) -> None:
    for cell in state.cells:
        cell.grass = max(0, min(100, int(round(cell.grass * rng.uniform(0.97, 1.03)))))
    _scale_entities(state, rng, "rabbit", 0.95, 1.05)
    _scale_entities(state, rng, "fox", 0.94, 1.06)


def _scale_entities(
    state: GridState,
    rng: random.Random,
    entity_type: Literal["rabbit", "fox"],
    low: float,
    high: float,
) -> None:
    """Randomly scale populations of the requested entity type between bounds."""
    cohort = [entity for entity in state.entities.values() if entity.type == entity_type]
    if not cohort:
        return
    target = max(0, int(round(len(cohort) * rng.uniform(low, high))))
    if target == len(cohort):
        return
    if target < len(cohort):
        to_remove = rng.sample(cohort, len(cohort) - target)
        for entity in to_remove:
            state.remove_entity(entity.id)
        return

    # Need to add new entities.
    spawn_locations = [(entity.x, entity.y) for entity in cohort]
    deficit = target - len(cohort)
    for _ in range(deficit):
        if spawn_locations:
            x, y = spawn_locations[rng.randrange(len(spawn_locations))]
        else:
            x = rng.randrange(state.grid_width)
            y = rng.randrange(state.grid_height)
        hunger_range = (0, 5) if entity_type == "rabbit" else (0, 7)
        age_range = (0, 20) if entity_type == "rabbit" else (0, 30)
        hunger = rng.randint(*hunger_range)
        age = rng.randint(*age_range)
        state.spawn_entity(entity_type, x, y, hunger=hunger, age=age)


def render_table(result: ForecastResult) -> str:
    lines: List[str] = []
    seed_text = f", seed={result.seed}" if result.seed is not None else ""
    lines.append(
        f"Forecasting '{result.world}' world for {result.days} days{seed_text} (sampling every {result.step} days)"
    )
    init = result.initial_state
    lines.append(
        "Initial state: "
        f"Day {int(init['day'])}, Grass={init['grass']:.0f}, Rabbits={init['rabbits']:.0f}, Foxes={init['foxes']:.0f}"
    )
    lines.append("")
    lines.append("Day    Grass   Rabbits  Foxes")
    for sample in result.samples:
        warn = _extinction_warning(sample, result.summary)
        lines.append(
            f"{sample.day:4d}    {sample.grass:4.0f}      {sample.rabbits:3.0f}      {sample.foxes:3.0f}{warn}"
        )

    lines.append("")
    lines.append(f"Summary ({result.days} days):")
    for label, species in ("Grass", "grass"), ("Rabbits", "rabbits"), ("Foxes", "foxes"):
        metric = result.summary[species]
        status = ""
        if metric.extinct_days:
            status = f"   extinct_days={metric.extinct_days}"
            if metric.end <= EXTINCTION_THRESHOLD:
                status += "   ⚠️ EXTINCT"
        lines.append(
            f"  {label:<7} start={metric.start:.0f}  end={metric.end:.0f}  min={metric.min:.0f}  max={metric.max:.0f}{status}"
        )
        if metric.first_extinction_day is not None:
            lines.append(
                f"    ⚠️  {label} went extinct on day {metric.first_extinction_day} "
                f"(spent {metric.extinct_days} days near 0)"
            )

    if result.seed is not None:
        lines.append(f"\nRun again with --seed {result.seed} for identical results.")

    return "\n".join(lines)


def _extinction_warning(sample: Sample, summary: Dict[str, MetricSummary]) -> str:
    warnings = []
    if sample.foxes <= EXTINCTION_THRESHOLD:
        warnings.append("Foxes extinct")
    if sample.rabbits <= EXTINCTION_THRESHOLD:
        warnings.append("Rabbits extinct")
    if sample.grass <= EXTINCTION_THRESHOLD:
        warnings.append("Grass depleted")
    if warnings:
        return "  ⚠️  " + "; ".join(warnings)
    return ""


def render_csv(result: ForecastResult) -> str:
    lines = ["day,grass,rabbits,foxes"]
    for sample in result.samples:
        lines.append(f"{sample.day},{sample.grass:.0f},{sample.rabbits:.0f},{sample.foxes:.0f}")
    return "\n".join(lines)


def render_json(result: ForecastResult) -> str:
    return json.dumps(result.as_dict(), indent=2)
