# Jury quickstart: install, run and try Wisp

Wisp runs on **your own computer**. The landing page is not a hosted agent. You do not need the developer's account, keys, computer, a browser extension or a separate bridge download.

Choose a path:

| What you want to verify | Model access needed? | Start here |
| --- | --- | --- |
| Open the UI and execute recorded PATCH/BLACKOUT actions | **None** | Sections 1–2 |
| Check recorded catalog management and both task results in Docker | **None** | Section 5 |
| Generate new capabilities from your own prompt | Your own confirmed Gemini Free key **or** eligible ChatGPT plan-usage connection | Sections 3–4 |
| Control a native macOS app | Model connection plus locally granted Accessibility permission | Optional section 6; experimental |

## 1. Install from the public repository

The checked setup is **macOS**, with Git, Python 3.11+, uv, Docker running, Node.js **20+**, npm and Google Chrome installed. Node and Chrome are required for browser control and the complete test suite, but not for the data-only replay. There is no frontend build command: Python serves the checked-in HTML, CSS and JavaScript.

Install missing prerequisites using their official installers: [Python](https://www.python.org/downloads/), [uv](https://docs.astral.sh/uv/getting-started/installation/), [Docker Desktop](https://www.docker.com/products/docker-desktop/), [Node.js](https://nodejs.org/en/download), and [Chrome](https://www.google.com/chrome/). Complete Docker's first-run setup and leave its engine running. These tools and the initial image download require internet access and free disk space.

In Terminal:

```sh
git clone --branch main https://github.com/drewn-ed/Wisp.git Wisp
cd Wisp
uv sync --frozen
npm ci --ignore-scripts
docker pull python:3.12-slim
docker info
```

`uv sync --frozen` creates the local `.venv` using the committed lockfile. `docker info` must show a running server, not a connection error. `node --version` must report 20 or later. Wisp launches installed Google Chrome through Playwright; a separate Playwright browser download is not needed.

Native Windows Python is unsupported (`fcntl` is Unix-only). Linux/WSL have not been validated; do not treat them as a tested installation path. Native control is macOS-only.

**Clean-checkout verification, 9 October 2026:** a fresh clone of committed implementation `8b22251` on the development Mac completed `uv sync --frozen`, `npm ci --ignore-scripts` and the credential-free replay below. No `.env` was present; all 7 replay tests passed, with 16 participants, 10 assigned, 6 waiting and 0 model calls. A fresh normal server returned HTTP 200 for its UI, Docker ready and model not configured. This reused the Mac's installed prerequisites and Docker image; it was not a fresh operating-system installation or a new third-party ChatGPT account test.

## 2. Try PATCH and BLACKOUT without an API key

From the repository directory, with Docker running:

```sh
uv run python scripts/replay_blackout.py --serve
```

Wait for the verification report and `Recorded replay workspace` URL, then open **http://127.0.0.1:8789**. Keep the terminal open.

Expected terminal result: **7 sandbox tests passed, 16 participants, 10 assigned, 6 waiting, 0 model calls**. The script checks the original generated-code hashes, retests the saved code and uses a separate `.runtime/blackout-replay` registry with explicit replay provenance. It starts with BLACKOUT enabled and no configured model.

1. Open **Library → Actions**. Two recorded actions are loaded: registration cleaning and group-preserving allocation.
2. Open an action. Review the input fields; the replay's prior executions supply example input. Keep it unchanged for the first trial or use **Import inputs** for your own compatible JSON/CSV.
3. Choose **Preview result**, inspect the output and **View run & evidence**. It should show zero model calls and completion while Blackout was on.
4. Choose **Download result** to save the computation output. Inspect **Library → Skills** for code, interface, tests and version.
5. A new free-text AI task is intentionally blocked in this replay. To test fresh learning, continue with section 3 in the normal workspace.

This is **execution of previously agent-created code**, not fresh generation or autonomous composition. No ChatGPT subscription, Gemini key or reverse proxy is needed. After setup, these local computations need the server, Docker and the downloaded image, but no model connection.

Stop with **Ctrl+C** in the terminal. The replay refuses to overwrite an existing registry on a subsequent launch. Preserve the previous run and use a new folder:

```sh
uv run python scripts/replay_blackout.py --serve --data-dir .runtime/jury-replay-2
```

If 8789 is occupied, add `--port 8790` and open the printed URL instead. The replay workspace and the normal workspace on 8767 have separate data stores.

## 3. Optional: connect a model for fresh learning

Create local settings without overwriting an existing configuration:

```sh
test -f .env || cp .env.example .env
chmod 600 .env
```

Edit `.env` in your text editor. Replace existing values rather than adding duplicate lines. Restart the server after editing. Never commit your key or put it into chat, screenshots or the submission form.

### Option A: Gemini API key, strict zero-dollar mode

Create your own key in [Google AI Studio](https://aistudio.google.com/apikey). Verify that its associated project is on the **Free tier with billing disabled**. Only then set:

```dotenv
MODEL_PROVIDER=gemini
GEMINI_API_KEY=replace_with_your_own_key
GEMINI_MODEL=gemini-3.5-flash-lite
GEMINI_FREE_TIER_CONFIRMED=true
SPEND_POLICY=strict
MAX_RUN_USD=0
MAX_MODEL_CALLS=20
MAX_RUN_SECONDS=600
```

Do not keep the placeholder as a real key. The current code allowlists `gemini-3.5-flash-lite` and `gemini-3.1-flash-lite`; another model is rejected. Availability and quota belong to your Google project. Wisp cannot independently verify billing status or force a provider-side free-only request. No paid fallback exists. If the key/project cannot use this route, use the credential-free replay rather than enabling billing to get past an error.

Start the normal app:

```sh
uv run python -m workbench.server
```

Open **http://127.0.0.1:8767** → **Personal workspace → Settings → Runtime & limits**. Confirm model readiness, Docker readiness and the strict $0 policy. A missing/invalid key or exhausted quota prevents new AI work; saved local actions still work.

### Option B: Continue with ChatGPT, provider-managed plan usage

You need your **own ChatGPT account eligible for plan usage**, permission to use its allowance and an available model. Do not assume every subscription or managed workspace is eligible. The authorization flow confirms access. This follows OpenAI's [official sign-in flow](https://developers.openai.com/siwc/token-sharing-open-source/sign-in); account/workspace restrictions can cause [eligibility errors](https://developers.openai.com/siwc/token-sharing-open-source/errors-and-recovery).

1. Set `SPEND_POLICY=existing_plan` in `.env`. This is a deliberate alternative to strict mode: **there is no local USD spending guarantee**. Plan limits and credits are managed by OpenAI. You can leave `MODEL_PROVIDER=gemini` temporarily and leave the Gemini key blank; the UI still opens for sign-in.
2. Start or restart `uv run python -m workbench.server`, and open **http://127.0.0.1:8767** on the same computer.
3. Open **Personal workspace → Settings → Continue with ChatGPT**. Complete the OpenAI login and plan-usage consent. Keep Wisp running for the local callback.
4. Return to Settings, select one of the models returned for your account, and click **Activate model**. Login alone does not activate inference.
5. Confirm the active provider/model and readiness. Activation saves `MODEL_PROVIDER=chatgpt` and the selected `CHATGPT_MODEL` in your local `.env`; it does not publish credentials. Review provider allowance in ChatGPT Settings → Usage.

**Do not supply an `OPENAI_API_KEY`, copy Codex tokens, install a reverse API proxy or configure a custom base URL.** None of those is supported by this checkout. The implemented ChatGPT connection uses OAuth directly; it needs neither a paid OpenAI API key nor a proxy. A ChatGPT subscription and paid API billing are different access mechanisms. The app also has no Anthropic adapter.

OAuth credentials are stored in `~/.config/007-frankenstein/accounts.json`, separately from the project and sandbox. Application data lives under `.runtime/`. To switch back to Gemini, set `MODEL_PROVIDER=gemini`, `SPEND_POLICY=strict` and the confirmed Free settings, then restart. Provider switching is not automatic.

## 4. Run a new task and see what happened

Use the normal app on **8767**, with a ready model and Docker. Turn BLACKOUT off before asking for new AI work.

For a small first trial, choose **Try an example**, review its synthetic data and send it. For the browser walkthrough:

1. Open **Computer → Web browser → Open event operations**. Wisp launches an isolated Chrome session, opens the local Fieldwork fixture and prepares a task with its CSV. No personal website login is required.
2. Review the prepared prompt, confirm **Use browser** is on and send. Watch the steps for missing-capability detection, test creation, sandbox tests, installation and execution. The full flow may take several minutes or fail; it is live inference.
3. Open **View evidence** and **View result**, then download the actual report. Inspect the new capabilities under **Library → Skills** and their direct forms under **Library → Actions**.
4. Keep Fieldwork connected and choose **Prepare room change**. For fresh-chat composition, use the [exact follow-up walkthrough](user-guide.md#3-combine-earlier-skills-in-a-fresh-chat), attaching the report from your own previous run and the supplied later roster.

The browser scenario and the group-booking replay use different fixtures/capacities, so their totals differ. A first installation has an empty Library; replay deliberately loads recorded artifacts. Do not describe replayed artifacts as generated during your new run.

Readable task inputs and relevant application observations are sent to the selected model provider. Generated Python runs in a restricted Docker container, without model credentials or network access. External application mutations may wait for **Allow this step**; check the proposed action and actual result.

## 5. Verify the final track evidence without model credentials

```sh
uv run python scripts/check_frankenstein_evidence.py
```

This replays the actual published catalog and allocation code in Docker. It checks version changes, deactivation, rollback, unchanged permissions and the two nonempty results: **16 → 10 seated / 6 waiting**, then **18 → 8 seated / 10 waiting**. It makes no model calls and refreshes two derived report files. See the [evidence README](frankenstein-final-evidence-2026-10-09/README.md) for exact provenance and retained failures.

With a confirmed Gemini Free key, these two separate commands instead attempt **fresh creation and fresh-process composition**:

```sh
uv run python scripts/verify_frankenstein.py --phase first
uv run python scripts/verify_frankenstein.py --phase second
```

The second requires the first to succeed with two task skills and a discovery skill. Each attempt retains evidence in `.runtime/frankenstein-verification`. Fresh generation is nondeterministic; failures are possible and are not replaced with prerecorded success. To start another independent attempt, pass the same new `--data-dir .runtime/jury-live-2` to both phases.

## 6. Optional native bridge and troubleshooting

Native macOS control is experimental and not required for the proven browser/data paths. Follow the [README Accessibility instructions](../README.md#optional-native-macos-control) only if you want to test it. There is no additional bridge download; Swift source is included and builds locally with Apple Command Line Tools. Actual permission-enabled native interactions have not been validated.

For port conflicts, Docker, model quota, financial-policy blocks, replay directories or denied Accessibility permission, use the [troubleshooting table](../README.md#setup-and-runtime-troubleshooting). Keep the server terminal open. Closing the browser does not stop Wisp. **Ctrl+C** stops the local server; persisted data remains. Scheduling requires the computer awake and the server running. Browser reconnection creates a fresh isolated browser session, so save reports before disconnecting.
