# Final capability-management and budget verification

Recorded on 9 October 2026. The event and people are synthetic; model requests, generated code, Docker tests and registry operations are real. This evidence does not establish customer demand or universal reliability.

## Learning and fresh-process composition

1. [Learning run](learning-chatgpt.json), `6bacaed7078449a0a39d992f1e2ac609`: **17 ChatGPT model calls**. The starting project scope contained one older shared cleaner, explicitly included in `registry_before_records`; it was not an empty registry. Its hash matches the recorded starting hash. The agent created a group-aware roster cleaner (4 tests), a group allocator (3 tests), and a discovery/index-management plugin (7 tests). The latter indexes current tested capabilities and searches by query and accepted input fields. The task requested a useful coordinator handover, without naming a tool to implement. The result was 16 people, 10 seated and 6 waiting.
2. [Fresh-process run](fresh-session-strict.json), `bf47b3caa23b48cea2f7383f875976e5`: a separate Python process, empty conversation, the same persisted registry, a closed room and a new two-person booking. **3 Gemini calls**. The generated discovery plugin ran, then the planner called both previously generated domain skills. No skill was installed, no IDs were wired by the verification harness, and the registry hash remained unchanged. Result: 18 people, 8 seated and 10 waiting.
3. [Independent outcome checks](independent-event-check.json) validate the nonempty results, source cleaning, data passed between skills, group integrity, preferences, room capacity and closed-room handling. They rerun the actual generated allocator in Docker. Its original three model-authored unit tests were weak (empty-roster cases); the additional checks are explicitly team-written verification, not fabricated original tests.
4. [Catalog lifecycle checks](management-check-complete-chain.json) rerun the actual generated catalog with synthetic registry fixtures: a new version, deactivation and rollback. Index contents follow the active tested version; lookup does not change the registry or permissions. These checks use zero model calls.

All new capabilities retain `permissions: ["compute"]`. The generated catalog supplies index/search logic. SQLite persistence, permissions, installation, version activation and the plugin protocol remain fixed team-written infrastructure.

## Financial limit and its scope

The first ChatGPT learning run used a process started **before** the new monetary gate. It is not evidence of a dollar-bounded learning run. The fresh-process Gemini run uses the new **strict 0 USD gate**, with a reservation recorded before every model request.

The gate rejects unknown-price routes before inference and retains reservations after transport failure. The supported zero-cost route requires an allowlisted Gemini model and the operator's explicit confirmation that the Google project is Free with billing disabled. Wisp does not verify Google billing or force a provider-side free-only request. There is no automatic paid fallback. Optional `existing_plan` mode has no local USD guarantee and is outside the strict configuration.

Financial boundary and HTTP-admission tests are in `tests/test_spend.py`; generated-catalog contract and sandbox tests are in `tests/test_track_completion.py`. A displayed cost estimate alone is not this gate.

## Retained failures and test ownership

The `gemini-*.json` files preserve six unsuccessful attempts made during verification. Early attempts produced contradictory model-authored catalog tests; another generated a working catalog but failed its combined domain capability; the last failed JSON parsing before installation. [Partial-run management checks](management-check.json) transparently use the catalog from that failed overall run and are separate from the successful same-registry chain above.

The runtime now classifies a catalog-shaped manifest into the fixed discovery protocol, checks model-authored expectations against a **team-written test-only oracle before any candidate code exists**, allows one bounded test-author correction, and retains the independent platform cases. The oracle does not serve production searches. Incorrect tests or implementations still block installation. Runtime generated code remains in the networkless Docker sandbox.

## Reproduction

To verify the published generated code and results without model credentials:

```sh
uv run python scripts/check_frankenstein_evidence.py
```

This runs real Docker checks against the published artifacts and refreshes the two derived verification reports. It makes no model calls.

For fresh generation with your own confirmed Gemini Free credentials and Docker, run these as two separate processes:

```sh
uv run python scripts/verify_frankenstein.py --phase first
uv run python scripts/verify_frankenstein.py --phase second
```

This harness starts a new empty registry, unlike the recorded successful learning run's explicit shared baseline. Each attempt retains a uniquely named evidence file. Model output is nondeterministic; the retained failures show why fresh regeneration is not guaranteed. The second phase verifies discovery, two prior task capabilities, no installation and unchanged permissions/registry. It does not manually select their IDs.

The older [PATCH/BLACKOUT evidence](../patch-blackout-evidence-2026-10-09/README.md) and credential-free replay remain available. A replay is not fresh agent generation. Native desktop operation, public hosting, video publication and HQ submission are not established by this evidence.
