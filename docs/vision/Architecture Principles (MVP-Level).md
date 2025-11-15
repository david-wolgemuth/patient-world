---
title: Architecture Principles (MVP-Level)
type: note
permalink: vision/architecture-principles-mvp-level
---

# Architecture Principles (MVP-Level)

## Summary
Keep the production world protected, experimentation disposable, and state stored in the simplest possible JSON files until the simulation itself demands more.

## Principles
- Maintain `state_prod.json` for the long-running world and `state_dev.json` for experimentation.
- Tick prod daily via automation while running limitless local dev loops.
- Use Git branches to gate changes; merge only after testing against dev state.
- Reject rule directories, schema migrations, and complex hierarchies until absolutely necessary.

## Tags
- #vision
- #architecture
- #mvp

## Observations
- [guardrail] Clear boundaries prevent experiments from corrupting prod history.
- [practice] Daily automation plus manual dev loops cover both stability and play.
- [principle] Simplicity is maintained by saying “no” to premature versioning layers.

## Relations
- depends_on [[Preferred Development Approach]]
- protects [[Project Vision]]
- constrains [[Core Features (The Fun Part)]]
