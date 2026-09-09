# Skill evaluations

These files retain workflow-quality cases and their evidence separately from the
generated host packages.

| Resource | Purpose |
| --- | --- |
| [Skill trigger cases](skill-trigger-cases.json) | Positive routing cases and negative boundaries for the canonical skills. |
| [Controlled end-to-end guide](CONTROLLED-E2E.md) | Procedure and proof boundaries for reviewing multi-tool workflows. |
| [Controlled end-to-end matrix](controlled-e2e-matrix.json) | The structured workflow cases used by that guide. |
| [April 20, 2026 founder-journey evaluation](archive/2026-04-20-founder-journey-default/run-manifest.md) | Historical prompts, rubric, baseline, candidate, verdict, and test report. |

The archived run was moved from `.codex/skill-runs/` without changing its contents.
Its checkout paths, branch names, scores, and test results describe the original
run; they are not current release or performance evidence. Keep these records for
provenance. Future local agent runs are ignored by Git; promote only reviewed,
credential-free evaluation material into this directory.

Run the repository checks described in [CONTRIBUTING.md](../CONTRIBUTING.md).
Automated package tests check case coverage and safety contracts. Those checks
do not establish that a host completed a workflow in production.
