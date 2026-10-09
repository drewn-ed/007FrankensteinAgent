# Demo video and live pitch

These are English production scripts, not a claim that a video has been recorded or uploaded. Use the current **Workspace** label consistently. Fieldwork is the synthetic target app, not the agent's name. Source requirements: [HQ submission](https://hq.agents007.ai/submit) and the organizers' 60-second-pitch clarification relayed by David on 9 October 2026, summarized in the [brief](hackathon-brief.md).

## 90-second submission video

The jury needs a running product and traceable outcomes. Aim for 85–88 seconds to leave export margin. Use actual captured runs; label archival playback **Recorded live run** and accelerated waiting **Waiting sped up**. Show the starting registry before claiming creation. Never hide a failure or replace model execution with a seeded skill.

| Time | Screen / evidence | English narration |
| --- | --- | --- |
| 0–15 s | Workspace beside Fieldwork; registration CSV and room capacities. Label: **Synthetic event data · real execution**. | “An event organizer has messy registrations, workshop preferences and limited seats. When a room closes, the plan changes again. Workspace turns the missing steps into tested skills it can use next time.” |
| 15–33 s | Starting registry and outcome-based task. Show gap, generated contract, test results, then installed versions. | “The task exposes the gap. The agent writes separate normalization and allocation skills. Tests run in Docker before activation. Generated skills get compute permission only.” |
| 33–46 s | Actual Fieldwork roster and board, then report download: **24 attendees / 24 seated**. | “Twenty-eight source rows become twenty-four attendees. The browser imports the roster, applies the checked seating plan and downloads the actual report.” |
| 46–59 s | Room-change task: Hall A closed, Studio D selected; new replanning skill and **22 seated / 3 waiting**. | “A room closes. The agent learns replanning while preserving unaffected seats.” |
| 59–75 s | Fresh chat, late CSV plus report attached. Show two earlier skill IDs used, no installation, equal registry hashes, **22 seated / 4 waiting**. | “In a fresh chat, another late registration reuses normalization and replanning. No skill is rebuilt. The registry hash stays unchanged.” |
| 75–90 s | Evidence summary including earlier failed runs; concise limits card over the real application. | “Earlier failed attempts remain documented. The app and data are synthetic. Agent-built discovery and a dollar cap are still missing. The model, tests and browser actions are real.” |

Keep the gap → test → install order legible. The room-change task creates replanning; only the third task demonstrates combining existing skills without installation. Do not collapse these into a false two-task story.

The recording must show real operator controls as part of the UI/evidence: skill versions or deactivate, task steps and Stop. If an external approval or failure occurs in the recorded run, retain it. Do not imply the three browser tasks restarted the server; the demonstrated reset is an empty conversation. End with the repository name; add a video URL to the README/submission only after upload.

## 60-second live pitch

Focus on two messages: useful task logic survives the conversation, and new skills must pass tests. This script is approximately 120 words; rehearse at your natural pace.

> Every time a work process changes, an AI assistant can leave you explaining the same rules again.
>
> Workspace keeps useful task logic. An event organizer gives it messy registrations and workshop capacities. When a room closes, it must preserve existing bookings and produce a new plan.
>
> The agent identifies a missing step, writes a reusable skill, and tests it before activation. In our recorded demo, a fresh chat combines two earlier skills without rebuilding them. The result is a checked seating plan and a downloadable report.
>
> The promise is that yesterday's work becomes part of tomorrow's capability. This prototype demonstrates that reuse; agent-built skill management and a monetary cap are still unfinished.

One supporting screen is enough: **Task → Tested skill → Reuse in a new chat**, with the actual before/after allocation. Avoid filling the minute with stack details or a claim of complete track compliance.

## Questions the jury may ask

| Question | Evidence-based answer |
| --- | --- |
| What did the agent actually create? | The three Python capabilities and their contract tests in the generated-skills bundle. The app, sandbox, connector and registry are team-written. |
| How do we know it reused them? | Empty conversation, earlier skill IDs/versions in `used`, no `installed` event and identical registry hashes in the third run. |
| What changed when it learned? | Executable skill code and tests in the registry; not model weights or broader permissions. |
| Why would a user want it? | To keep task-specific rules and corrections for later work. The event example produces a checked report; real-world demand and time savings remain hypotheses. |
| Does it fulfill all of Frankenstein? | No. Agent-generated discovery/management is not demonstrated, and operational bounds are not an independent dollar cap. |
| Is the demo a mock? | The event and attendees are synthetic. Model generation, Docker tests, browser changes and exports actually ran. |
| Is it always-on or universal computer control? | No. Schedules need a running local server; browser control has one-origin limits, and live native control remains unverified. |

See the [jury guide](jury-guide.md) for the supporting files. The landing launch film is a separate marketing artifact and does not replace this running-product submission video.
