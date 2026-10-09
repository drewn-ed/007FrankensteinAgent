# Documentation validation — 9 October 2026

This revision rewrites the public README and submission copy, adds the user/architecture/jury/video guides, expands the in-app Quick guide and extracts two synthetic CSV fixtures for the later demonstration tasks. It does not change the learning engine or claim a new live-model acceptance run.

## Checks performed

| Check | Result |
| --- | --- |
| Authenticated HQ brief and form | Re-read Frankenstein, common rules, judging weights, field limits and video requirements; form remained an unsubmitted draft |
| Infrastructure suite | **57 tests passed**, 32.317 seconds, using the then-current local working tree |
| Recorded generated skills | Code hashes verified using the repository's canonical `digest()` serialization; **12 of 12 cases replayed successfully in Docker** |
| Live-evidence consistency | Three runs completed; empty conversations; tests precede installation; third run uses two earlier skills, no installation, equal registry hashes and a passing independent preservation check |
| HQ story lengths | What it does: **1,556 / 3,000**; what works: **1,555 / 2,000**; limitations: **1,786 / 2,000** characters |
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
