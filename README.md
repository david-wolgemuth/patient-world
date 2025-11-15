# Patient World

A self-running simulation that ticks daily.

<!-- SNAPSHOT START -->
## 🌍 Patient World

**Day 2** • 2025-11-15

### Population
```
🌱 Grass    ██████████              549
🐇 Rabbits  █                        65
🦊 Foxes                             13
```

<!-- SNAPSHOT END -->

## About

This world runs autonomously via GitHub Actions and evolves according to simple ecological rules. The simulator lives in `sim.py`, with prod/dev worlds stored in JSON. History accumulates in `history.csv` for future visualization.

## Local Snapshot Testing

1. Generate a snapshot without touching README:

```bash
python sim.py --dev --snapshot
cat snapshot.md
```

2. Update the README using the generated snapshot:

```bash
python update_readme.py
git diff README.md
```

3. Reset README changes after testing if desired:

```bash
git checkout -- README.md
```

`snapshot.md` is ignored locally so these steps stay clean while the GitHub Action commits the official snapshot each tick.
