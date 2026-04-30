# Rubric

Primary metric: `founder_journey_score`

## Dimensions

Score each case on:
- trigger accuracy
- scope control
- contract correctness
- founder-journey coherence
- artifact integrity
- investability framing

## Scoring Method

Use `0`, `1`, or `2` points per dimension for each case:
- `0` = incorrect, missing, or likely harmful
- `1` = partially correct but incomplete or inconsistent
- `2` = clear, correct, and robust

Maximum score:
- 6 cases x 6 dimensions x 2 points = `72`

## Keep Threshold

- Candidate must exceed baseline by at least `4` points.
- Candidate must not introduce a contract regression on API-key scope, project selection, or documented tool names.
- A tie is acceptable only if the candidate is simpler and removes ambiguity.
