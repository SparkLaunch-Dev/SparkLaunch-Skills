# Baseline Evaluation

## Summary

Baseline is already materially updated for the user-scoped MCP key model, but it still has founder-journey gaps:
- the broad founder path is present but not clearly framed as the default path to a credible or investable startup
- several files still carry outdated project-scoped wording or “API key scope determines tenancy” language
- cross-skill handoffs are uneven, especially around CRM naming consistency and launch-to-traction follow-up

Estimated baseline score: `58/72`

## Case Results

### CASE-01 Broad Founder Ask

- Result: partial pass
- Notes: `sparklaunch-platform` routes broad founder work correctly, and the founder recipe is strong, but the top-level docs do not yet make this the obvious default path for idea-to-investable outcomes. The post-launch traction loop is under-emphasized.

### CASE-02 MCP Setup

- Result: pass
- Notes: root and recipe docs now consistently describe user-scoped MCP keys, per-request project selection, and `projects.create`.

### CASE-03 Focused Validation

- Result: pass with wording drift
- Notes: the validation recipe is strong, but its summary still says `project-scoped validation record`, and the validation skill still contains outdated “bound to the MCP API key” wording.

### CASE-04 Brand To Launch

- Result: partial pass
- Notes: the launch recipe documents the known-good path well, but it does not strongly frame launch assets as traction-capture infrastructure for proving demand.

### CASE-05 Post-Launch Signals

- Result: partial pass
- Notes: the review recipe covers analytics and follow-up, but it is thin on investor- or traction-oriented synthesis, and it does not clearly distinguish lead-note versus contact-note handling.

### CASE-06 CRM Workspace Follow-Up

- Result: partial pass
- Notes: the CRM skill is substantively strong, but the repository still has naming inconsistency between `sparklaunch-sales-crm` and `sparklaunch-sales`, which weakens trigger reliability and handoff clarity.
