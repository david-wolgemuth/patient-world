"""Forecasting utilities for grid worlds."""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import Dict, List, Literal

import core.scheduler as scheduler
import core.telemetry as telemetry
from core.model import GridState
from core.environment.producers import PRODUCER_PROFILES, PRODUCER_TYPES

SPECIES = ("grass", "rabbits", "foxes")
PRODUCER_SPECIES = tuple(PRODUCER_TYPES)
EXTINCTION_THRESHOLD = 0.5


@dataclass
class Sample:
    day: int
    grass: float
    rabbits: float
    foxes: float
    water_mean: float
    water_min: float
    water_max: float
    dry_cells: int
    producers: Dict[str, float]

    def as_dict(self) -> Dict[str, float | int | Dict[str, float]]:
        return {
            "day": self.day,
            "grass": self.grass,
            "rabbits": self.rabbits,
            "foxes": self.foxes,
            "water_mean": self.water_mean,
            "water_min": self.water_min,
            "water_max": self.water_max,
            "dry_cells": self.dry_cells,
            "producers": dict(self.producers),
        }


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
    initial_state: Dict[str, float | Dict[str, float]]
    samples: List[Sample]
    summary: Dict[str, MetricSummary]
    producer_summary: Dict[str, MetricSummary]
    water_summary: "WaterSummary"
    capacity_summary: Dict[str, object] | None = None

    def as_dict(self) -> Dict[str, object]:
        return {
            "world": self.world,
            "days": self.days,
            "step": self.step,
            "seed": self.seed,
            "initial_state": self.initial_state,
            "samples": [sample.as_dict() for sample in self.samples],
            "summary": {k: v.as_dict() for k, v in self.summary.items()},
            "producer_summary": {k: v.as_dict() for k, v in self.producer_summary.items()},
            "water_summary": self.water_summary.as_dict(),
            "capacity_summary": self.capacity_summary,
        }


