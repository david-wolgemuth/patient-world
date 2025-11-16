"""Environment namespace: cells + spatial helpers."""

from .cell import Cell

__all__ = ["Cell", "apply_entity_diffusion"]


def apply_entity_diffusion(*args, **kwargs):
    from .spatial import apply_entity_diffusion as _impl

    return _impl(*args, **kwargs)
