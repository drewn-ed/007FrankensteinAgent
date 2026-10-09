# Using Wisp

This guide describes the current local application. All example attendees are synthetic. For a complete clean installation, exact model settings and a no-account demo, start with the [jury quickstart](jury-quickstart.md). The [README](../README.md#run-locally) contains the shorter setup reference.

## Before the first task

Start Docker and the Wisp server, open [localhost:8767](http://127.0.0.1:8767), and check **Personal workspace → Settings → Runtime & limits**. For the default strict $0 policy, configure an allowlisted Gemini model and confirm that its project has billing disabled. ChatGPT plan inference is blocked in strict mode. The optional `SPEND_POLICY=existing_plan` requires a deliberate local configuration change and has no local USD guarantee; connecting an account alone does not activate a model.

For the full event example, use `MAX_MODEL_CALLS=20` and `MAX_RUN_SECONDS=600` in `.env`, then restart the server before the run. Only one task executes at a time. **Stop task** prevents further steps after the current operation; it does not undo changes already made.

## Find your way around

| Area | Use it for |
| --- | --- |
| New chat | A fresh conversation; create it inside the same project to retain access to that project's skills |
| Projects | Related chats and persistent instructions; project skills are scoped, with shared skills also available |
| Computer | Connect a website or a supported native macOS application |
| Library → Actions | Run a learned compute skill with editable inputs and a preview, without asking the model |
| Blackout (header) | Pause AI tasks while keeping saved local actions available |
| Library → Skills | Inspect a generated skill's interface, permissions, code, test results and versions; improve or deactivate it |
| Library → Saved workflows | Reuse a completed task's instructions with fresh inputs, or schedule its original inputs |
| Library → Schedules | Run once or repeat while the local server is running |
| Overview | Review task outcomes, use of earlier skills and model consumption |
| Search | Find chats, skills and workflows by title; this UI search is team-written |
| Quick guide | In-app instructions for the common flows |

## Work with files

Attach files with the **+** beside the message. Ask for an outcome and specify the rules that matter. For example:

> Clean the attached registration CSV. Trim whitespace, lowercase email addresses, remove incomplete rows and keep the first valid registration for each email. Return the cleaned data and explain what changed.

The limit is 10 MB per file and 20 MB per task. UTF-8 text up to 120 KB per attachment can be included in model context. Larger text and binary files provide metadata for transfer; do not assume the model has read them. Only attached or task-generated file IDs are available to the browser connector. Generated Python cannot read arbitrary host files.

Replies in a chat can use up to six recent turns selected by the server, including their saved inputs and results. Oversized context is marked as omitted. A new chat has no prior conversation: attach any source file or baseline report needed for that task.

## Event walkthrough

Fieldwork is a local event operations application served through the connector at `https://event.workspace.demo`. This address is a local fixture handled by Wisp, not a public hosted demo. It includes a roster, workshop board, room changes, allocation preview and report export.

### 1. Clean the roster and allocate seats

Open **Computer → Web browser → Open event operations**. Wisp connects a separate Chrome session, creates or reuses the **Event operations** project, and opens a chat with a task and registration CSV. If Fieldwork is already connected, use **Computer → Start a task** to prepare it. Confirm **Use browser** is enabled, then send the prepared task.

The task asks to normalize the roster, keep the first valid registration per email, assign attendees in roster order to an available preferred workshop, apply the checked plan and export a report. It does not name a tool to create. The source is also available as [october-registrations.csv](../examples/october-registrations.csv).

The recorded result was **24 attendees, 24 assigned, 0 waiting** from 28 source rows. The agent created separate normalization and allocation skills. A new run may choose different names or fail; inspect its actual outcome.

Before claiming fresh generation, inspect **Library → Skills** and the task's starting registry. The showcase button does not clear an existing registry. Already learned skills may be reused.

### 2. Handle a room closure

Keep the connected Fieldwork session open. Choose **Computer → Prepare room change**. This opens a new chat in the same project and attaches the revised roster. Send the prepared task.

It asks to close Hall A, move Agents lab to the 8-seat Studio D, preserve unaffected assignments, account for the new attendee and export the updated report. The recorded result was **25 attendees, 22 assigned, 3 waiting**. This task created a replanning skill, so it is not the demonstration of reuse without new creation.

Download the actual operations report from your successful run. The [revised CSV](../examples/event-revised-registrations.csv) is supplied for manual reproduction.

### 3. Combine earlier skills in a fresh chat

Create **New chat inside Event operations**, keeping the same browser connection. Attach [event-late-registrations.csv](../examples/event-late-registrations.csv) and the **operations report you downloaded in step 2**. Enable **Use browser**. Send:

> One more late registration arrived. Clean and import the attached CSV, then update the seating plan. Use the attached operations report as the baseline: preserve every existing seat in the unaffected workshops, respect the current room capacities, and place new or waiting participants only into remaining preferred seats, otherwise retain them on the waiting list. Apply the full checked allocation and export the new operations report.

The recorded result was **26 attendees, 22 assigned, 4 waiting**. The agent combined the earlier normalization and replanning capabilities. The conversation was empty, no skill was installed and the registry hash stayed unchanged. This establishes fresh-conversation reuse; it is not evidence of a full process restart between these three browser runs.

Check your own steps and evidence: did it use earlier IDs/versions, avoid installations, preserve unaffected seats and export the actual result? A new installation means that run does not establish creation-free reuse, even if its final allocation is correct.

## PATCH: run a learned action

A tested, active **compute skill** automatically becomes an action in **Library → Actions**. This panel and its forms are application infrastructure; the skill's source and original task remain inspectable. Browser plans and discovery tools do not become standalone local actions.

1. Open **Library → Actions** and select an action. Check its project, version and test count.
2. Review the inputs. Wisp prefills the last successful input for that version, or a saved test example when there is no previous run. These are examples to review, not fresh data from your application.
3. Edit the generated fields or choose **Import inputs**. JSON supplies the complete input object. CSV import fills the action's single declared CSV text field and retains the other values; actions without that interface require JSON. Inputs are limited to 120 KB.
4. Choose **Preview result**. The recorded code runs in the existing Docker sandbox, with compute permission only, no network and an eight-second timeout. Invalid or unsupported fields are rejected rather than silently ignored.
5. Review the output, choose **Download result**, or open **View run & evidence**. The result includes the skill version, model-call count and execution duration. Schema validation and saved tests do not prove every business rule for a new input.

If a skill was deactivated or its active version changed since you opened the form, reopen the action. PATCH does not silently substitute a different version. Unsupported requirements need an improved skill and tests, which requires AI again.

### Apply a preview to Fieldwork

Only the included Fieldwork showcase has this direct handoff. Connect it in **Computer** first. A compatible allocation action offers **Use current Fieldwork data** to load its roster, rooms and workshops; supported replanners can also receive the current assignments and waitlist. Otherwise supply the action's declared inputs yourself.

After previewing, **Apply to Fieldwork** checks that the source data still matches, validates the allocation, applies it through the fixed browser connector and checks the resulting application state. A room or roster change requires a fresh preview. This explicit handoff adds no browser permission to generated Python and uses no model call.

If a skill returns richer allocation records, the fixed adapter applies only the participant/workshop IDs and waitlist IDs that Fieldwork accepts. The evidence records this conversion; explanatory fields stay in the original downloadable preview.

A compatible normalization result containing matching `cleaned_csv` and `participants` offers **Replace Fieldwork roster**. This replaces the roster and **clears previous seat assignments and the waitlist**; review the result before choosing it. Generate an allocation preview afterward to assign seats again.

The Fieldwork CSV format supports optional `group_id`. Its independent allocation check rejects splitting a group between workshops or between seats and the waitlist. This check does **not** upgrade an older skill: the chosen normalization and allocation interfaces must explicitly support group data and the required policy. Group-aware skill generation is separate from the fixed application's checker.

An apply attempt that cannot verify its result is marked for review. Inspect Fieldwork before continuing; the app does not promise rollback or blindly retry the same preview. Other websites and native applications do not have this direct PATCH adapter. For those, download the output or use a normal connected-agent task with AI enabled.

## BLACKOUT: keep working with AI paused

When the current task has finished, click **Blackout** in the header, or **Pause AI** in **Library → Actions**. The server saves this state across restarts and rejects new AI tasks, corrections and scheduled AI dispatches. The pause cannot be changed during an active task.

Open a saved action, change its input and choose **Preview result**. It executes the saved tested code directly, without consulting the selected model or requiring working provider quota. A successful result shows **0 AI calls** and **Completed while Blackout was on**. Supported Fieldwork apply buttons still work because that explicit connector operation does not use a model.

Click **Blackout on** in the header, or **Resume AI** in Actions, to allow model tasks again. If a scheduled dispatch was rejected during Blackout, check **Library → Schedules** and resume that paused schedule deliberately.

Blackout switches off Wisp's AI execution path; it does not disable your computer's internet connection. Local computations need the running server, Docker and the already-downloaded sandbox image. Connected external applications may still need internet. Creating new skills, repairing them or interpreting a new natural-language problem requires AI. Zero model calls describes this execution only and excludes earlier learning, testing and local compute costs.

### Recorded group-booking example

The [PATCH/BLACKOUT evidence](patch-blackout-evidence-2026-10-09/) records two genuinely agent-created skills: CSV normalization and allocation that keeps group bookings together. The successful learning run used 9 model calls and passed 3 normalization tests plus 4 allocation tests. A preceding provider-stream failure is retained.

The learning input had 17 CSV rows, 16 unique attendees and workshop-room capacities of 5, 4 and 4; its result was 10 seats and 6 people waiting. The later Blackout check reused both skills with zero model calls and an unchanged registry. It explicitly imported the roster and applied an independently checked allocation in Fieldwork. Fieldwork's available workshop rooms had capacities of 10, 8 and 6, so that separate application check seated all 16. These different outputs reflect different inputs, not an improvement in allocation quality.

A separate fresh-conversation task closed Hall A and added a late pair. It combined both existing skills in 3 model calls, with no installation and an unchanged registry: **18 attendees, 8 seated, 10 waiting**. This demonstrates AI-planned reuse in a new conversation; it is distinct from direct Blackout execution.

### Try the recorded actions without model credentials

After completing the Python, uv and Docker setup in the README, run:

```sh
uv run python scripts/replay_blackout.py --serve
```

Open [localhost:8789](http://127.0.0.1:8789). This uses a separate `.runtime/blackout-replay` store, reruns the 7 saved tests in Docker, and recreates the two recorded skills with explicit evidence-replay provenance. It runs their recorded inputs without model inference and reproduces **16 attendees, 10 seated, 6 waiting**. Inspect **Library → Actions** and try changed inputs within their interfaces. Omit `--serve` if you only want the verification report.

The replay does not generate new skills and should not be presented as doing so. It needs the already-downloaded Docker image, but no model account, key or inference request. This replay does not itself prove generated discovery. The separate [final evidence](frankenstein-final-evidence-2026-10-09/) records an agent-created catalog and fresh-process reuse.

## Inspect or attempt the full creation/discovery flow

The [final evidence bundle](frankenstein-final-evidence-2026-10-09/) contains a 17-call ChatGPT learning run and a separate three-call Gemini Free reuse process. The latter uses the learned catalog, cleaner and allocator under strict $0 admission, with no new installation. The first learning process predates the monetary gate. Its allocator tests all used empty rosters; inspect that coverage limitation before trusting other inputs.

To attempt fresh creation with your own confirmed Gemini Free project, use separate invocations:

```sh
uv run python scripts/verify_frankenstein.py --phase first
uv run python scripts/verify_frankenstein.py --phase second
```

This harness is team-written verification infrastructure, not an agent-created tool. The first phase requires an empty registry, and the second requires the generated task and discovery capabilities. Each attempt retains a unique evidence file, including failures, in `.runtime/frankenstein-verification`; use `--data-dir` for another workspace. A fresh full learning attempt can fail: the published successful chain used ChatGPT for learning and Gemini for strict reuse, rather than demonstrating both fresh phases with Gemini.

## Financial policy

**Settings → Runtime & limits** shows the policy and per-run USD cap. The shipped `SPEND_POLICY=strict`, `MAX_RUN_USD=0` configuration admits operator-confirmed Gemini Free requests and blocks unknown-price routes before inference. Keep billing disabled in Google AI Studio; Wisp cannot verify billing state or enforce a provider-side free-only flag. Calls and elapsed time have separate limits.

**Usage & cost** shows a task’s financial admission, reservations and blocked requests separately from estimated usage. Earlier tasks may have no admission record. Explicit `existing_plan` mode uses provider-managed ChatGPT allowances and credits; it does not supply a local dollar guarantee and is not the strict-budget demonstration path. There is no automatic paid fallback.

## Inspect and improve a result

Expand the steps in a chat, then choose **View evidence** or **More options → Execution details**. **View result** opens the JSON result and any downloadable artifacts. **More options → Usage & cost** shows per-call usage, including failed attempts when the provider reports it.

Open **Library → Skills**, select a skill and choose **Improve**. Describe a specific wrong behavior and the expected result. The optional **Test case** control accepts an explicit input/expected-output example. The new regression case must expose a failure in the old version. The engine checks two candidate repairs against the accumulated tests and activates the first successful candidate. Failure leaves the old active version in place. You can deactivate a skill or reactivate a previously tested version in its detail view.

Passing tests show agreement with those test cases, not universal correctness. A correction changes executable behavior, not model weights.

## Connect a real application

In **Computer**, enter a website URL and choose **Connect browser**. Work happens in a separate Chrome session. It does not inherit your everyday browser login. Only the connected origin is permitted. Redirects, WebSockets and new tabs are unsupported; redirect-based authentication may fail.

External changes wait for **Allow this step** or **Decline**. A task without an independent outcome adapter ends as **Needs review**. Check the target application before choosing **I checked the result**. That records human confirmation, not an automated check. The local showcase permits its synthetic browser mutations without the external-site approval gate.

**Desktop application** is experimental and macOS-only. It requires Apple Command Line Tools to build the bridge and explicit Accessibility permission for Workspace Desktop Bridge. Use **Show connector in Finder** and grant permission in macOS yourself if you choose to use it. The connector supports mapped controls, click and text entry in one selected app, with approval of each mutation. Actual native interaction has not yet been validated on the development machine. Secure fields, system permission apps, screenshots and canvas-based controls are outside its scope.

The bridge source comes with the repository; there is no separate installer to download. Follow the [complete macOS setup and troubleshooting steps](../README.md#optional-native-macos-control). Browser-only tasks do not need this permission.

## Save and schedule work

After a completed task, use **More options → Save as workflow**. **Use workflow** prepares its instructions for new inputs. Attach the new files yourself; opening a workflow does not imply that yesterday's files are today's inputs.

Use **Schedule** from a saved workflow to retain its original inputs, or **Library → Schedules → Schedule a task** for a task without attachments. Choose one-time, every 15 minutes, hourly, daily or weekly. The time input uses the computer's local timezone.

Schedules persist across server restarts. They require the local server to run and the machine to stay awake; there is no wake service or daemon. A missed interval produces one occurrence, not a backlog burst. Busy tasks defer dispatch. Dispatch failures pause a schedule. Application tasks need the same target still connected, and normal approval requirements still apply. Use **Pause** to stop future dispatches.

## Troubleshooting

| Symptom | What to check |
| --- | --- |
| Setup needed | Open Settings; for strict mode configure the Gemini key and confirm billing remains disabled |
| Financial limit blocked | The provider has no verified USD upper bound. Use confirmed Gemini Free; ChatGPT plan inference is unavailable under the strict cap |
| Docker unavailable or missing image | Start Docker; run `docker pull python:3.12-slim`. There is no host-execution fallback |
| Blackout is on | Run an existing action, or resume AI before sending a chat task, correction or scheduled task |
| Action changed or inactive | Reopen the action to review its current tested version; reactivate a version through Skills only if appropriate |
| Preview no longer matches Fieldwork | Load current Fieldwork data and preview again before applying |
| Quota / provider failure | Read the failed task; retry deliberately when service is available. The app does not silently switch providers |
| Run reached its limit | Inspect the steps; simplify the task or use the documented 20-call / 600-second ceiling for the event walkthrough |
| Needs input | Attach the actual source or baseline; a new chat intentionally lacks previous conversation |
| Needs review | Inspect the connected app and confirm only the observed result |
| Redirect or connection blocked | The fixed browser boundary rejected it; use a supported single-origin workflow |
| Schedule did not run | Check server uptime, sleep, paused status, current task and application connection |
| Conflicting workspace edits | Export unsaved edits from the offered UI, then load the latest copy |
| Changes disappeared after reconnecting Fieldwork | A new browser connection has fresh fixture state; retain reports before disconnecting |

Local task state and files live under `.runtime/`; provider credentials are stored separately as described in [architecture](architecture.md#data-and-credentials). Keep runtime data out of public commits.
