---
title: README
type: note
permalink: docs/readme
---

# Docs Overview

Use this README as the entry point for the `patient-world` knowledge base. The
notes mirror the repo's `docs/` folder structure so agents know where to look
before editing code.

## Using the Basic Memory CLI
- The CLI binary lives at `/Users/david/.local/bin/bm`; call it explicitly in
  scripts.
- Always specify the project: `bm tool read-note --project patient-world <id>`
  or `bm tool write-note --project patient-world --folder <folder> --title <t>`.
- Author notes by piping markdown via heredoc/stdin; relations resolve after the
  referenced note exists.
- `bm status --project patient-world` surfaces pending sync work if the daemon
  is active.

## Docs Tree Structure
- `vision/` — Goals, preferred development approach, and MVP architecture
  principles that constrain prod vs. dev behavior.
- `architecture/` — Deeper structural guides, e.g., the migrated **Migration
  Strategy** reference and future system designs.
- `agents/` — Meta process guides such as **Basic Memory Usage** and the
  **Changelog Playbook** for logging work.
- `changelog/` — Dated entries describing large epics landing in main, useful
  context before proposing overlapping work.

## Example: Add a Changelog Entry
```bash
cat <<'EOF' | /Users/david/.local/bin/bm tool write-note \
  --project patient-world \
  --folder changelog \
  --title "2025-11-16 Entity Grid Kickoff"
--- 
title: 2025-11-16 Entity Grid Kickoff
permalink: changelog/2025-11-16-entity-grid-kickoff
---
\n# 2025-11-16 Entity Grid Kickoff\n\n- Started entity-based grid epic\n- Added Entity dataclass + GridState registry\nEOF
```
- Pipe the markdown body via heredoc (include front matter).
- The folder controls placement under `docs/changelog/`.
- Pick a descriptive title; permalinks derive from it.

Add new folders sparingly; keep scope clear so future notes are easy to find.
