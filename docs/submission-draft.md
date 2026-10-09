# HQ submission copy

Prepared in English on 9 October 2026 against the current code, recorded evidence and authenticated [HQ form](https://hq.agents007.ai/submit). **Prepared locally, not submitted.** The copy uses **Workspace**, the existing application label, rather than introducing a new brand. Final naming and the video link still need to be settled before submission.

Only the text inside each block belongs in its corresponding field. Character limits are 3,000 / 2,000 / 2,000 for the three story fields. Do not paste the checklist or editorial notes into those fields.

## Project name

<!-- hq:project_name -->
```text
Workspace
```

## One-line pitch

<!-- hq:pitch -->
```text
An agent workspace that turns missing steps into tested skills and combines them for the next task.
```

## What it does — maximum 3,000 characters

<!-- hq:what_it_does -->
```text
Workspace is a local work environment for people who repeatedly prepare data and operate applications. The product hypothesis: useful task logic should survive the conversation, so the next task can build on work that has already been tested.

Our concrete user is an event organizer. A messy registration file must become a valid workshop seating plan. When a room closes, the organizer needs a revised plan that respects capacity and preferences while keeping unaffected bookings intact.

The user gives an outcome and source files. The agent identifies a missing operation, declares its JSON interface and compute-only permission, writes Python, runs tests in Docker and registers the skill only if it passes. A fixed browser connector applies results in the connected application and captures the downloaded report. In a new chat, the planner can combine earlier skills without asking the user to wire them together.

The intended value is reusable operational logic with visible evidence: source, versions, tests and outcomes. Corrections can become regression cases, and replacement versions must preserve earlier tests. Projects, files, saved workflows, schedules and usage history make this a working environment around that loop.

Built solo by David. The demonstrated scenario uses synthetic data in Fieldwork, a local event app. Customer demand and productivity gains have not been measured. Agent-created discovery/management and an independent monetary budget remain incomplete, so we do not claim the full Frankenstein checklist is satisfied.
```

## What works end-to-end — maximum 2,000 characters

<!-- hq:what_works -->
```text
Three recorded live runs use ChatGPT model gpt-6.1-sol, real Docker tests and a separate Chrome session. The attendees and target event app are synthetic; the executions are real.

1. Open the event: 28 CSV rows become 24 valid attendees, all 24 seated. The agent creates separate CSV normalization and preference/capacity allocation skills, passes four tests for each, imports the roster, applies the checked plan and downloads the report.

2. Room closure: the revised roster has 25 attendees. Hall A closes and Agents lab moves to an 8-seat room. The agent reuses normalization and creates a tested replanning skill. Result: 22 seated, 3 waiting, with unaffected bookings preserved.

3. Fresh-chat reuse: another late registration brings the roster to 26. With no prior conversation and an explicitly attached baseline report, the agent combines the earlier normalization and replanning skills. Result: 22 seated, 4 waiting and an exported report. No skill is installed and the registry hash is unchanged.

The repository includes prompts, event logs, code, schemas, test results, provenance and captured application states. A separate check verifies preservation of unaffected seats. All three generated skills remain compute-only; the connector keeps the same browser origin. New input files are explicitly supplied by the user.

The application also supports version inspection, correction with retained tests, deactivation, task cancellation, file transfer and persistent local schedules. See docs/jury-guide.md for evidence and reproduction steps.
```

## What is simulated, missing or fragile — maximum 2,000 characters

<!-- hq:limitations -->
```text
Fieldwork, attendee records and event conditions are synthetic. The target application, browser connector, registry and outcome verifier are team-written infrastructure. Only the documented generated skills are claimed as model-created.

Agent-created discovery/management has not been demonstrated. The catalog protocol and UI search do not satisfy that requirement by themselves. Calls, elapsed time and repair attempts are bounded in code, but there is no independent dollar budget. Gemini requires user-confirmed Free-tier status; ChatGPT uses authorized account allowances. Billing is not verified and usage estimates are not spending enforcement. There is no automatic paid API/provider fallback.

The fresh-session evidence uses an empty conversation with persistent skills and explicit inputs, not a full process restart between all three browser tasks. Generated tests may misunderstand the contract. The showcase verifier checks defined constraints and preservation, not global optimality or arbitrary intent.

Five earlier Gemini attempts failed; their IDs and reasons remain in the evidence. Quota, transport errors or generated test failures can stop a new run. The successful runs used an explicitly selected ChatGPT connection, not a hidden fallback.

Browser control allows one origin and blocks redirects/WebSockets. Other websites and native apps require human outcome review. The macOS bridge compiles, but actual native clicks/typing await permission and validation. Schedules require the local server to remain running and the computer awake. Binary files can be transferred but are not interpreted. Team sharing, external MCP integration and always-on hosting are absent. Demand, time savings, comparative performance and a full accessibility audit are unverified.
```

## Stack and partner tools — optional

<!-- hq:stack -->
```text
Python 3.11+, SQLite, Docker (Python 3.12 sandbox), JSON Schema, HTML/CSS/JavaScript, Node.js + Playwright + Google Chrome. Gemini API and explicitly selected ChatGPT plan connection; successful event evidence used gpt-6.1-sol. Experimental native macOS bridge in Swift. No ElevenLabs integration.
```

## Links

- Repository: [drewn-ed/007FrankensteinAgent](https://github.com/drewn-ed/007FrankensteinAgent). Verify the public commit actually includes the implementation, runtime assets, lockfiles and these guides; working-tree files alone are not visible to the jury.
- Live demo: optional. The app currently runs locally; do not enter `localhost` or `event.workspace.demo` as a public demo URL. A marketing landing page is not a hosted application.
- YouTube Unlisted video: **not supplied**. Insert only a real playable link, no placeholder.
- Best ElevenLabs Use: current implementation has no ElevenLabs integration; the existing evidence does not justify entering that side prize.

## Final publication checklist

The verified deadline is **9 October 2026, 07:14 Europe/Prague**. Later commits are not judged. This checklist records unfinished publication work, not a claim it has happened.

- [ ] Settle the displayed project name and use it consistently in HQ, video and repository.
- [ ] Review the three story fields against the final evidence; retain every remaining limitation.
- [ ] Record a running-product demo, no longer than 90 seconds; retain failures and label speedups/synthetic data.
- [ ] Upload the video to YouTube as Unlisted and verify playback from the jury's perspective.
- [ ] Commit and push the reviewed implementation, required assets, examples, evidence and documentation. Exclude credentials, private runtime databases and raw HQ exports.
- [ ] Verify a fresh clone of the intended public branch starts using the README; record the exact commit in the submission evidence.
- [ ] Confirm the repository link on the HQ team page and in the submission form.
- [ ] Paste the final copy and actual video URL into HQ; review public-results consent and optional fields.
- [ ] Submit the project explicitly and verify submitted status before the freeze. Autosaved DRAFT is not submitted.
- [ ] Rehearse the separate [60-second live pitch](demo-script.md#60-second-live-pitch).

The discovery/management and monetary-budget gaps are product gaps, not items that documentation can mark complete. The [jury guide](jury-guide.md) preserves their status even if submission proceeds.
