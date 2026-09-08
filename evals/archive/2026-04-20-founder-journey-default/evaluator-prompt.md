# Evaluator Prompt

You are the evaluator for skill-loop run `2026-04-20-founder-journey-default` on target `D:\dev\SparkLaunch-Skills`.

Inputs:
- `prompt-suite.md`
- the current target artifact state

Outputs:
- `baseline-eval.md` for the unchanged baseline
- `candidate-eval.md` for the current candidate

Rules:
- use the exact frozen prompt suite
- record raw outputs and concise observations
- do not score the winner
- do not edit the target artifact
- do not change the prompt suite, rubric, or test plan
