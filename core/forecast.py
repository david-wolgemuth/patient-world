"""Forecasting utilities for read-only projections."""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from typing import Dict, Iterable, List

from core import simulation

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


def _copy_state(state: Dict[str, float]) -> Dict[str, float]:
    return {k: float(state[k]) for k in SPECIES + ("day",)}


def run(state: Dict[str, float], *, world_name: str, days: int, step: int, seed: int | None = None) -> ForecastResult:
    if days <= 0:
        raise ValueError("--days must be positive")
    if step <= 0:
        raise ValueError("--step must be positive")

    current = _copy_state(state)
    start_day = int(current["day"])
    end_day = start_day + days
    rng = random.Random(seed)

    def init_summary(species: str) -> MetricSummary:
        value = current[species]
        return MetricSummary(start=value, end=value, min=value, max=value)

    summary = {species: init_summary(species) for species in SPECIES}
    samples: List[Sample] = []

    def record_sample() -> None:
        samples.append(
            Sample(
                day=int(current["day"]),
                grass=current["grass"],
                rabbits=current["rabbits"],
                foxes=current["foxes"],
            )
        )

    record_sample()

    while int(current["day"]) < end_day:
        current = simulation.tick(current)

        if seed is not None:
            _apply_noise(current, rng)

        for species in SPECIES:
            value = current[species]
            metric = summary[species]
            metric.min = min(metric.min, value)
            metric.max = max(metric.max, value)
            if value <= EXTINCTION_THRESHOLD:
                metric.extinct_days += 1
                if metric.first_extinction_day is None:
                    metric.first_extinction_day = int(current["day"])

        if int(current["day"]) >= end_day or ((int(current["day"]) - start_day) % step == 0):
            record_sample()

    for species in SPECIES:
        summary[species].end = current[species]

    return ForecastResult(
        world=world_name,
        days=days,
        step=step,
        seed=seed,
        initial_state=_copy_state(state),
        samples=samples,
        summary=summary,
    )


def _apply_noise(state: Dict[str, float], rng: random.Random) -> None:
    state["grass"] = max(0, min(1000, state["grass"] * rng.uniform(0.97, 1.03)))
    state["rabbits"] = max(0, state["rabbits"] * rng.uniform(0.95, 1.05))
    state["foxes"] = max(0, state["foxes"] * rng.uniform(0.94, 1.06))


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
        lines.append(
            f"\nRun again with --seed {result.seed} for identical results."
        )

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
