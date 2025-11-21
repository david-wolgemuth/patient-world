"""Telemetry helpers for summarizing simulation diagnostics."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple


Coord = Tuple[int, int]


@dataclass
class CapacityTracker:
    """Aggregate carrying-capacity clamp events across multiple ticks."""

    total_events: int = 0
    cell_counts: Counter[Coord] = field(default_factory=Counter)
    layer_counts: Counter[str] = field(default_factory=Counter)
    day_counts: Counter[int] = field(default_factory=Counter)

    def ingest(self, events: Iterable[Dict[str, int]]) -> None:
        for event in events:
            x = int(event.get("x", 0))
            y = int(event.get("y", 0))
            layer = str(event.get("layer", "unknown"))
            day = int(event.get("day", 0))
            self.total_events += 1
            self.cell_counts[(x, y)] += 1
            self.layer_counts[layer] += 1
            self.day_counts[day] += 1

    def has_events(self) -> bool:
        return self.total_events > 0

    def snapshot(self, top_n: int = 3) -> Dict[str, object]:
        if not self.has_events():
            return {}
        return {
            "total_events": self.total_events,
            "unique_cells": len(self.cell_counts),
            "active_days": len(self.day_counts),
            "layer_totals": dict(self.layer_counts),
            "top_cells": [
                {"x": x, "y": y, "events": count} for (x, y), count in self.cell_counts.most_common(top_n)
            ],
        }


def format_capacity_lines(summary: Dict[str, object] | None, *, verbose: bool = False) -> List[str]:
    if not summary:
        return []
    total_events = int(summary.get("total_events", 0))
    unique_cells = int(summary.get("unique_cells", 0))
    active_days = int(summary.get("active_days", 0))
    lines = [
        f"Capacity-limited events: {total_events} across {unique_cells} cells "
        f"(active on {active_days or 0} days)",
    ]
    top_cells = summary.get("top_cells") or []
    if top_cells:
        formatted = ", ".join(f"({cell['x']},{cell['y']})×{cell['events']}" for cell in top_cells)
        lines.append(f"  Hotspots: {formatted}")
    if verbose:
        layer_totals = summary.get("layer_totals") or {}
        if layer_totals:
            layer_text = ", ".join(f"{layer}:{count}" for layer, count in layer_totals.items())
            lines.append(f"  Layer totals: {layer_text}")
    return lines


def capacity_csv_block(summary: Dict[str, object] | None) -> List[str]:
    if not summary:
        return []
    top_cells = summary.get("top_cells") or []
    top_str = ";".join(f"{cell['x']}:{cell['y']}:{cell['events']}" for cell in top_cells)
    layer_totals = summary.get("layer_totals") or {}
    layer_str = ";".join(f"{layer}:{count}" for layer, count in layer_totals.items())
    return [
        "metric,value",
        f"capacity_total_events,{summary.get('total_events', 0)}",
        f"capacity_unique_cells,{summary.get('unique_cells', 0)}",
        f"capacity_active_days,{summary.get('active_days', 0)}",
        f"capacity_top_cells,{top_str or 'n/a'}",
        f"capacity_layer_totals,{layer_str or 'n/a'}",
    ]
