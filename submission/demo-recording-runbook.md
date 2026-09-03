# SparkLaunch ChatGPT Plugin Demo Recording Runbook

Use this runbook to create the reviewer-facing demonstration required for the MCP-backed SparkLaunch plugin. The recording is external review material and is never included in the portal ZIP.

## Recording gate

Record only after all of the following are true:

- OpenAI Scan Tools has succeeded against `https://sparklaun.ch/api/mcp/` and discovered exactly 61 tools for the deployed candidate. The retained 59-tool scan is historical evidence and does not satisfy this gate.
- Reviewer access, project isolation, and required review materials have been verified; operational sign-in and project-binding details remain outside this repository.
- The OpenAI portal shows the intended verified publisher identity in the same organization and project used for submission.
- The portal candidate version and package digest match `submission/portal-prerequisites.json`.

Never show or retain sign-in values, authorization codes, consent artifacts, private browser data, addresses, customer information, private Action Center links, confirmation tokens, signed file URLs, or provider-session details. Pause the recording while entering the reviewer sign-in values, then resume only after the consent screen is safe to display.

## Target format

- Record in English at 1080p or better with legible browser text and clear narration.
- Keep the walkthrough approximately 8–12 minutes.
- Show hosted ChatGPT first and Codex second because both are supported plugin surfaces.
- Use only synthetic data in the disposable reviewer project.
- Host the final recording at a stable HTTPS URL that opens without sign-in, access requests, an expiring link, or a private network.

## Walkthrough

1. **Introduce SparkLaunch.** State that the plugin supports private founder workflows for projects, validation, branding, launch assets, CRM, and incorporation preparation.
2. **Connect in hosted ChatGPT.** Select SparkLaunch, trigger the first protected action with `projects.list`, complete OAuth off-camera, and show the consent scopes before approval. Confirm the returned project list contains only the synthetic reviewer project.
3. **Run the five submitted positive cases.** Use the exact prompts from `chatgpt-app-submission.json` for `projects.list`, `validation.create_project`, `branding.generate_palette`, `landing.list_projects`, and `crm.prepare_business_card_import`. Show concise, human-readable results without exposing internal identifiers or versions.
4. **Show write safety.** Request `projects.invite_collaborator` with an `example.com` recipient, display the exact confirmation preview, and decline it. Explain that confirming would send a non-recallable email, so the demo intentionally creates no invitation.
5. **Show the portable CRM handoff and address boundary.** Ask SparkLaunch to prepare a business-card import. Open the expiring first-party action off-camera, sign in, select a synthetic image that includes an address, and explicitly choose **Upload and import**. Return to ChatGPT and read status through `crm.get_business_card_import`. Demonstrate that only non-address contact data is stored, nothing is imported by the prepare call, and no arbitrary URL, base64, image bytes, address, or private contact data crosses the MCP transcript.
6. **Show the incorporation handoff.** Attach the packaged synthetic non-address incorporation draft, update the disposable case, and show the safe case status. Explain that participant and company addresses are entered only in the authenticated SparkLaunch Action Center. Do not open a private participant link or start identity, signature, payment, filing-provider, or registered-agent activity.
7. **Show Codex support.** Open a fresh Codex task with SparkLaunch installed, run `projects.list`, and perform one narrow read from the same disposable project. Do not repeat a write merely to demonstrate the second platform.
8. **Show disconnect behavior.** Disconnect SparkLaunch from its connection settings, then demonstrate that the next protected action requests authorization again. Do not display grants, tokens, or internal connection identifiers.
9. **Close with proof boundaries.** State that internal Filing Operations receipts are not external filing, formation, provider acceptance, published traffic, leads, conversions, or revenue proof.

## URL acceptance check

Before entering the URL in the portal:

1. Open it in a signed-out private browser window.
2. Confirm playback starts without requesting access or sign-in.
3. Confirm the link is HTTPS, stable, and non-expiring.
4. Watch the full recording once for accidental credentials, personal data, notifications, or private URLs.
5. Record only the final URL, access-check time, and pass/fail result in `submission/portal-prerequisites.json`.
