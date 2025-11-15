---
title: Basic Memory Usage
type: note
permalink: agents/basic-memory-usage
---

# Basic Memory Usage

## Purpose
Quick meta guide for working with Basic Memory inside the `patient-world` repo.

## Setup
- Notes live under `docs/` (e.g., `vision/`, `agents/`).
- The `patient-world` project was added via `bm project add patient-world ./docs`.
- Always pass `--project patient-world` (default project mode is off here).

## Authoring Flow
- Create notes with `bm tool write-note --folder <folder> --title <title> --project patient-world`.
- Provide content via heredoc or stdin to include Observations, Relations, and tags.
- Use `bm tool read-note <permalink>` to inspect formatted output.
- `bm status --project patient-world` shows pending sync work.

## Findings
- Omitting `--project` results in “No project specified” errors.
- Relations resolve automatically once referenced notes exist or after sync.
- The CLI binary lives at `/Users/david/.local/bin/bm`; it may not be on every PATH, so use the explicit path if needed.
- Deprecation warnings from `aiosqlite` are harmless for current usage.

## Tags
- #meta
- #basic-memory
- #workflow

## Observations
- [practice] Keeping folders scoped (vision, agents, etc.) makes it easy to target new notes.
- [tooling] Explicit project flags avoid accidental writes to other knowledge bases.
- [tip] When scheduling automation, ensure GitHub Actions can run `bm` only if the CLI is available on runners.

## Relations
- relates_to [[Preferred Development Approach]]
