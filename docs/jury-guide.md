# Jury guide

**Wisp · 007 Frankenstein — solo prototype by David.** Documentation reviewed on 9 October 2026. The [Frankenstein brief](https://hq.agents007.ai/topics#frankenstein) and [submission form](https://hq.agents007.ai/submit) were re-read in authenticated HQ on that date. No submission was made by this documentation update.

## The user and the value

The intended user repeatedly prepares operational data and acts on it in an application. Our concrete example is an event organizer handling messy registrations, workshop preferences and a room closure. The useful output is a checked seating plan and downloadable report, with every attendee accounted for and unaffected bookings preserved.

The product hypothesis is that validated task logic should survive the conversation: create a missing operation once, keep its contract and tests, and combine it with earlier operations when the next task changes. The prototype adds test-gated activation, correction with retained regressions, and visible provenance. This is a proposed useful combination, not a claim to have invented self-extending agents or outperformed existing products. No customer study or controlled time/cost comparison has been completed.

## Recorded demonstration

Start with the [summary](operations-evidence-2026-10-09/summary.json), then inspect each complete evidence file:

| Evidence | Observable result | Skills |
| --- | --- | --- |
| [First task](operations-evidence-2026-10-09/first-task.json), run `5b8453c25ac6449dbc2d94c6de58f34e` | 28 CSV rows → 24 attendees, 24 assigned, 0 waiting; report downloaded | Creates normalization and allocation |
| [Room change](operations-evidence-2026-10-09/room-change.json), run `daf5ccc0cdfb4613a480a6cea12032b4` | 25 attendees, 22 assigned, 3 waiting; unaffected bookings preserved | Reuses normalization, creates replanning |
| [Fresh-chat reuse](operations-evidence-2026-10-09/reuse-task.json), run `ede440fdec46485e93f93a1221beaf84` | 26 attendees, 22 assigned, 4 waiting; report downloaded | Reuses normalization and replanning, creates nothing |

The [generated artifact bundle](operations-evidence-2026-10-09/generated-skills.json) contains code, manifests, schemas, hashes, provenance and cases/results for:

- `peventops_normalize_registration_csv`, version 1, four passing recorded cases.
- `peventops_allocate_preferred_workshops`, version 1, four passing recorded cases.
- `peventops_replan_preserving_unaffected_assignments`, version 1, four passing recorded cases.

All declare `permissions: ["compute"]` and `provenance.source: "agent"`. Their project is `event-ops-chatgpt`. Skill IDs are evidence identifiers, not instructions injected into the user's tasks.

For creation, inspect `gap → test_plan → tests_passed → installed → used` events. For reuse, inspect `run.conversation: []`, the two earlier IDs in `used`, absence of `installed`, and equal `registry_before` / `registry_after` hashes. The latter hash is `9c9fa5e2c0f56eb2f00d8f3926430b7f0d624f1ec8db93b7b2a32cd4a4dd41b0`. The first registry hash corresponds to an empty list.

These runs prove a new conversation using declared persistent skills and explicit input files. They do not establish a complete OS-process restart between all three browser tasks. File IDs change when the user supplies new inputs; the skill permission remains compute-only and the browser origin remains the same.

The successful runs used `gpt-6.1-sol`: 15, 15 and 11 model calls, approximately 216, 173 and 81 seconds. Different tasks and different creation/reuse states make these unsuitable for a speedup claim. Five earlier Gemini failures are retained in the summary, including failed tests, invalid JSON, an unknown action and exhausted quota. Provider selection was changed explicitly for validation, not by an automatic fallback.

## PATCH and BLACKOUT: additional recorded proof

**PATCH** exposes active, tested compute skills as editable actions in **Library → Actions**. **BLACKOUT** persistently blocks model tasks, corrections and scheduled model dispatches while those actions continue to run in Docker. Previewing does not modify the application; the fixed Fieldwork adapter requires a separate operator action and verifies the result.

The [additional evidence bundle](patch-blackout-evidence-2026-10-09/README.md) records:

| Stage | Observed result |
| --- | --- |
| Learning | 9 model calls; agent-created CSV cleaner and group-preserving allocator; 3 + 4 passing tests. 17 rows → 16 attendees, 10 seated / 6 waiting with capacities 5/4/4. |
| Fresh conversation | Hall A closed and a late pair added: 18 attendees → 8 seated / 10 waiting. Both existing skills used in 3 model calls; no installation; unchanged registry. |
| Blackout | Both saved actions executed with 0 model calls and an unchanged registry; a new AI task was rejected. Explicit roster replacement and allocation were checked in Chrome. Different Fieldwork capacities of 10/8/6 seated all 16. |
| Credential-free replay | Original code hashes checked, all 7 original tests rerun in Docker, 16 attendees → 10 seated / 6 waiting reproduced without a configured model. |

A preceding failed learning attempt is retained. Zero model calls applies to the later local executions, excluding learning and hardware costs. Blackout does not disconnect the internet or interpret new natural-language tasks without AI. PATCH forms and the adapter are team-written infrastructure, not agent-created discovery/management. The allocator preserves groups deterministically; it does not optimize global seat utilization.

To inspect the recorded actions without model access, run `uv run python scripts/replay_blackout.py --serve` after the README setup, then open [localhost:8789](http://127.0.0.1:8789). On subsequent runs supply a fresh `--data-dir`; the script refuses to replace an existing registry. This is explicitly labeled recorded-code replay, not fresh generation or autonomous wiring.

## Frankenstein requirements

| Requirement | Current assessment | Evidence or gap |
| --- | --- | --- |
| A real task reveals a missing capability | Demonstrated on synthetic operational inputs | `gap` events and task text in the first/room-change runs |
| Agent creates, tests and registers a useful capability | Demonstrated | Generated code, separate test-author context and passing tests before installation |
| First task produces a useful result | Demonstrated within Fieldwork | Roster, applied allocation, browser actions, outcome check and export |
| Agent builds/extends discovery and management tooling | **Not demonstrated** | Catalog protocol, registry and UI search are team-written; no successful generated discovery artifact in this evidence |
| Different task combines earlier capabilities in a fresh session | Demonstrated as a fresh conversation | Empty conversation, two earlier skills used, no installation, unchanged registry hash |
| Generated code stays in a sandbox | Implemented and tested within the documented boundary | Docker configuration and negative infrastructure tests |
| Capabilities grow without granting themselves more authority | Supported within the recorded boundary | Compute-only manifests, fixed origin, explicit input files; not an adversarial security proof |
| Self-iterations are capped in code | Implemented | Call/time limits, bounded repair and format retry |
| Spend per run is capped in code | **Incomplete** | Free-tier confirmation/no fallback and operational bounds; no independent dollar cap or billing verification |
| Operator control is visible | Implemented; several paths tested | Evidence, versions, deactivate/reactivate, Stop and external-action review |

**The full track is not claimed as complete.** In particular, do not relabel the handmade registry or passing catalog fixture tests as agent-created management.

## What is real, synthetic or still unverified

- **Real executions:** model responses, generated Python, Docker tests, version registration, browser uploads/actions/downloads and persisted task evidence.
- **Synthetic scenario:** Fieldwork, attendees, event configuration and the source CSVs. Fieldwork and its verifier are handwritten infrastructure.
- **Bounded outcome check:** source fidelity, accounting, preferences, capacities, an applied allocation and the separately recorded preservation check. It does not prove optimality or all possible user intent.
- **Native desktop:** helper build, app inventory and denied-permission behavior checked; live clicking/typing awaits permission and validation.
- **Other limits:** one browser origin, blocked redirects/WebSockets, no team sharing or external MCP integration, server required for scheduling, model quota dependence and no completed accessibility audit.

## Reproduce and inspect

For installation choices, prerequisites and the optional macOS Accessibility setup, start with [How the jury can try it](../README.md#how-the-jury-can-try-it). This version runs locally from source. The browser demonstration does not need Accessibility or a separately downloaded bridge; native control adds a locally compiled helper and manual permission on the reviewer's Mac.

Follow the [user guide](user-guide.md#event-walkthrough) to run the three tasks. Use the same project and live target state, but a new chat for reuse. Supply your own step-2 report as the step-3 baseline. Do not seed the registry with the published generated code and call it fresh generation.

Run `uv run python -m unittest discover -s tests -v` from the repository root for infrastructure checks. Docker, its Python image, Node dependencies and Chrome are required. Fixture tests do not call a live model and do not establish the full competition result. [Build validation notes](build-validation.md) record implementation and UI checks; [operations notes](operations-extension-2026-10-09.md) describe the original live acceptance work.

## Submission readiness

HQ gives 35% to user value/track relevance, 25% to originality, 20% to an end-to-end result, 10% to technical execution and 10% to validation/honest limits. The user/problem above addresses value; the artifact trail supports execution; the incomplete rows remain visible.

Required publication items are the public repository, English project fields and a playable **YouTube Unlisted video no longer than 90 seconds**, submitted before **9 October 2026, 07:14 Europe/Prague**. The separate stage pitch is **60 seconds**, per the organizers' message relayed by David. See [submission copy and checklist](submission-draft.md) and [video/pitch scripts](demo-script.md).

At this documentation review the HQ form was an unsubmitted draft with empty project and link fields. Local documentation, a draft form and a video script do not establish submission, upload or inclusion in the freeze snapshot.
