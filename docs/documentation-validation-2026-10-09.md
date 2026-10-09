# Documentation validation — 9 October 2026

**This is a chronological validation log.** Earlier gap statements and test counts describe their original revision. Current reproduction steps are in the [jury quickstart](jury-quickstart.md); current discovery and financial-gate evidence is in the [final bundle](frankenstein-final-evidence-2026-10-09/README.md).

This revision rewrites the public README and submission copy, adds the user/architecture/jury/video guides, expands the in-app Quick guide and extracts two synthetic CSV fixtures for the later demonstration tasks. It does not change the learning engine or claim a new live-model acceptance run.

## Checks performed

| Check | Result |
| --- | --- |
| Authenticated HQ brief and form | Re-read Frankenstein, common rules, judging weights, field limits and video requirements; form remained an unsubmitted draft |
| Infrastructure suite | **57 tests passed**, 32.317 seconds, using the then-current local working tree |
| Recorded generated skills | Code hashes verified using the repository's canonical `digest()` serialization; **12 of 12 cases replayed successfully in Docker** |
| Live-evidence consistency | Three runs completed; empty conversations; tests precede installation; third run uses two earlier skills, no installation, equal registry hashes and a passing independent preservation check |
| HQ story lengths | What it does: **1,551 / 3,000**; what works: **1,555 / 2,000**; limitations: **1,786 / 2,000** characters |
| Public documentation language | All newly written public guides are English; historical records retain their original text |
| Navigation labels | Matched the concurrent UI update: Library → Skills / Saved workflows / Schedules, Try an example, Prepare room change |
| Quick guide | Opened in the running application; all six sections present; visually checked desktop layout; Explore skills opens Library → Skills |
| JavaScript | `node --input-type=module --check < web/insights.js` passed |
| Documentation links | 78 local targets/anchors checked, no missing targets |
| Publication hygiene | No credential-pattern matches in the newly written public prose or attached test log; this is not a security audit of the entire repository |

The [infrastructure output](documentation-evidence-2026-10-09/infra-tests.txt) and [Docker replay report](documentation-evidence-2026-10-09/replay.json) are attached. The replay is a deterministic re-execution of already generated code, **not fresh generation**, and made no model calls.

Commands used:

```sh
uv run python -m unittest discover -s tests -v
node --input-type=module --check < web/insights.js
git diff --check -- README.md AGENTS.md docs web/insights.js examples
```

The synthetic revised and late-registration CSVs were extracted from the existing showcase fixture and captured reuse input. The walkthrough explicitly uses the reader's own downloaded baseline report, rather than silently loading a historical application state.

## Scope of this validation

The local working tree contains parallel implementation and UI changes. This is not a commit-pinned release validation or a claim about the public repository/freeze snapshot. A clean-clone installation, publication, video recording/upload and HQ submission were not performed by this documentation task. The earlier live evidence remains dated and traceable in the [jury guide](jury-guide.md).

Agent-generated discovery/management and independent dollar-budget enforcement remain incomplete. Native clicks/text entry remain unverified. The documentation does not convert these gaps into successful tests or imply a controlled speed/cost advantage.

## Follow-up: PATCH and BLACKOUT

Reviewed implementation commit `f59f457` and its published learning, fresh-session, Blackout and replay evidence. Updated the jury guide, architecture, HQ copy, demo/pitch scripts, documentation index and in-app Quick guide to include the two features. This is a documentation follow-up, not a new model-generated learning run or HQ submission.

- Full infrastructure suite rerun: **79 tests passed in 52.684 seconds**, including real Docker execution and the Chrome Fieldwork handoff. [Full test output](documentation-evidence-2026-10-09/patch-blackout-tests.txt).
- Credential-free recorded replay in a fresh isolated store: **7 original tests passed**, 16 attendees, 10 seated, 6 waiting; zero model calls and unchanged registry. [Replay report](documentation-evidence-2026-10-09/patch-blackout-replay.json). The optional replay UI did not start because requested port 8791 was already occupied; the recorded-code verification completed before that bind attempt.
- Independently checked the running application on port 8767: Blackout was on, Library → Actions listed learned skills, and the CSV-cleaner preview completed with **0 AI calls**, 18 participants and one duplicate rejected. It explicitly reported no external application change. No apply action was requested.
- JavaScript syntax and diff whitespace checks passed. The new Quick guide section rendered in the browser.
- Revised HQ story fields contain **1,811 / 3,000**, **1,802 / 2,000** and **1,963 / 2,000** characters.

The existing discovery/management and independent dollar-budget gaps remain. The evidence demonstrates bounded saved computation, not general reasoning without a model or zero total cost. Historical evidence and original run outcomes remain unchanged.

## Follow-up: clean reviewer setup after the final fixes

Verified committed implementation `8b22251` from a fresh local Git clone, with no `.env` file or bundled model key. The same Mac supplied the already-installed Git/uv/Python/Node/Chrome/Docker prerequisites and sandbox image; this was not a clean OS installation.

- `uv sync --frozen`: passed and created a new environment from the lockfile.
- `npm ci --ignore-scripts`: passed.
- `uv run python scripts/replay_blackout.py`: passed all 7 saved tests; 16 participants, 10 assigned, 6 waiting; no configured model, 0 calls, unchanged registry.
- A separate normal server on port 8793 returned HTTP 200 for the UI; `/api/health` reported Docker ready and model unavailable, as expected without credentials. It was stopped after verification.
- README and the new jury quickstart now distinguish credential-free replay, confirmed Gemini Free, eligible ChatGPT OAuth plan usage and unsupported API-key/proxy routes. Node 20+ and the native Windows `fcntl` limitation are explicit.
- No new model calls, account authorizations, permission changes or HQ submission were performed for this setup review.

The previous implementation verification passed 99 tests and demonstrated actual generated catalog management and fresh-process composition. Financial evidence remains scoped: original ChatGPT learning predates the gate; later Gemini reuse records strict $0 admission. See the final bundle for failures, prerequisites and limitations.
