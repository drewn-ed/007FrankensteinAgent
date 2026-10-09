# Workspace · 007 Frankenstein

**An agent workspace that turns missing steps into tested skills it can use again.**

Workspace helps people who repeatedly prepare files and operate business applications. Give it a task and the relevant inputs. When a reusable operation is missing, the agent writes Python, tests it in Docker, and registers it only after the tests pass. Later tasks can combine those saved skills. Corrections can become regression tests for a new version.

Built solo by David for **Agents 0.0.7 — From Dusk Till Dawn #01**, track **Frankenstein**. `007FrankensteinAgent` is the repository name; **Workspace** is the current application label. **Fieldwork** is the fictional event application used to demonstrate it.

[Use the application](docs/user-guide.md) · [Review the evidence](docs/jury-guide.md) · [Architecture and boundaries](docs/architecture.md) · [Submission text](docs/submission-draft.md)

## See what it does

An event organizer has a messy registration file, workshop preferences and limited room capacity. Then a room becomes unavailable. Workspace cleans the roster, creates allocation logic, applies the result in the connected application and downloads an operations report.

The recorded demonstration uses **synthetic attendees in a local application, with real model calls, Docker tests and browser actions**:

| Task | Observed result | What the agent learned or reused |
| --- | --- | --- |
| Open the event | 28 source rows → 24 valid attendees, all 24 seated | Created and tested CSV normalization and preference-based allocation |
| Handle a room closure and a revised roster | 25 attendees → 22 seated, 3 waiting; unaffected seats preserved | Reused normalization; created and tested replanning |
| Process another late registration in a new chat | 26 attendees → 22 seated, 4 waiting; report exported | Combined earlier normalization and replanning; no new installation, unchanged registry hash |

