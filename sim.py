#!/usr/bin/env python3
"""Patient World simulation supporting multiple named worlds."""
import argparse
import json
from datetime import datetime
from pathlib import Path

DEFAULT_STATE = {"day": 0, "grass": 500, "rabbits": 50, "foxes": 10}
HISTORY_HEADER = "date,day,grass,rabbits,foxes"
WORLDS_DIR = Path("worlds")


def tick(state):
    """Pure function: state in → state out"""
    grass = min(state["grass"] * 1.1, 1000)

    # Feedback loop: rabbit births track food availability
    demand = state["rabbits"] * 5 or 1
    food_ratio = min(grass / demand, 1.0)
    rabbit_growth = 0.9 + 0.2 * food_ratio  # 0.9× when starving, up to 1.1× when abundant
    rabbits = state["rabbits"] * rabbit_growth
    rabbits -= state["rabbits"] * (1 - food_ratio) * 0.1  # starvation losses when grass is scarce

    foxes = state["foxes"] * 1.05 if rabbits > state["foxes"] * 2 else state["foxes"] * 0.95

    grass -= state["rabbits"] * (0.2 + 0.1 * food_ratio)

    rabbits -= state["foxes"] * 0.2

    grass = int(max(0, round(grass)))
    rabbits = int(max(0, round(rabbits)))
    foxes = int(max(0, round(foxes)))

    return {
        "day": state["day"] + 1,
        "grass": max(0, grass),
        "rabbits": max(0, rabbits),
        "foxes": max(0, foxes),
    }


def generate_snapshot(state):
    """Generate README snapshot."""
    max_pop = 1000

    def bar(value):
        return "█" * min(20, int(value / max_pop * 20))

    return (
        "## 🌍 Patient World\n\n"
        f"**Day {state['day']}** • {datetime.now().strftime('%Y-%m-%d')}\n\n"
        "### Population\n```\n"
        f"🌱 Grass    {bar(state['grass']):<20} {state['grass']:>6.0f}\n"
        f"🐇 Rabbits  {bar(state['rabbits']):<20} {state['rabbits']:>6.0f}\n"
        f"🦊 Foxes    {bar(state['foxes']):<20} {state['foxes']:>6.0f}\n"
        "```\n"
    )


def load_state(path: Path):
    if path.exists():
        with path.open() as fh:
            return json.load(fh)
    return DEFAULT_STATE.copy()


def save_state(path: Path, state):
    with path.open("w") as fh:
        json.dump(state, fh, indent=2)


def ensure_history_file(path: Path):
    if not path.exists():
        path.write_text(HISTORY_HEADER + "\n")


def append_history(state, path: Path):
    ensure_history_file(path)
    line = f"{datetime.now().date()},{state['day']},{state['grass']:.0f},{state['rabbits']:.0f},{state['foxes']:.0f}\n"
    with path.open("a") as fh:
        fh.write(line)


def parse_args():
    parser = argparse.ArgumentParser(description="Run a Patient World tick for a specific world.")
    parser.add_argument("world", help="World name (prod, dev, staging, etc.)")
    parser.add_argument("--snapshot", action="store_true", help="Write snapshot.md for the given world")
    return parser.parse_args()


def main():
    args = parse_args()
    world_dir = WORLDS_DIR / args.world
    world_dir.mkdir(parents=True, exist_ok=True)
    state_file = world_dir / "state.json"
    history_file = world_dir / "history.csv"
    snapshot_file = world_dir / "snapshot.md"

    state = load_state(state_file)
    new_state = tick(state)
    save_state(state_file, new_state)

    if args.snapshot:
        snapshot_file.write_text(generate_snapshot(new_state))

    append_history(new_state, history_file)

    print(
        f"[{args.world}] Day {new_state['day']}: "
        f"Grass={new_state['grass']:.0f}, Rabbits={new_state['rabbits']:.0f}, Foxes={new_state['foxes']:.0f}"
    )


if __name__ == "__main__":
    main()
