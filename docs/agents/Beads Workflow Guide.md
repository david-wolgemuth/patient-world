---
title: Beads Workflow Guide
type: note
permalink: agents/beads-workflow-guide
---

# Beads Workflow Guide

## Summary
Practical steps for managing work with `bd` inside the patient-world repo, based on initializing the tool, configuring hooks, and creating epics/subtasks for the README snapshot request.

## Setup
- Run `bd init` once per repo; it creates `.beads/` and configures issue prefixes (e.g., `patient-world`).
- Accept the prompts to install git hooks (pre-commit flush) and configure the merge driver for `.beads/beads.jsonl`.
- Git now tracks `.beads/` and `.gitattributes`; commit them so others share the configuration.

## Creating Work
- Use `bd create --type epic --title "[size][tags] Title"` for epics. Titles can carry tags directly.
- Child tasks can be created with `--parent epic-id` to form a hierarchy (e.g., `patient-world-m6j.1`).
- Use the `--description` flag to summarize the request instead of editing after creation.
- `bd list` shows the epic and children, and `bd epic status` summarizes completion.

## Observations
- [workflow] Following a `[S]/[M]/[XS]` sizing convention in titles keeps scope obvious in `bd list` output.
- [practice] Git hooks + merge driver prevent conflicts between commits and async bead flushes.
- [tip] When asked to “create tasks but not implement,” keep everything in `bd` first and avoid touching code.

## Relations
- relates_to [[Basic Memory Usage]]
- supports [[Preferred Development Approach]]
