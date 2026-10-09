# Functional review fixes

Follow-up to [the independent functional review](functional-review-2026-10-09.md), 9 October 2026. The original report and its evidence are preserved. This is a verification of concrete fixes, not a claim that the whole product or Frankenstein submission is complete.

## Changes and evidence

| Finding | Change | Verification |
| --- | --- | --- |
| Ordinary chat lost the previous result | Server selects up to six recent turns from the same chat and project, preserving actual inputs/results. New chat stays clean. Explicit references to an absent prior result request input. | A real CSV task returned Mira, Kai and Noah. An ordinary subsequent message, without Follow up, returned Noah, Kai, Mira. A new chat with no source returned `needs_input` with zero model calls. |
| A second tab could erase a project | Three-way merge by record and changed field; conflicts reject the whole write. UI retains local edits, supports export, and offers loading the saved version. Old clients without a base snapshot must reload. | Two actual UI tabs preserved both new projects. A conflicting instruction edit preserved the first saved value; the second edit was visible in the exported unsaved snapshot. Unit tests also cover disjoint fields, deletions and atomicity. |
| Redirect crossed the selected origin | Browser requests use `route.fetch(maxRedirects=0)`, rejecting redirects before a destination request. WebSocket connections are blocked. | Before the fix, the original probe recorded a hit on the second server. After the fix, a real Chrome regression test recorded zero hits for both a redirected image and redirected navigation. |
| False browser success | Whole-token text checks reject `1 registered` inside `11 registered`. A task with no browser action cannot complete. The practice app has a fixed independent outcome adapter checking exact count and all name/email/workshop/check-in fields against DOM records. Other sites end as `needs_review`. | Negative tests reject wrong counts, email, workshop and check-in state, and a model claiming completion without actions. Real registration runs passed full-record verification. The fixed outcome adapter is team-written, not an agent-created capability. |
| Equivalent generated plans failed exact JSON tests | Tests compare values committed by each action group, permit reordered setters and additional assertions, and retain all independently authored required assertions. Wrong values and missing assertions still fail. Planner receives its remaining call budget and prefers reusable plans for repeated multi-step work. | Regression tests exercise equivalent order, extra checks, wrong values and omitted checks. A new model-authored plan passed 3/3 cases, executed ten steps and registered two participants in six model calls. Two subsequent clean sessions each used that plan in three calls without installing anything. |
| Project memory and registry hashes had inconsistent scopes | Application maps use a project-scoped table; legacy maps stay personal. Registry before/after uses the same project-plus-shared scope and records that scope. | Isolated tests prove project B cannot read A's map and that unrelated project capabilities do not enter the starting hash. |

The final full suite passed **41 tests** with real Docker and Chrome. The local transcript is `.runtime/review-fixes/tests.txt`. No paid fallback or new model was enabled.

The final UI smoke check passed nine checks, including the new Needs input state, verified result and outcome evidence, connected-page preview, guide text, browser restrictions and the updated main instance. No JavaScript or HTTP errors occurred. Report: `.runtime/review-fixes/final-ui.json`. Eleven targeted regressions were rerun after the last source adjustment and passed. The isolated live experiment included seven passing UI checks before its first quota failure; that partial run is not presented as a fully passing end-to-end script.

Visual inspection also caught static external SVG references disappearing after repeated view changes in Chrome. The approved Nucleo sprite now loads once as local document symbols; the icon set itself is unchanged. The final smoke checks were repeated and the connected-browser screenshot was visually inspected. The isolated test browser/server were then stopped; the updated main instance remains on port 8767.

## Live runs, including failures

All data below are synthetic and were executed on an isolated instance at port 8784. Its registry is separate from the main application. Local artifacts are in `.runtime/review-fixes/`; the directory remains ignored by Git.

- `7440f58566fb46479ae87d99eb1d3829`: CSV processing, completed, five calls.
- `a89078e10bdc453ba9a1800f76c7149d`: ordinary same-chat continuation, correct reversed names, five calls.
- `ed30aa18f75147aebee407daba2f3c55`: missing prior result in a new chat, requests input, zero calls.
- `c422f94fdd9541ecbcbfc159d458d6d4`: browser attempt stopped on Gemini quota after six calls. No paid fallback. Partial form input was not claimed as completion.
- `48b63189601345b68a352c047ab278ab`: browser attempt stopped on invalid model JSON after two calls. A later change permits one format retry per run, within the existing budget; quota and transport errors do not trigger it.
- `8ea0fa1528ca476f8482f90af969c7df`: new browser plan, three passing tests, two correctly registered participants, six calls.
- `a828020afade44a9a1435c97a307b60e`: actual registration succeeded, but the new completion guard incorrectly rejected the generic `call` path because its action counter was not incremented. Fixed and covered for both `call` and `browser_plan`; the failed run and observed page were preserved.
- `809c41e9c1ad4f899429daf17fce068b`: fresh reuse after the fix, two registrations fully verified, three calls, no installation.
- `b28f871b63c54d03a16a23911d8e1a81`: another clean session, two further registrations fully verified with existing records preserved, three calls, no installation.

## Practical limits

- All HTTP redirects are blocked, including same-origin redirects. Redirect-dependent login flows are unsupported. This is deliberately narrower than a general-purpose browser. [Playwright documents redirect suppression for `route.fetch`](https://playwright.dev/docs/api/class-route#route-fetch).
- Strong automatic outcome verification currently covers additions in the local practice registration app. Goal extraction still uses a model; names/emails must appear in the supplied source. This does not prove the user's entire intent can always be interpreted correctly.
- Browser-plan tests validate the declared plan contract, not every possible external application. The local simulator permits setter reordering; it is not a universal equivalence proof for eventful web forms.
- API quotas, malformed output and unsuccessful tests can still stop a run. Passing these scenarios does not establish a general success rate or benchmark improvement.
- The required agent-created discovery/management tool and a different task combining multiple prior skills still lack a complete demonstrated Frankenstein run. Reusing one skill does not satisfy that requirement.
- Model/provider selection, paid billing integration, native desktop control and external-account testing are outside this repair pass.
