# SparkLaunch reviewer demo script

An approximately 8–12 minute recording of the five positive and three negative cases in `chatgpt-app-submission.json`. Read the **Say** passages aloud; paste the **Prompt** text into ChatGPT. Timing is a guide: allow time to read each actual result and pause during long waits.

This is a recording script, not evidence that the cases have passed. The current candidate is `0.11.2`; consult `portal-prerequisites.json` for the current package digest and readiness status before filming.

## Before recording

- Use the existing private development installation or preview, with the skills and restricted tool surface corresponding to the packaged public candidate. Its endpoint must be `https://sparklaun.ch/api/mcp/chatgpt/`, with the verified 121-tool inventory. The existing full-endpoint test connection alone does not establish this. Deployment and authenticated verification remain prerequisites.
- Rotate the dedicated reviewer password securely and complete reviewer preflight. Select that account and confirm it can access only its synthetic project. Do not film from your ordinary founder account.
- The exact review prompts below currently reference synthetic project **99**. Verify that this is the reviewer project. If preflight establishes a different project, update and regenerate the review cases and this script together before filming.
- Rehearse once. Creating the validation workspace and generating the palette save private records. Check for earlier successful attempts before repeating either write after a timeout. Do not reset or delete records simply to improve a take.
- Record at 1080p or better. Enlarge the browser text, hide other tabs, close notifications, and crop the account/sidebar area. Pause for sign-in, consent, and any private handoff.
- Keep passwords, email addresses, tokens, authorization codes, raw tool payloads, private Action Center URLs, signed download URLs, and customer data out of the capture. Scene 6 needs a crop or opaque mask over the action link **before it appears**. Do not rely on blur for secrets.

If a scene fails in rehearsal, resolve it before filming. During recording, describe the actual response; do not read a success line when the operation failed or remains pending.

## 1. Introduction — 0:00–0:35

**Show:** The private SparkLaunch installation in ChatGPT. Use the real plugin page and interface.

**Say:**

> This is SparkLaunch, a connected workspace for building and operating a startup. I'm demonstrating the candidate for public review through our private test installation, using a dedicated account with synthetic data.
>
> I'll choose a project, create an idea-validation workspace, generate a brand palette, inspect landing-page projects, and prepare a secure CRM handoff. I'll also show how the app handles requests outside its capabilities.

## 2. Connection and project selection — 0:35–1:45

**Show:** The connected-account section, cropped to the synthetic account's safe display label. If connection is needed, pause recording before signing in and resume after returning to ChatGPT. Start a fresh chat with SparkLaunch enabled and the reviewer connection selected.

**Say:**

> SparkLaunch connects to the account I authorize. I signed in off-camera. First, I'll ask which projects that account can access.

**Prompt — positive case 1:**

```text
Show me the SparkLaunch projects I can access so I can choose one.
```

**Show:** The actual `projects.list` call label, if available without exposing private arguments, and the human-readable project list. Confirm the sole accessible project is the verified synthetic reviewer project.

**Say after verifying the result:**

> This is the synthetic project available to the reviewer account. I'll use it for the rest of the walkthrough.

If additional projects appear, stop and fix account isolation before recording further.

## 3. Create an idea-validation workspace — 1:45–2:50

**Say:**

> The example business is an AI bookkeeping assistant for independent contractors. I'll create a private workspace for evaluating that idea.

**Prompt — positive case 2:**

```text
Create a validation project for an AI bookkeeping assistant for independent contractors in project 99.
```

**Show:** Any necessary confirmation and the actual `validation.create_project` result, including the workspace's human-readable name and status. Keep internal identifiers and versions out of the displayed response.

**Say only after confirmed creation:**

> The validation workspace has been created in our selected project. This establishes the workspace; it doesn't mean market research or validation analysis has been completed.

If ChatGPT requests a required detail, supply synthetic data and leave that exchange visible. If creation is uncertain, inspect existing records before retrying.

## 4. Generate brand palettes — 2:50–4:10

**Say:**

> Next, I'll ask for colors suited to a bookkeeping product: trustworthy and modern.

**Prompt — positive case 3:**

```text
Generate a trustworthy, modern color palette for my contractor bookkeeping product in project 99.
```

**Show:** The actual `branding.generate_palette` result: saved palette names, color values, and feeling labels. Hold the result on screen long enough to read it.

**Say after confirmed generation:**

> These are the palette options SparkLaunch returned and saved. The names, color values, and descriptions give me concrete options to evaluate for the brand.

Point to one real option and read its name and two actual hex values. Do not use predetermined colors or describe an unsaved preview as saved.

## 5. Inspect landing-page projects — 4:10–5:00

**Say:**

> I'll now check the landing-page projects already available in this workspace.

**Prompt — positive case 4:**

```text
List the landing-page projects in SparkLaunch project 99.
```

**Show:** The actual `landing.list_projects` response. An honest empty result is valid; do not create or publish a page for this scene.

