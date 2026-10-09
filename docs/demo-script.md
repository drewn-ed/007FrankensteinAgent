# Demo video and live pitch

These are English production scripts, not a claim that a video has been recorded or uploaded. Use the confirmed product name **Wisp** consistently. Fieldwork is the synthetic target app, not the agent's name. Source requirements: [HQ submission](https://hq.agents007.ai/submit) and the organizers' 60-second-pitch clarification relayed by David on 9 October 2026, summarized in the [brief](hackathon-brief.md).

## 90-second submission video

The jury needs a running product and traceable outcomes. Aim for 85–88 seconds to leave export margin. Use actual captured runs; label archival playback **Recorded live run** and accelerated waiting **Waiting sped up**. Show the starting registry before claiming creation. Never hide a failure or replace model execution with a seeded skill.

| Time | Screen / evidence | English narration |
| --- | --- | --- |
| 0–15 s | Wisp, source CSV and group bookings. Label: **Synthetic event data · real execution**. | “An event organizer needs clean registrations and a seating plan that keeps groups together. Wisp learns the missing operations and keeps them as tested tools.” |
| 15–34 s | Original empty registry, task, gap, contracts, 3 + 4 passing tests and installed versions from the group-booking learning evidence. | “The agent writes a CSV cleaner and a group allocator. Seven tests pass in Docker before activation. Seventeen rows become sixteen attendees: ten seated, six waiting.” |
| 34–48 s | Library → Actions; editable input and actual preview. | “PATCH turns those tested interfaces into usable actions. Change the input, preview the result and download it. Applying it in Fieldwork is a separate, explicit step.” |
| 48–63 s | Blackout on, actual saved-action result, **0 AI calls**, unchanged registry. | “BLACKOUT pauses AI. Saved actions keep running locally with zero model calls. This is tested code execution, not offline reasoning.” |
| 63–77 s | Fresh-conversation evidence: Hall A closed, late pair; earlier IDs used, no installation, equal hashes; **8 seated / 10 waiting**. | “With AI enabled, a different task in a fresh chat combines both existing skills. Nothing is rebuilt.” |
| 77–90 s | Failed-attempt record and concise limits over actual UI. | “The earlier learning failure is retained. Data is synthetic; execution is real. Agent-built management and a dollar cap remain unfinished. Zero calls excludes earlier learning.” |

Use the [group-booking evidence](patch-blackout-evidence-2026-10-09/README.md) for this sequence. The learning/replay capacities 5/4/4 produce 10 seated / 6 waiting; the separate Fieldwork handoff uses 10/8/6 and seats all 16. Do not mix these outcomes or present manual action selection as autonomous composition. The fresh-chat evidence is a separate AI-planned run, using three model calls.

Keep gap → test → install legible and retain failures. A credential-free replay must be labeled **Recorded-code replay**, not fresh learning. Show versions/evidence and Stop as operator controls. End with the repository name; add the video URL only after upload. This script does not establish that any recording or submission is complete.

## 60-second live pitch

Focus on two messages: learning creates tested tools, and those tools remain useful when AI is paused. Rehearse at your natural pace.

> What if the work an AI agent learns could become a tool you keep?
>
> Wisp starts with a real task. In our example, an event organizer needs clean registrations and a seating plan that keeps groups together. The agent writes the missing skills, tests them, and saves them.
>
> PATCH turns those skills into actions with editable inputs and visible results. BLACKOUT pauses AI, but the saved actions keep working locally with zero model calls.
>
> In a fresh conversation, another task combines earlier skills without rebuilding them. Yesterday's work becomes useful again.
>
> The prototype uses synthetic event data and real execution. Agent-built skill management and a monetary cap are still unfinished; zero calls excludes the earlier learning.

One supporting screen is enough: **Learn → Test → Run again with AI paused**. Keep AI-planned fresh-session composition distinct from direct local action execution.

## Questions the jury may ask

| Question | Evidence-based answer |
| --- | --- |
| What did the agent actually create? | The original three event capabilities, plus the cleaner and group allocator in the separate PATCH/BLACKOUT evidence bundle, with their recorded tests. The app, sandbox, connector and registry are team-written. |
| How do we know it reused them? | Empty conversation, earlier skill IDs/versions in `used`, no `installed` event and identical registry hashes in the third run. |
| What changed when it learned? | Executable skill code and tests in the registry; not model weights or broader permissions. |
| Why would a user want it? | To keep task-specific rules and corrections for later work. The event example produces a checked report; real-world demand and time savings remain hypotheses. |
| Does it fulfill all of Frankenstein? | No. Agent-generated discovery/management is not demonstrated, and operational bounds are not an independent dollar cap. |
| Is the demo a mock? | The event and attendees are synthetic. Model generation, Docker tests, browser changes and exports actually ran. |
| Does Blackout mean no internet or no cost? | No. It blocks Wisp model execution; saved compute actions run in Docker. Initial learning and local compute still have costs, and external applications may need internet. |
| Is it always-on or universal computer control? | No. Schedules need a running local server; browser control has one-origin limits, and live native control remains unverified. |

See the [jury guide](jury-guide.md) for the supporting files. The landing launch film is a separate marketing artifact and does not replace this running-product submission video.
