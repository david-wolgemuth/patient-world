"""Environment namespace: cells + spatial helpers."""

from .cell import Cell, generate_water_distribution, random_environment_profile

__all__ = ["Cell", "apply_entity_diffusion", "random_environment_profile", "generate_water_distribution"]


def apply_entity_diffusion(*args, **kwargs):
    from .spatial import apply_entity_diffusion as _impl

    return _impl(*args, **kwargs)
