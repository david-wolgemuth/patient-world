#!/usr/bin/env python3
"""
World simulation. Run with --prod or --dev.
"""
import json
import sys
from datetime import datetime
from pathlib import Path


def tick(state):
    """Pure function: state in → state out"""
    grass = state["grass"] * 1.1
    rabbits = state["rabbits"] * 1.2 if grass > state["rabbits"] else state["rabbits"] * 0.8
    foxes = state["foxes"] * 1.15 if rabbits > state["foxes"] * 2 else state["foxes"] * 0.9

    grass = min(grass, 1000)
    rabbits -= state["foxes"] * 0.3
    grass -= state["rabbits"] * 0.5

    return {
        "day": state["day"] + 1,
        "grass": max(0, grass),
        "rabbits": max(0, rabbits),
        "foxes": max(0, foxes),
    }


def load_state(path: Path):
    if path.exists():
        with path.open() as fh:
            return json.load(fh)
    return {"day": 0, "grass": 500, "rabbits": 50, "foxes": 10}


def save_state(path: Path, state):
    with path.open("w") as fh:
        json.dump(state, fh, indent=2)


def append_history(state):
    line = f"{datetime.now().date()},{state['day']},{state['grass']:.0f},{state['rabbits']:.0f},{state['foxes']:.0f}\n"
    with Path("history.csv").open("a") as fh:
        fh.write(line)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dev"
    state_file = Path("state_prod.json" if mode == "--prod" else "state_dev.json")

    state = load_state(state_file)
    new_state = tick(state)
    save_state(state_file, new_state)

    if mode == "--prod":
        append_history(new_state)

    print(
        f"Day {new_state['day']}: Grass={new_state['grass']:.0f}, "
        f"Rabbits={new_state['rabbits']:.0f}, Foxes={new_state['foxes']:.0f}"
    )


if __name__ == "__main__":
    main()
