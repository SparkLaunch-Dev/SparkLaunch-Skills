---
title: Prepare and share a SparkRoom investor room
summary: Prepare reviewed room contents and create or revoke bounded investor access.
---

# Prepare and share a SparkRoom investor room

Use `sparklaunch-sparkroom` for its host-managed OAuth, effective Growth access,
privacy, confirmation and write-recovery rules.

Retain identifiers and versions only for internal tool calls; use human-readable
names and omit identifier/version labels or columns from user-facing output.

1. Select the project with `projects.list`; inspect `projects.get` permissions.
2. Find the intended room with paginated `sparkroom.list`, or create an empty
   private room with `sparkroom.create` and one stable idempotency key.
3. Read `sparkroom.get` and paginated `sparkroom.list_documents`. Ask only for
   missing document-selection preferences. Explain that metadata does not prove
   document completeness or content review. Upload missing files in SparkLaunch.
4. Prepare `sparkroom.add_documents` with explicit reviewed revisions, the
   current room version and a stable key. Show its confirmation preview and
   wait for approval. Submit the same arguments/key and confirmation token;
   read back pinned contents. Any existing room links may expose additions
   according to their current permissions.
5. If sharing was requested, review the room's named contents, changing linked
   or live sources, permission, expiry and use limit. Prepare
   `sparkroom.create_share_link`; wait for explicit approval of the preview,
   then submit the same arguments/key and confirmation token.
6. Present the new bearer link and its controls. No invitation was sent. Verify
   privately with `sparkroom.list_share_links`; opening a public link consumes
   usage. Password-protected links and invitations stay in SparkLaunch.
7. Use `sparkroom.get_analytics` for aggregate usage. If the user requests ending
   access, prepare `sparkroom.revoke_share_link` using fresh readback, review its
   preview and confirm the exact action. Any other links are unaffected; prior
   downloads, if any, cannot be recalled.

On stale state, read the room again and prepare a newly reviewed action. On an
uncertain write, follow same-key recovery; never silently repeat link creation.
Do not infer diligence readiness from titles, treat counts as unique investors,
expose private diagnostics, or claim that a handoff uploaded files or sent mail.
