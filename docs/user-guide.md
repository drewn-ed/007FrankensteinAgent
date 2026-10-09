# Using Wisp

This guide describes the current local application. All example attendees are synthetic. For installation and provider setup, start with the [README](../README.md#run-locally).

## Before the first task

Start Docker and the Wisp server, open [localhost:8767](http://127.0.0.1:8767), and check **Personal workspace → Settings → Runtime & limits**. Configure and activate a model. A connected ChatGPT account alone does not select the active model.

For the full event example, use `MAX_MODEL_CALLS=20` and `MAX_RUN_SECONDS=600` in `.env`, then restart the server before the run. Only one task executes at a time. **Stop task** prevents further steps after the current operation; it does not undo changes already made.

## Find your way around

| Area | Use it for |
| --- | --- |
| New chat | A fresh conversation; create it inside the same project to retain access to that project's skills |
| Projects | Related chats and persistent instructions; project skills are scoped, with shared skills also available |
| Computer | Connect a website or a supported native macOS application |
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
| Setup needed | Open Settings; select and activate a ChatGPT model, or configure the Gemini key and Free-tier confirmation |
| Docker unavailable or missing image | Start Docker; run `docker pull python:3.12-slim`. There is no host-execution fallback |
| Quota / provider failure | Read the failed task; retry deliberately when service is available. The app does not silently switch providers |
| Run reached its limit | Inspect the steps; simplify the task or use the documented 20-call / 600-second ceiling for the event walkthrough |
| Needs input | Attach the actual source or baseline; a new chat intentionally lacks previous conversation |
| Needs review | Inspect the connected app and confirm only the observed result |
| Redirect or connection blocked | The fixed browser boundary rejected it; use a supported single-origin workflow |
| Schedule did not run | Check server uptime, sleep, paused status, current task and application connection |
| Conflicting workspace edits | Export unsaved edits from the offered UI, then load the latest copy |
| Changes disappeared after reconnecting Fieldwork | A new browser connection has fresh fixture state; retain reports before disconnecting |

Local task state and files live under `.runtime/`; provider credentials are stored separately as described in [architecture](architecture.md#data-and-credentials). Keep runtime data out of public commits.
