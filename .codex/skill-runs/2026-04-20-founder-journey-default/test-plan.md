# Test Plan

List the smallest relevant checks for the target artifact.

## Required checks

- Command: `python -m pytest tests/test_agent_recipes.py`
  Purpose: Verify recipe catalog structure and the founder-flow contract that the main SparkLaunch repo enforces against the sibling skills repo.
  Required: yes

## Optional checks

- Command: `git diff --check`
  Purpose: Catch markdown and YAML whitespace or merge-marker mistakes in the skills repo.
  Required: no
