---
title: Aggregated View Layer
type: note
permalink: vision/aggregated-view-layer
---

# Aggregated View Layer

## Summary
Separate the high-resolution world state from a fixed-resolution visualization grid. Derive the README snapshot by spatially aggregating entities and fields into a small (e.g., 80×80) “camera” view instead of limiting the world to that size.

## Concepts
- **World space:** true resolution (e.g., 200×200). Entities, cells, and resources live here with precise coordinates.
- **View space:** fixed, smaller grid (e.g., 80×80) used only for visualization. Each view cell represents a rectangular region of world space.
- **Spatial binning:** map entities to bins based on `vx = int(x * VW / W)` and `vy = int(y * VH / H)`, clamped to view bounds. Accumulate per-bin counts (e.g., rabbits, foxes) and scalar fields (grass totals/averages).
- **Emoji selection:** pick a symbol per bin via priority rules (foxes > rabbits > dense grass > sparse grass > empty). Generates a compact, readable snapshot even if thousands of entities exist.

## Extensions
- **Temporal accumulation:** optionally track per-bin histories (visits, kills) for long-term heatmaps instead of single-tick snapshots.
- **README rendering:** output VH lines of VW emojis inside a code block; 80×80 (~6.4k chars) remains readable, and future view sizes can change without touching world resolution.

## Observations
- [principle] Keep world state as source of truth; the view is derived on demand.
- [practice] Aggregation lets README stay readable while the simulation grows in scope.
- [idea] Historical counts enable highlighting trails or hotspots once the spatial aggregation works well.

## Relations
- relates_to [[Project Vision]]
- relates_to [[Core Features (The Fun Part)]]
