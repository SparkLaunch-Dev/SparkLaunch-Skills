---
title: Model and save a SAFE scenario
summary: Calculate supported SAFE exposure and optionally save a reviewed private modeling snapshot.
---

# Model and save a SAFE scenario

Use `sparklaunch-sparkclose` and the [shared rules](./README.md#shared-rules).

1. Select the project, inspect effective permissions and read financing readiness.
2. Select an existing cap table and model the founder's proposed USD post-money
   valuation-cap allocations with `sparkclose.model_safe`. Explain exposure,
   inclusion, priced-round and pool assumptions and returned warnings.
3. If requested, save a confirmed snapshot with `sparkclose.save_scenario` using
   unchanged model input and the current source version. Show the returned preview,
   wait for explicit approval and replay identical arguments and the idempotency
   key with its confirmation token. Read back the saved scenario.
4. Read private investment metadata when requested. Separate modeled scenarios,
   existing investment milestones and unverified assumptions.

Signing, agreement preparation and finalizing investments are unavailable through
this public plugin. Explain that limit without invoking tools or creating an
execution handoff. Never use hidden REST routes or the full MCP endpoint.
Retain identifiers and versions only for internal tool calls. Use human-readable
names in every report and confirmation. Never collect bank credentials or agreement bodies.
