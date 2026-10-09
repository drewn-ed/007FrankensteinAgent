# Focused security review — 9 October 2026

This is a targeted code and runtime review of the local Wisp prototype, not a penetration-test certification or a guarantee against every vulnerability. It covers provider credentials, repository exposure, local HTTP boundaries, generated-code isolation and unintended inference spending.

## Findings fixed

1. **Existing runtime data permissions.** The live `.runtime` directory was mode 0755 and its SQLite database 0644. This could expose task history to another OS user able to traverse the project directory. Store initialization now enforces directory 0700 and database 0600, including an existing workspace. The current workspace was tightened without deleting data. `.env` was already 0600; ChatGPT credentials have their own private directory/file handling.
2. **Credential-bearing provider redirects.** Gemini used the default urllib redirect handler. A redirect response could forward the custom API-key header to a different destination. The adapter now rejects redirects before a second request. A regression test uses a synthetic key and two loopback HTTP servers; the second server receives no request. No actual key disclosure was observed. ChatGPT already rejected redirects.
3. **External navigation review.** Agent-requested navigation on an external site now requires the same operator review as clicks and text entry. A GET endpoint can change state, so navigation is not assumed harmless. Declining the operation prevents the browser request. Only the included synthetic showcase origins retain their existing review exemption; read-only page inspection remains available.

## Checks and evidence

- **Git history:** all 777 locally reachable Git blobs were scanned for the currently known local keys/tokens and common credential patterns; no matches. This does not detect every possible secret format or establish that a previously revoked unknown key never existed elsewhere.
- **JavaScript dependencies:** `npm audit --omit=dev` reported no known vulnerabilities.
- **Python dependencies:** the complete pinned dependency export was checked with `pip-audit`; no known vulnerabilities were reported for its 10 packages. Advisory coverage does not prove absence of undiscovered vulnerabilities. No runtime dependency was upgraded by this audit.
- **Focused suite:** 41 security, spend, usage, OAuth and sandbox tests passed after the first two fixes. After all three fixes, the full automated suite passed: **104 tests in 67.423 seconds**, including the external-navigation regression.
- **Local HTTP:** regression requests with an attacker Origin, an attacker Host or Origin `null` are rejected before changing Blackout. The server binds to 127.0.0.1. Mutation routes require JSON; no broad CORS access is enabled.
- **Generated code:** Docker execution has no network, no host credential mounts, a read-only root, unprivileged user, dropped capabilities and bounded CPU/memory/process/time/output use. Infrastructure tests check failed-test rejection, permission escalation, missing credentials, network isolation and timeout/output stops.
- **Observed live financial state:** provider Gemini, `SPEND_POLICY=strict`, `MAX_RUN_USD=0`, zero enabled schedules. No paid inference or real provider call was made as part of this review.

## Financial and security boundaries that remain

- Strict $0 admission relies on the operator's truthful confirmation that the Gemini project is Free and billing stays disabled. Wisp does not verify Google billing or set a provider-side free-only flag. Enabling paid billing outside Wisp invalidates that assumption.
- Optional `existing_plan` ChatGPT mode uses provider-managed allowance/credits and has no local dollar guarantee. A local estimate is not an invoice. The inference budget does not cap purchases or other financial actions you approve on external websites.
- The local HTTP service is not a multi-user authenticated service. Other processes running with local access can call it. Do not expose it through a public tunnel, change its bind address to a public interface, or deploy it as a shared server without authentication and a separate security review.
- Task data and readable attachments are intentionally sent to the selected model during AI work. BLACKOUT prevents model calls, but does not encrypt local data, revoke existing credentials or disconnect the computer from the internet.
- External browser/native actions require human review. Model output and website content can still be wrong or adversarial; approval is not proof of correctness. Native Accessibility interaction remains experimentally unverified.
- Keep Docker and the host OS updated. Container isolation is a boundary, not proof against every kernel/container vulnerability. This audit did not reproduce arbitrary browser exploits or audit all native bridge behavior.

For lowest exposure during jury review, use the credential-free recorded replay described in [jury quickstart](jury-quickstart.md). It makes no model calls and uses synthetic data.