**Say if records exist:**

> These are the landing-page projects visible to this account. This request only inspected existing records.

**Say if the result is empty:**

> There are no landing-page projects in this synthetic workspace yet. SparkLaunch reports that directly. This request hasn't created or published a page.

## 6. Prepare a secure CRM handoff — 5:00–6:10

**Before submitting:** Apply the recording crop or opaque mask that hides the action-link area. Do not expand raw tool output.

**Say:**

> Some tasks continue in SparkLaunch's authenticated interface. I'll prepare a business-card import, while explicitly withholding permission to import anything yet.

**Prompt — positive case 5:**

```text
Prepare a secure business-card import for project 99, but do not import anything until I explicitly upload it in SparkLaunch.
```

**Show:** The safe `crm.prepare_business_card_import` call label and readable confirmation that the handoff was prepared and nothing was imported. Keep the actual expiring URL hidden. Do not open it, upload an image, or complete an import in this scene.

**Say after verified preparation:**

> SparkLaunch prepared an expiring first-party handoff. Nothing has been imported. Completing the task requires a separate, explicit upload in SparkLaunch. I've hidden the private action link in this recording.

## 7. Capability boundaries — 6:10–8:00

Start a fresh SparkLaunch-enabled chat for each of these three prompts, using the same reviewer connection. Show the complete answer and check that no SparkLaunch tool was invoked. Do not approve a transaction or follow a signing link if unexpected behavior occurs; treat that as a failed case.

**Say:**

> I'll finish the ChatGPT cases with three requests that should not trigger a SparkLaunch operation.

**Prompt — negative case 1:**

```text
What is the difference between a seed round and a Series A?
```

**Show:** A general educational answer, with no SparkLaunch call.

**Say after checking:**

> That was a general explanation. It didn't need access to our SparkLaunch workspace.

**Prompt — negative case 2:**

```text
Sign my SAFE agreement and close the investment in SparkLaunch.
```

**Show:** An explanation that signing and finalizing investments are excluded, with no SparkLaunch call or transaction link.

**Say after checking:**

> The initial public SparkClose scope supports planning and private records. Signing agreements and finalizing investments are excluded from this plugin.

**Prompt — negative case 3:**

```text
Transfer $500 from my checking account to savings.
```

**Show:** An honest explanation that SparkLaunch cannot access bank accounts or transfer funds, with no SparkLaunch call.

**Say after checking:**

> SparkLaunch has no banking or funds-transfer capability, so it hasn't performed that request.

## 8. Codex read check — approximately 8:00–9:00

Include this segment when demonstrating the supported Codex host. Rehearse it separately with the same candidate skills, restricted endpoint, and synthetic reviewer account; a successful ChatGPT call does not establish Codex execution.

**Show:** A fresh Codex task with SparkLaunch available. Keep unrelated files and terminal content out of the capture.

**Say:**

> I'll also demonstrate project discovery in Codex, using the same synthetic account.

**Prompt:**

```text
Show me the SparkLaunch projects I can access so I can choose one.
```

**Show:** A genuine `projects.list` result for the isolated reviewer project. Do not repeat the earlier writes. If tools are unavailable, resolve that host setup before including this segment; do not present an explanation of missing tools as a successful read.

## 9. Disconnect and close — approximately 9:00–10:15

Perform this last so it cannot interrupt earlier scenes. Disconnect only the synthetic reviewer connection. Keep connection identifiers and account details off screen. Start a fresh ChatGPT chat with SparkLaunch enabled and repeat the project-list prompt from scene 2.

**Show:** The connection settings and the resulting request to authorize access again. Do not reconnect on camera.

**Say after verifying the authorization request:**

> I disconnected the reviewer account. A new protected request now asks for authorization again.
>
> This walkthrough showed project discovery, a private validation workspace, saved brand palettes, landing-page inspection, and a prepared CRM handoff. It also showed the boundaries for general questions, investment execution, and bank transfers. The demonstration used synthetic data and did not publish a page, import a business card, sign an agreement, or move money.

Use only the closing claims supported by your actual take. If the disconnect check behaves differently, investigate rather than reading the expected line.

## After recording

1. Watch the complete exported video. Confirm prompts and results are readable, all eight review cases appear, narration matches the actual outcomes, and private data and links are hidden throughout.
2. Keep a private recording note with the recording date, candidate version and digest, host versions, verified endpoint, and outcome of each case. Do not publish credentials or raw tool payloads with the video.
3. Host the video at a stable HTTPS link accessible to reviewers without sign-in, an access request, or an expiring token. Test playback in a signed-out window.
4. Provide the final link for playback verification and inclusion in the package's review metadata. Until then, the demo-recording submission item remains incomplete. Recording does not submit or publish the plugin.

For broader workflow rehearsals and URL acceptance checks, see [the recording runbook](demo-recording-runbook.md).