The three successful runs used `gpt-6.1-sol` through an explicitly selected ChatGPT connection. [Logs, generated code and tests](docs/jury-guide.md#recorded-demonstration) include earlier unsuccessful Gemini attempts. The timings are not a controlled speed or cost comparison.

**Track status:** creation, test-gated installation and composition in a fresh conversation have evidence. **Agent-created discovery/management is not yet demonstrated.** The runtime bounds calls and time, but does not enforce an independent dollar budget. The complete Frankenstein checklist is therefore **not claimed as satisfied**. [Requirement-by-requirement status](docs/jury-guide.md#frankenstein-requirements).

## How the jury can try it

**This is currently a local, source-distributed prototype, not a downloadable desktop installer or a hosted agent service.** The interface opens in a browser, but the Python runtime, Docker sandbox and application connectors run on the reviewer's own computer. Opening our localhost URL on another computer does not connect to the demonstration machine.

| Review path | What the reviewer needs | Accessibility permission? |
| --- | --- | --- |
| Inspect recorded evidence | A browser for the repository, logs and generated-code bundle in the [jury guide](docs/jury-guide.md) | No |
| Run the file/browser showcase | Clone this implementation; install the prerequisites below; start the local server; connect a model using the reviewer's own account or key | No |
| Try native macOS control | The same local setup, plus Apple Command Line Tools and a running macOS application to test | Yes, explicitly granted on that Mac |

**Recommended first trial:** run the Fieldwork browser showcase. It exercises real skill generation, sandbox tests, browser uploads/actions/downloads and reuse without access to the reviewer's native applications or personal website accounts. The scenario and its data are synthetic. Model inference still requires internet access and available provider allowance; evidence inspection does not.

There is **no separate bridge download or browser extension** for this checkout. The browser connector is included in the repository. The native bridge source is included too and is compiled locally when the reviewer opens the desktop connection tab. There is no signed/notarized release installer, one-click `.dmg`, remote-control relay or cloud-hosted demo in this version. Development checks were performed on macOS; a fresh Windows/Linux installation is not validated, and native control is macOS-only.

## Run locally

Prerequisites: **Python 3.11+**, [uv](https://docs.astral.sh/uv/), a running Docker engine, and the `python:3.12-slim` image. Browser control also needs Node.js, npm and installed Google Chrome. Development validation was performed on macOS; native application control is macOS-only.

```sh
git clone --branch codex/learning-agent-mvp https://github.com/drewn-ed/007FrankensteinAgent.git
cd 007FrankensteinAgent
uv sync --frozen
npm ci --ignore-scripts
docker pull python:3.12-slim
# Create local settings only if they do not already exist.
test -f .env || cp .env.example .env
chmod 600 .env
uv run python -m workbench.server
```

Open **[http://127.0.0.1:8767](http://127.0.0.1:8767)**. Use the checkout containing the implementation and this README; local edits do not become available to reviewers until committed and pushed. Check **Settings → Runtime & limits** for readiness.

Choose one model connection:

- **ChatGPT:** open **Personal workspace → Settings → Continue with ChatGPT**, complete account consent, choose an available model and click **Activate model**. Connecting the account and activating a model are separate steps. No Gemini key is needed on this path.
- **Gemini:** put your own `GEMINI_API_KEY` in `.env`. Confirm the associated project is on the Free tier, then set `GEMINI_FREE_TIER_CONFIRMED=true`. Keep `MODEL_PROVIDER=gemini` and restart the server. The checked-in default is `gemini-3.5-flash-lite`; the adapter has an explicit model allowlist.

Tasks, readable attachments and relevant application observations are sent to the selected provider. Credentials stay outside the UI and generated-code sandbox. There is **no automatic provider switch or paid API fallback**. ChatGPT account allowances and credits depend on the user's provider settings; usage reporting is not a billing statement.

For the longer event walkthrough, set `MAX_MODEL_CALLS=20` and `MAX_RUN_SECONDS=600` in `.env` before starting the server. The shipped defaults are 18 calls / 240 seconds; code clamps these to at most 20 / 600. Changing these limits does not change sandbox permissions.

## Try the application

1. For a small data task, choose **Try an example**, review the synthetic input and send it.
2. For the full browser example, choose **Computer → Open event operations**. This opens a separate Chrome session and prepares the first task with its CSV attached. If Fieldwork is already connected, choose **Start a task**. Review and send it.
3. Expand the task steps, inspect **View evidence**, then open **View result** and download the actual report. **Library → Skills** shows the generated contracts, versions and tests.
4. In **Computer**, choose **Prepare room change**. After it completes, follow the [fresh-chat reuse walkthrough](docs/user-guide.md#3-combine-earlier-skills-in-a-fresh-chat) with the late roster and the report from your own run.

The full walkthrough takes several minutes and needs working model quota. It is not an instant prerecorded success path.

## Optional: native macOS control

**Skip this section for the browser showcase.** Accessibility is only required to inspect and operate another native application through macOS. The bridge is trusted application infrastructure; it is not code generated by the model.

1. Complete the local setup above. Install Apple's Command Line Tools if `swiftc --version` is unavailable. Run `xcode-select --install` in Terminal and complete Apple's installer yourself.
2. Start the Workspace server, then open **Computer → Desktop application**. On first use, Workspace compiles the included Swift source and creates `.runtime/Workspace Desktop Bridge.app` inside this checkout. It applies a local ad-hoc signature; this is not a notarized distribution build. Compilation may take a moment.
3. Choose **Show connector in Finder**. In **System Settings → Privacy & Security → Accessibility**, use **+** to add the revealed **Workspace Desktop Bridge** application and enable it. macOS may require the account owner to authenticate. If macOS attributes the request to the launching app, follow its indicated entry, such as Terminal or the development app. Do not grant unrelated applications access.
4. Return to Workspace and choose **Check permission again**. Proceed only when the UI allows **Connect application**. If permission remains denied after enabling the appropriate entry, stop any active task, restart the local server and check again. The app cannot grant this permission itself.
5. Open a disposable test document in a supported application, such as TextEdit. Select that running application in Workspace, choose **Connect application**, then **Start a task here**. Confirm **Use desktop** is enabled and ask it to enter a short test sentence in that document.
6. Review each proposed change and choose **Allow this step** or **Decline**. Check the actual target window before confirming the task's result. **Disconnect** ends the app connection; macOS Accessibility permission remains until the user turns it off in System Settings.

**Current validation limit:** the bridge builds and signs locally, lists applications and correctly reports denied permission. Actual native clicking and typing have **not yet been verified** on the development Mac because Accessibility remains denied. Native control is experimental, not the required reproduction path for the recorded browser demonstration. The supported operations are reading mapped controls, clicking and text entry in one selected app; arbitrary keyboard shortcuts, screenshots, protected fields and canvas-only controls are not supported. Rebuilding or moving the helper may require macOS to review its permission again.

### Setup and runtime troubleshooting

| Symptom | Next step |
| --- | --- |
| The localhost page does not open | Start `uv run python -m workbench.server` on the same computer and keep its terminal open. `127.0.0.1` always refers to that computer |
| Port 8767 is already in use | Start with `uv run python -m workbench.server --port 8768`, then open `http://127.0.0.1:8768` |
| Sandbox is unavailable | Start Docker and pull `python:3.12-slim`; use **Settings → Runtime & limits → Check runtime** |
| Browser connection fails | Install Google Chrome and run `npm ci --ignore-scripts` in the project directory. No browser extension or Accessibility grant is needed for this connector |
| Desktop connector cannot compile | Check that `swiftc --version` works after installing Apple Command Line Tools |
| Desktop connection remains disabled | Follow the Accessibility steps above; `trusted: false` means macOS has not authorized the connector's access |
| Model is unavailable or quota is exhausted | Use the reviewer's own connection in Settings or `.env`; inspect the error. There is no bundled shared API key or automatic paid fallback |
| Scheduled work does not execute | Keep the local server running and the computer awake; connected-app tasks may still wait for operator approval |

To stop Workspace, finish or stop the current task and press **Ctrl+C** in the server terminal. Tasks, files, skills and schedules persist in the local `.runtime/` directory; stopping the server does not remove them. Browser reconnection starts a fresh isolated browser session, so retain exported reports. Closing only the web page does not stop the server or its scheduler.

## What is included

- Projects, persistent chats, scoped skills and saved workflows.
- Skill creation, contract tests, a persistent versioned registry, correction with regression tests, deactivation and reactivation of tested versions.
- A fixed browser connector for one approved origin, file upload/download and operator review for external changes.
- Local one-time and repeating schedules; the server must remain running and the computer awake.
- Task history, execution evidence and provider-reported token usage.
- A native macOS connector whose build and permission-denial path were checked. Actual clicks and text entry remain unverified pending Accessibility permission.

Saved workflows store instructions and input references; they are not themselves newly generated skills. Remembered application maps are observations, not proof of learning. The connector, registry and outcome verifier are team-written infrastructure.

## Verify it

```sh
# Requires Docker, the image, Node dependencies and Chrome.
# Uses synthetic/model fixtures; does not require live model inference.
uv run python -m unittest discover -s tests -v

# Optional live data-only task in a separate registry; consumes model allowance.
uv run python -m workbench.cli \
  'Clean the supplied registrations, remove duplicate email records, and report workshop demand.' \
  --input examples/registrations.json --data-dir .runtime/verification
```

Infrastructure tests cover isolation, failed-test rejection, permission boundaries, budget stops, persistence, corrections, browser constraints, files, schedules and usage. They do not substitute for agent-generated demonstration evidence. See [validation and limitations](docs/jury-guide.md).

## Current limits

This is a local prototype. It has no team sharing, external MCP integration or always-on hosted service. Browser connections allow one origin and block HTTP redirects and WebSockets; many login flows will not work. External sites and native apps require human outcome review. Binary files can be transferred, but their contents are not interpreted by the text model. Generated tests and showcase constraints do not prove general correctness or optimal allocation. User demand, time savings and superiority over other assistants have not been validated.

The Python source is in [`workbench/`](workbench/), UI in [`web/`](web/), fixtures in [`examples/`](examples/) and tests in [`tests/`](tests/). The [documentation index](docs/README.md) separates current guides from historical research. The separate landing page and brand work are not runtime evidence.

No project-wide software license has been selected in this repository; public visibility alone is not an open-source license. Bundled fonts and icons retain their own license/copyright files under [`design/`](design/) and [`web/fonts/`](web/fonts/).
