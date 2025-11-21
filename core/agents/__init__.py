"""Agent namespace for Patient World."""

from .entity import Entity
from .herbivores import HERBIVORE_PROFILES, HERBIVORE_TYPES, HerbivoreProfile

__all__ = ["Entity", "HerbivoreProfile", "HERBIVORE_PROFILES", "HERBIVORE_TYPES"]
