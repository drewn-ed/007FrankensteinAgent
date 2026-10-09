# PATCH and BLACKOUT: recorded verification

These are actual runs on 9 October 2026, using synthetic workshop registrations. No generated capability in this bundle was manually substituted. The fixed UI, executor and Fieldwork adapter are team-written infrastructure.

| Run | Result | Model calls |
| --- | --- | ---: |
| [Preceding attempt](preceding-failed-attempt.json) | Provider stream ended before a complete response. No partial capability was accepted. | 3 |
| [Successful learning](learning.json) | Agent created a CSV cleaner and group allocator, passed 3 + 4 generated tests and used both. 17 source rows became 16 participants; 10 assigned, 6 waiting with room capacities 5/4/4. | 9 |
| [Different task in a fresh session](fresh-session-reuse.json) | Closed Hall A plus a late two-person booking: 18 participants, 8 assigned, 10 waiting. Empty conversation context, both existing capabilities used, no installations, identical before/after registry hashes. | 3 |
| [BLACKOUT and live application handoff](blackout.json) | AI paused; ordinary chat rejected. Cleaner and allocator executed directly in Docker. Explicit roster import and allocation application verified in real Chrome. Fieldwork's different default capacities 10/8/6 accommodated all 16 participants. | 0 |
| [Credential-free recorded replay](credential-free-replay.json) | Seven original tests rerun, original 10-assigned/6-waiting result reproduced in a fresh local store. No model configured. | 0 |

The recorded failed attempt is retained. Learning cost includes that attempt as well as the successful run. “Zero calls” describes subsequent local execution, not the earlier learning phase or all hardware costs.

## Reproduce without model credentials

After the main README's Python and Docker setup, from the repository root:

```sh
uv run python scripts/replay_blackout.py --serve
```

Open [http://127.0.0.1:8789](http://127.0.0.1:8789), then **Library → Actions**. The replay uses a separate `.runtime/blackout-replay` store and starts with Blackout on. Supply a fresh `--data-dir` on subsequent invocations; it refuses to replace an existing registry. Omit `--serve` to run the checks and exit. Browser application handoff additionally requires the normal Chrome/Node setup.

The [replay bundle](replay-bundle.json) contains original generated code, contracts, cases, provenance, inputs and expected output. The script checks code hashes, reruns the original tests inside the networkless sandbox, and records imported skills as `recorded_evidence_replay`. Its two-stage wiring is explicit infrastructure, **not a new demonstration of autonomous discovery or generation**. The separate fresh-session record above is the evidence for model-planned reuse and composition.

## Verification of the implementation

`python -m unittest discover -s tests -v` completed with **79 passing tests** after integration. The new suite includes real Docker execution and Chrome application handoff, paused-model routing, scope/version/test gates, stale snapshots, tampered artifacts, group integrity and CSV validation. Separate browser checks covered desktop and 390 px mobile layout, file import, readable errors and an end-to-end flow with no model credentials.

## What this establishes, and its limits

- Tested skill interfaces become parameterized actions automatically. The user can import inputs, preview results, download them and explicitly hand supported results to Fieldwork.
- Model-free execution does not use a model provider, planner, account or API key. A server-side persisted switch blocks chat, corrections and scheduled model tasks while paused.
- Generated code remains compute-only in Docker. Browser changes use a fixed, separately invoked adapter after operator action. Rich allocation results are projected to explicit participant/workshop IDs; the original explanations remain in the preview and evidence.
- Application verification checks the source roster, unique accounting, preferences, capacity, group integrity and the applied result. Stale context and changed inputs invalidate the preview. A failed/uncertain apply is not automatically retried.
- These checks do not establish optimal seat utilization or universal correctness. The group policy is deterministic first-member order, not a global optimizer. The generated allocator explicitly rejects multiple concurrent workshops sharing a room.
- Blackout is a block on Wisp's model execution, not disconnection of the computer's internet. Arbitrary new natural-language work requires AI. The generic offline feature handles saved computations; browser-plan and native-control skills are excluded.
- The bundled Fieldwork handoff does not provide a universal connector for arbitrary websites. This experiment does not establish agent-created discovery/management, an independent dollar budget or complete satisfaction of every Frankenstein requirement.
