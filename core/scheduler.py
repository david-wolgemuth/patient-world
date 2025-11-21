"""Tick scheduler orchestrating rule execution."""
from __future__ import annotations

from core.model import GridState
from . import rules


def tick_grid(state: GridState, *, log_capacity: bool = True) -> GridState:
    """Apply one tick over the grid using entity behaviors."""
    next_state = state.clone()
    rules.apply_all(next_state, log_capacity=log_capacity)
    next_state.day += 1
    return next_state
