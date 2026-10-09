# HQ submission copy

Prepared in English on 9 October 2026 against the current code, recorded evidence and authenticated [HQ form](https://hq.agents007.ai/submit). **Prepared locally, not submitted.** **Wisp** is the product name confirmed by David on 9 October 2026. The video link still needs to be supplied before submission.

Only the text inside each block belongs in its corresponding field. Character limits are 3,000 / 2,000 / 2,000 for the three story fields. Do not paste the checklist or editorial notes into those fields.

## Project name

<!-- hq:project_name -->
```text
Wisp
```

## One-line pitch

<!-- hq:pitch -->
```text
An agent workspace that turns missing steps into tested skills and combines them for the next task.
```

## What it does — maximum 3,000 characters

<!-- hq:what_it_does -->
```text
Wisp is a local work environment for people who repeatedly prepare data and operate applications. The product hypothesis: useful task logic should survive the conversation, so the next task can build on work that has already been tested.

Our concrete user is an event organizer. A messy registration file must become a valid workshop seating plan. When a room closes, the organizer needs a revised plan that respects capacity and preferences while keeping unaffected bookings intact.

The user gives an outcome and source files. The agent identifies a missing operation, declares its JSON interface and compute-only permission, writes Python, runs tests in Docker and registers the skill only if it passes. A fixed browser connector applies results in the connected application and captures the downloaded report. In a new chat, the planner can combine earlier skills without asking the user to wire them together.

PATCH turns tested compute skills into actions with editable inputs, local previews and downloadable results. BLACKOUT pauses AI while those saved actions keep running without model calls. Supported Fieldwork changes require a separate explicit apply action.

The intended value is reusable operational logic with visible evidence: source, versions, tests and outcomes. Corrections can become regression cases, and replacement versions must preserve earlier tests. Projects, files, saved workflows, schedules and usage history make this a working environment around that loop.

Built solo by David. The demonstrated scenario uses synthetic data in Fieldwork, a local event app. Customer demand and productivity gains have not been measured. The latest evidence includes a generated discovery tool and fresh-process composition. Strict financial admission is demonstrated on the later Gemini reuse; the earlier ChatGPT learning run predates that gate.
```

## What works end-to-end — maximum 2,000 characters

<!-- hq:what_works -->
```text
The latest learning run used 17 ChatGPT calls to create three executable capabilities: a registration cleaner, a group-preserving allocator and an operations catalog. They passed 4, 3 and 7 tests respectively before registration. The catalog builds a current index and finds compatible operations by their metadata and accepted inputs; its algorithm was generated, while its protocol and authority checks are team-written.

A different task ran in a separate Python process with an empty conversation and the saved registry. Hall A closed and a late group arrived. In three Gemini Free calls, the agent executed the generated catalog and combined the earlier cleaner and allocator. Result: 18 attendees, eight seated and ten waiting. No capability was installed or rewritten; the registry hash stayed unchanged. Generated permissions remained compute-only.

This second run used the new strict $0 financial admission policy. The earlier ChatGPT learning process did not have that gate and is not presented as financially capped.

Separate PATCH/BLACKOUT evidence shows editable action inputs, Docker execution with AI paused and zero model calls, plus explicit verified application of results to Fieldwork in Chrome. A credential-free replay reproduces those earlier saved actions. These browser/local-action runs are distinct from the latest creation/discovery run.

The repository retains task inputs, generated code, tests, source run IDs, catalog results, registry snapshots and failures. A portable two-phase verification harness allows reviewers to attempt new learning and separate-process reuse with their own confirmed Gemini Free project.
```

## What is simulated, missing or fragile — maximum 2,000 characters

<!-- hq:limitations -->
```text
Fieldwork and attendee data are synthetic. The application, connector, registry, catalog protocol, permission checks and PATCH forms are team-written. Only the recorded capability implementations are claimed as agent-generated.

The latest allocator passed three generated tests, but all used empty rosters. This is weak coverage, not proof of correct allocation for arbitrary inputs. Actual populated outputs are inspectable. Generated tests and bounded outcome checks do not guarantee correctness or optimality.

The successful learning run used ChatGPT before the monetary gate existed. The later reuse used strict $0 Gemini Free admission. Strict mode blocks unpriced routes before inference, but requires billing to remain disabled in the operator's Google project; Wisp cannot verify billing or force a free-only request. Optional ChatGPT existing_plan mode has no local USD guarantee. There is no automatic paid fallback.

Six additional Gemini attempts are retained, including partial generation and invalid-JSON failures; earlier demonstration failures are retained separately. Fresh learning can stop on quota, transport, generated-code or test failures.

Browser control is single-origin and blocks redirects/WebSockets. Native macOS clicking/typing remains unverified. Schedules need the local server awake. Binary attachments are transferable but not interpreted. There is no team sharing, external MCP integration or always-on hosting.

BLACKOUT runs saved computations without AI; new language tasks still need a model, and external sites may need internet. Zero model calls excludes learning and hardware costs. Customer demand, time savings and accessibility have not been validated.
```

## Stack and partner tools — optional

<!-- hq:stack -->
```text
Python 3.11+, SQLite, Docker (Python 3.12 sandbox), JSON Schema, HTML/CSS/JavaScript, Node.js + Playwright + Google Chrome. Gemini API and explicitly selected ChatGPT plan connection; successful event evidence used gpt-6.1-sol. Experimental native macOS bridge in Swift. No ElevenLabs integration.
```

## Links

- Repository: [drewn-ed/Wisp](https://github.com/drewn-ed/Wisp). Verify the public commit actually includes the implementation, runtime assets, lockfiles and these guides; working-tree files alone are not visible to the jury.
- Live demo: optional. The app currently runs locally; do not enter `localhost` or `event.workspace.demo` as a public demo URL. A marketing landing page is not a hosted application.
- YouTube Unlisted video: **not supplied**. Insert only a real playable link, no placeholder.
- Best ElevenLabs Use: current implementation has no ElevenLabs integration; the existing evidence does not justify entering that side prize.

## Final publication checklist

The verified deadline is **9 October 2026, 07:14 Europe/Prague**. Later commits are not judged. This checklist records unfinished publication work, not a claim it has happened.

- [x] Product name confirmed: **Wisp**. Use it in HQ, video and repository; David has also renamed the GitHub repository to `drewn-ed/Wisp`.
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
