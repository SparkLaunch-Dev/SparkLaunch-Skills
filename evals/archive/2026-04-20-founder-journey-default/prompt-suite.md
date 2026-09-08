# Prompt Suite

Freeze these prompts for the entire run against target `D:\dev\SparkLaunch-Skills`.

## CASE-01 Broad Founder Ask

User request:
`I have an idea for an AI back-office assistant for independent insurance agencies. Use SparkLaunch to take me from idea to something credible and investable.`

Pass criteria:
- Routes to the broad founder workflow instead of a narrow one-off skill.
- Treats validation as the first blocking step.
- Carries the workflow through brand, launch, and founder deliverables.
- Frames the output around credibility, traction, and proof gaps rather than just asset creation.

Failure modes:
- Starts with a narrow skill such as landing or logo generation.
- Treats brand assets as sufficient without validation.
- Omits traction or investability framing.

## CASE-02 MCP Setup

User request:
`Set up SparkLaunch MCP for me so one key works across all my projects.`

Pass criteria:
- Uses the user-scoped MCP key recipe.
- Mentions `POST /api/mcp/auth/api-keys?token=<JWT>`.
- Mentions `X-SparkLaunch-Project-Id: <project_id>` and `projects.create`.

Failure modes:
- Refers to project-scoped keys.
- Suggests interactive login before the API-key path.

## CASE-03 Focused Validation

User request:
`Validate this startup idea for my current SparkLaunch project and give me the strongest risks and next actions.`

Pass criteria:
- Routes to validation rather than the full founder recipe.
- Keeps validation founder-facing instead of dumping raw JSON.
- Preserves the rule that downstream assets are not validated until the analysis completes.

Failure modes:
- Routes to full founder bootstrap without justification.
- Treats in-progress analysis as completed validation.

## CASE-04 Brand To Launch

User request:
`I already have a selected palette and logo. Build the launch page and QR campaign I can share next week.`

Pass criteria:
- Routes to the launch workflow.
- Requires favorite palette/logo or explicitly patches brand assets into the landing draft.
- Prefers a capture flow that creates measurable launch signals.

Failure modes:
- Ignores brand handoff requirements.
- Publishes without confirming draft persistence or live state.

## CASE-05 Post-Launch Signals

User request:
`Review my latest launch signals and tell me what I should follow up on right now so I can prove traction.`

Pass criteria:
- Routes to the signals/follow-up workflow.
- Pulls analytics and leads before suggesting writes.
- Converts signals into prioritized follow-up and traction proof, not just a metrics recap.

Failure modes:
- Returns only raw analytics.
- Blurs read-only analysis and write actions.

## CASE-06 CRM Workspace Follow-Up

User request:
`Open the contact workspace for our hottest lead, add a note, and refresh the summary if needed.`

Pass criteria:
- Routes to the CRM skill.
- Uses the contact-workspace contract as the verification read.
- Handles lead-note vs contact-note correctly.

Failure modes:
- Uses inconsistent CRM tool names.
- Skips the verification read after the write.
