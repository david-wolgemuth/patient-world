---
title: Changelog Playbook
type: note
permalink: agents/changelog-playbook
---

# Changelog Playbook

## Purpose
How to log epic-level work from Beads into `docs/changelog/` so the knowledge base tracks major changes.

## When to Add a Changelog Entry
- An epic (or large feature) finishes in Beads
- CI/automation behavior changes significantly
- Simulator rules are overhauled

## Steps
1. **Identify the epic**: `bd show <epic>` to grab title + summary.
2. **Create note**: `bm tool write-note --project patient-world --folder changelog --title "YYYY-MM-DD <Epic Name>"`.
3. **Describe**:
   - Summary of what changed
   - Key CLI/workflow impacts
   - Links to affected Beads issues (e.g., `[patient-world-47e]`).
4. **Tag & relate**: use tags like `#changelog`, `#cli`, `#automation`; add `relates_to [[Project Vision]]` when relevant.
5. **Reference**: mention README/AGENTS sections updated so future agents know where to look.

## Example Template
```
# 2025-11-15 Forecast CLI

## Summary
Short paragraph describing the epic.

## Details
- Bullet 1 (e.g., `sim.py forecast` command)
- Bullet 2 (documentation updates)
- Bullet 3 (testing notes)

## Relations
- relates_to [[patient-world-nlv]]
- relates_to [[Project Vision]]
```

## Tips
- Use ISO dates in titles so entries sort chronologically.
- Keep the language high level; changelog is for future context, not exhaustive diffs.
- Mention any follow-up work that remains open in Beads.

## Observations
- [practice] Consistent templates make it easy to scan `docs/changelog/`.
- [tip] Copy-paste from Beads issue description to avoid drift.
- [guardrail] Never delete old entries—append-only history keeps audits straightforward.