@dataclass
class WaterSummary:
    mean_start: float
    mean_end: float
    mean_min: float
    mean_max: float
    driest_cell: float
    wettest_cell: float
    max_dry_cells: int
    max_dry_day: int | None = None

    def as_dict(self) -> Dict[str, float | int | None]:
        return {
            "mean_start": self.mean_start,
            "mean_end": self.mean_end,
            "mean_min": self.mean_min,
            "mean_max": self.mean_max,
            "driest_cell": self.driest_cell,
            "wettest_cell": self.wettest_cell,
            "max_dry_cells": self.max_dry_cells,
            "max_dry_day": self.max_dry_day,
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

    def totals_dict(st: GridState) -> Dict[str, float | Dict[str, float]]:
        producer_totals = st.producer_totals()
        return {
            "day": float(st.day),
            "grass": float(sum(producer_totals.values())),
            "rabbits": float(st.total_rabbits()),
            "foxes": float(st.total_foxes()),
            "producers": {name: float(producer_totals.get(name, 0)) for name in PRODUCER_SPECIES},
        }

    def water_snapshot(st: GridState) -> Dict[str, float]:
        stats = st.water_stats()
        return {
            "mean": float(stats["mean"]),
            "min": float(stats["min"]),
            "max": float(stats["max"]),
            "dry_cells": int(stats["dry_cells"]),
        }

    def init_summary(species: str, totals: Dict[str, float]) -> MetricSummary:
        value = totals[species]
        return MetricSummary(start=value, end=value, min=value, max=value)

    initial_totals = totals_dict(current)
    initial_water = water_snapshot(current)
    summary = {species: init_summary(species, initial_totals) for species in SPECIES}
    producer_summary = {
        name: MetricSummary(
            start=initial_totals["producers"][name],
            end=initial_totals["producers"][name],
            min=initial_totals["producers"][name],
            max=initial_totals["producers"][name],
        )
        for name in PRODUCER_SPECIES
    }
    water_summary = WaterSummary(
        mean_start=initial_water["mean"],
        mean_end=initial_water["mean"],
        mean_min=initial_water["mean"],
        mean_max=initial_water["mean"],
        driest_cell=initial_water["min"],
        wettest_cell=initial_water["max"],
        max_dry_cells=initial_water["dry_cells"],
        max_dry_day=current.day if initial_water["dry_cells"] else None,
    )
    samples: List[Sample] = []
    capacity_tracker = telemetry.CapacityTracker()

    def record_sample(totals: Dict[str, float | Dict[str, float]], water: Dict[str, float]) -> None:
        samples.append(
            Sample(
                day=int(totals["day"]),
                grass=totals["grass"],
                rabbits=totals["rabbits"],
                foxes=totals["foxes"],
                water_mean=water["mean"],
                water_min=water["min"],
                water_max=water["max"],
                dry_cells=int(water["dry_cells"]),
                producers={name: float(totals["producers"][name]) for name in PRODUCER_SPECIES},
            )
        )

    record_sample(initial_totals, initial_water)

    while current.day < end_day:
        current = scheduler.tick_grid(current, log_capacity=False)
        capacity_tracker.ingest(current.capacity_events)

        if rng is not None:
            _apply_noise(current, rng)

        totals = totals_dict(current)
        water = water_snapshot(current)
        for species in SPECIES:
            value = totals[species]
            metric = summary[species]
            metric.min = min(metric.min, value)
            metric.max = max(metric.max, value)
            if value <= EXTINCTION_THRESHOLD:
                metric.extinct_days += 1
                if metric.first_extinction_day is None:
                    metric.first_extinction_day = int(totals["day"])
        for name in PRODUCER_SPECIES:
            value = totals["producers"][name]
            metric = producer_summary[name]
            metric.min = min(metric.min, value)
            metric.max = max(metric.max, value)
            if value <= EXTINCTION_THRESHOLD:
                metric.extinct_days += 1
                if metric.first_extinction_day is None:
                    metric.first_extinction_day = int(totals["day"])

        water_summary.mean_min = min(water_summary.mean_min, water["mean"])
        water_summary.mean_max = max(water_summary.mean_max, water["mean"])
        water_summary.driest_cell = min(water_summary.driest_cell, water["min"])
        water_summary.wettest_cell = max(water_summary.wettest_cell, water["max"])
        if water["dry_cells"] > water_summary.max_dry_cells:
            water_summary.max_dry_cells = water["dry_cells"]
            water_summary.max_dry_day = current.day

        if current.day >= end_day or ((current.day - start_day) % step == 0):
            record_sample(totals, water)

    totals = totals_dict(current)
    final_water = water_snapshot(current)
    for species in SPECIES:
        summary[species].end = totals[species]
    for name in PRODUCER_SPECIES:
        producer_summary[name].end = totals["producers"][name]
    water_summary.mean_end = final_water["mean"]

    return ForecastResult(
        world=world_name,
        days=days,
        step=step,
        seed=seed,
        initial_state=initial_totals,
        samples=samples,
        summary=summary,
        producer_summary=producer_summary,
        water_summary=water_summary,
        capacity_summary=capacity_tracker.snapshot(),
    )


def _apply_noise(state: GridState, rng: random.Random) -> None:
    for cell in state.cells:
        for name in cell.producers:
            jitter = rng.uniform(0.97, 1.03)
            cell.producers[name] = max(0, int(round(cell.producers[name] * jitter)))
        cell.clamp_layers()
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


def render_table(result: ForecastResult, *, capacity_details: bool = False) -> str:
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
    if isinstance(init.get("producers"), dict):
        lines.append("Initial producers: " + _format_producer_totals(init["producers"]))
    lines.append("")
    producer_header = " ".join(f"{PRODUCER_PROFILES[name].emoji:>6}" for name in PRODUCER_SPECIES)
    lines.append(f"Day    Grass   Rabbits  Foxes   Water  Dry  {producer_header}".rstrip())
    for sample in result.samples:
        warn = _extinction_warning(sample, result.summary)
        producer_values = " ".join(f"{sample.producers.get(name, 0):6.0f}" for name in PRODUCER_SPECIES)
        lines.append(
            f"{sample.day:4d}    {sample.grass:4.0f}      {sample.rabbits:3.0f}      {sample.foxes:3.0f}   "
            f"{sample.water_mean:4.2f}   {sample.dry_cells:3d}  {producer_values}{warn}"
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
    ws = result.water_summary
    lines.append(
        f"  Water   mean start={ws.mean_start:.2f}  end={ws.mean_end:.2f}  "
        f"range={ws.mean_min:.2f}-{ws.mean_max:.2f}  "
        f"cell range={ws.driest_cell:.2f}-{ws.wettest_cell:.2f}"
    )
    if ws.max_dry_cells:
        day_txt = f" on day {ws.max_dry_day}" if ws.max_dry_day is not None else ""
        lines.append(f"    Dry cells max={ws.max_dry_cells}{day_txt} (<=0.2 water)")
    else:
        lines.append("    No dry cells detected (water > 0.2 everywhere)")

    lines.append("")
    lines.append("Producer guilds:")
    for name in PRODUCER_SPECIES:
        profile = PRODUCER_PROFILES[name]
        metric = result.producer_summary[name]
        status = ""
        if metric.extinct_days:
            status = f"   extinct_days={metric.extinct_days}"
            if metric.end <= EXTINCTION_THRESHOLD:
                status += "   ⚠️ EXTINCT"
        lines.append(
            f"  {profile.emoji} {name:<18} start={metric.start:.0f}  end={metric.end:.0f}  "
            f"min={metric.min:.0f}  max={metric.max:.0f}{status}"
        )

    cap_lines = telemetry.format_capacity_lines(result.capacity_summary, verbose=capacity_details)
    if cap_lines:
        lines.append("")
        lines.extend(cap_lines)

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


def render_csv(result: ForecastResult, *, include_capacity: bool = False) -> str:
    producer_headers = ",".join(f"producer_{name}" for name in PRODUCER_SPECIES)
    base_header = "day,grass,rabbits,foxes,water_mean,water_min,water_max,dry_cells"
    header = f"{base_header},{producer_headers}" if producer_headers else base_header
    lines = [header]
    for sample in result.samples:
        producer_values = ",".join(str(int(sample.producers.get(name, 0))) for name in PRODUCER_SPECIES)
        producer_text = f",{producer_values}" if producer_values else ""
        lines.append(
            f"{sample.day},{sample.grass:.0f},{sample.rabbits:.0f},{sample.foxes:.0f},"
            f"{sample.water_mean:.3f},{sample.water_min:.3f},{sample.water_max:.3f},{sample.dry_cells}"
            f"{producer_text}"
        )
    if include_capacity:
        block = telemetry.capacity_csv_block(result.capacity_summary)
        if block:
            lines.append("")
            lines.extend(block)
    return "\n".join(lines)


def render_json(result: ForecastResult) -> str:
    return json.dumps(result.as_dict(), indent=2)


def _format_producer_totals(snapshot: Dict[str, float]) -> str:
    return " ".join(
        f"{PRODUCER_PROFILES[name].emoji}{snapshot.get(name, 0):.0f}" for name in PRODUCER_SPECIES
    )
