---
title: Beads Workflow Guide
type: note
permalink: agents/beads-workflow-guide
---

# Beads Workflow Guide

## Summary

Practical steps for managing work with `bd` inside the patient-world repo, based on initializing the tool, configuring hooks, and creating epics/subtasks for the README snapshot request.

- Run `bd quickstart` anytime you are asked to use beads or create/read issues

## Project Custom Preferences

### Use T-Shirt Size & Title Tags

- Use `bd create --type epic --title "[size][tags] Title"` for epics. Titles can carry tags directly.

### Use epics

- Child tasks can be created with `--parent epic-id` to form a hierarchy (e.g., `patient-world-m6j.1`).
- `bd list` shows the epic and children, and `bd epic status` summarizes completion.

### Prefer `--json` for queries

- When running `bd ready`, `bd list`, or similar commands, pass `--json` so output stays machine-friendly for notes or automations.

## Observations
- [workflow] Following a `[S]/[M]/[XS]` sizing convention in titles keeps scope obvious in `bd list` output.
- [practice] Git hooks + merge driver prevent conflicts between commits and async bead flushes.
- [tip] When asked to “create tasks but not implement,” keep everything in `bd` first and avoid touching code.

## Relations
- relates_to [[Basic Memory Usage]]
- supports [[Preferred Development Approach]]
