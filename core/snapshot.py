"""Snapshot generation and README updates."""
from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from core import world
from core.grid import viz
from core.grid.state import GridState

PROD_MARKERS = ("<!-- SNAPSHOT START -->", "<!-- SNAPSHOT END -->")
STAGING_MARKERS = ("<!-- STAGING SNAPSHOT START -->", "<!-- STAGING SNAPSHOT END -->")


def generate_snapshot(state: GridState) -> str:
    grid_viz = viz.render_grid(state)
    totals = (
        f"🌱 {state.total_grass()}  "
        f"🐇 {state.total_rabbits()}  "
        f"🦊 {state.total_foxes()}"
    )
    return (
        "## 🌍 Patient World\n\n"
        f"**Day {state.day}** • {datetime.now().strftime('%Y-%m-%d')}\n\n"
        f"{grid_viz}\n\n"
        "### Totals\n"
        f"{totals}\n"
    )


def save_snapshot(world_name: str, snapshot_text: str) -> Path:
    path = world.snapshot_path(world_name)
    with path.open("w") as fh:
        fh.write(snapshot_text)
    return path


def update_readme(world_name: str, *, staging: bool | None = None) -> None:
    snapshot_file = world.snapshot_path(world_name)
    if not snapshot_file.exists():
        raise FileNotFoundError(f"Snapshot not found for world '{world_name}' at {snapshot_file}")
    snapshot_text = snapshot_file.read_text()

    readme_path = Path("README.md")
    readme = readme_path.read_text()
    if staging is None:
        staging = world_name.startswith("staging") or world_name == "staging"
    start, end = STAGING_MARKERS if staging else PROD_MARKERS
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), flags=re.DOTALL)
    if not pattern.search(readme):
        raise RuntimeError(f"Marker pair {start}/{end} not found in README.md")
    replacement = f"{start}\n{snapshot_text}\n{end}"
    readme_path.write_text(pattern.sub(replacement, readme))
