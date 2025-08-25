# AutoGen-Based Multi-Agent TypeScript Development Engine (Offline-Capable)

**Goal**
Generate a Python package `autogen-ts-engine` that orchestrates an AutoGen multi-agent system to build large TypeScript projects in sprints (plan → code → test → review → commit/PR). It must run fully offline by default (LM Studio as OpenAI-compatible API), manage context with a local vector DB (Chroma), and support inner/outer RL. It should be installable via `pipx` directly from GitHub and configurable via Markdown files.

**Key requirement (example target app):** The engine must be able to create a **TypeScript terminal file manager** (Ranger-like TUI with vi keybindings) as a project scenario, including scaffolding, features, tests, and packaging.

---

## Deliverables (files & structure)

Create a Python package with this structure:

```
autogen-ts-engine/
├─ pyproject.toml                      # PEP 621; console_script entry point
├─ README.md
├─ autogen_ts_engine/
│  ├─ __init__.py
│  ├─ main.py                          # CLI: `autogen-ts-engine run ...`
│  ├─ config_parser.py                 # Markdown -> config model
│  ├─ agent_factory.py                 # Planner/Coder/Tester/Critic/RAG
│  ├─ sprint_runner.py                 # Sprint loop & group chat
│  ├─ rag_store.py                     # ChromaDB wrapper
│  ├─ rl_module.py                     # Inner/outer RL policies & rewards
│  ├─ git_ops.py                       # init/branch/commit/PR helpers
│  ├─ node_ops.py                      # npm/pnpm/yarn, ts-node, jest, esbuild
│  ├─ fs_bootstrap.py                  # Creates default project structure
│  ├─ logging_utils.py
│  └─ schemas.py                       # Pydantic models for configs
```

When the engine initializes a **work\_dir** (default `./ts_project`), create if missing:

```
work_dir/
├─ config/
│  ├─ settings.md
│  └─ agents.md
├─ scrum/
├─ src/
├─ tests/
├─ project_db/                         # Chroma persistence
└─ venv/                               # Optional local venv (see note below)
```

> **pipx vs venv note:** Since pipx already isolates the package, do **not** force a `venv/` in `work_dir` by default. Provide a `--create-venv` flag to create and use `work_dir/venv` if the user wants a project-local environment.

---

## Dependencies

Declare in `pyproject.toml`:

* `pyautogen` (AutoGen)
* `chromadb`
* `sentence-transformers` (embedder; choose a small default like `all-MiniLM-L6-v2`)
* `gymnasium` (for RL interfaces)
* `numpy`, `pydantic`, `markdown-it-py` or `markdown`, `pyyaml`
* (Optional) `rich` for CLI UX

---

## CLI

Expose a console script:

```
autogen-ts-engine run --config-dir <dir> --work-dir <dir> \
  [--create-venv] [--debug] [--max-sprint N] [--max-iters-per-sprint M]
```

Behavior:

1. Parse configs (`config/settings.md`, `config/agents.md`), apply defaults.
2. Initialize LM Studio binding (OpenAI-compatible; default `http://localhost:1234/v1`, model `llama3`).
3. Initialize Chroma at `vector_db_path`.
4. Bootstrap work\_dir (Node project, tsconfig, jest config) if missing.
5. Ensure Git repo; create sprint branch `{git_branch_prefix}{sprint_number}`.
6. Run sprint cycles (group chat with max rounds).
7. Persist results into `scrum/sprint_{N}.md` and index artifacts into Chroma.
8. Run tests, compute RL reward, update policies, and optionally open a PR (if GitHub token present).

---

## LM Studio (offline LLM)

* Default: `llm_api_base = "http://localhost:1234/v1"`, `llm_model_name = "llama3"`, `api_type = "open_ai"`, `api_key = "lmstudio"`.
* Detect if unreachable → print actionable warning: “Start LM Studio, load a model, enable server on port 1234” and exit cleanly.

---

## Configs in Markdown (with fenced YAML blocks)

### `settings.md` (example)

````markdown
# Settings

```yaml
project_name: "ts_project"
project_goal: "Build a TypeScript terminal file manager with a Ranger-like TUI and vi keybindings."
num_sprints: 4
iterations_per_sprint: 8

llm_binding:
  api_base: "http://localhost:1234/v1"
  model_name: "llama3"
  api_type: "open_ai"
  api_key: "lmstudio"
  cache_seed: 42

work_dir: "./ts_project"
vector_db_path: "./project_db"
git_branch_prefix: "sprint-"
human_input_mode: "NEVER"  # ALWAYS | NEVER | AUTO

# RL
rl:
  epsilon: 0.1
  alpha: 0.1
  gamma: 0.9
  state_buckets: 10

# RAG
rag:
  top_k: 5
  max_doc_tokens: 4000

# Node toolchain
node:
  package_manager: "npm"       # npm|pnpm|yarn
  test_command: "npm test"
  build_command: "npm run build"

# Jest/ts-jest defaults are auto-initialized if missing
debug_mode: false
````

````

### `agents.md` (table or YAML)

```markdown
# Agents

| Agent Name | Role  | System Message |
|------------|-------|----------------|
| Planner    | Plan sprint goals and tasks. | "Plan incremental TUI features; ensure testability and vi keybindings coverage; consult RAG for prior art." |
| Coder      | Implement features in TS.    | "Write idiomatic TS, add unit/integration tests, keep functions small; prefer react-blessed or blessed for TUI." |
| Tester     | Author & run tests.          | "Use Jest; add keybinding simulations; verify navigation, preview, file ops." |
| Critic     | Review & suggest fixes.      | "Focus on architecture, UX consistency, error handling, cross-platform fs semantics." |
| RAG        | Retrieval agent.             | "Supply relevant snippets from scrum history and src/ to reduce token usage." |
````

> The parser should accept either tables or fenced YAML blocks; if both exist, YAML wins.

---

## Agent & Tooling Details

* **Agents**: Implement AutoGen `AssistantAgent` instances + a `UserProxyAgent` (respect `human_input_mode`).
* **RAG**: `rag_store.py` chunks `src/`, `tests/`, and `scrum/` MD files; indexes to Chroma with Sentence-Transformers. Provide `retrieve(query, top_k)` and a conversation memory summarizer.
* **RL**:

  * *Inner loop*: bandit/Q-learning to pick next “action” class (e.g., refactor, add tests, improve docs, split module, reduce deps).
  * *Outer loop*: after each sprint, adjust weights based on trend in rewards.
  * *Reward signal (composite)*: test pass rate Δ, coverage Δ, lints, binary size Δ (for CLI), execution time of key flows, “UX probe” scripts for TUI (keybinding success), and optional human feedback file `scrum/feedback.md`.
* **Git ops**: `git init`, branch naming with `{git_branch_prefix}{N}`, conventional commits; if `GH_TOKEN` is set, open PR via `gh` CLI (fallback: local branch only).

---

## Node project bootstrap (for TS + Jest + TUI)

`node_ops.py` must support:

1. Initialize TS project if missing:

   * `package.json` with scripts: `build`, `test`, `start`.
   * `tsconfig.json` (strict mode), `jest.config.ts` (ts-jest), `src/index.ts`, `tests/smoke.test.ts`.
2. TUI dependencies for the Ranger-like app (choose one stack, but make it configurable):

   * Option A: `blessed` (or `neo-blessed`) + TypeScript typings
   * Option B: `react-blessed` + `react` + `@types/react`
3. Cross-platform FS ops: use Node’s `fs/promises`, handle symlinks, permissions, and Windows path quirks.
4. Keybinding layer: vi keys (`h j k l`, `gg`, `G`, `dd`, `yy`, `/` search), configurable in `src/keymap.ts`.
5. Testing helpers to simulate key events in Jest (e.g., mock stdin, send key codes, assert view state).

---

## Sprint workflow (group chat)

For each sprint:

1. **Planner**: synthesizes goals from `project_goal`, current repo status, failing tests, and RAG context.
2. **Coder**: implements tasks (create/modify TS files), updates tests, runs formatter.
3. **Tester**: runs tests, reports coverage and UX probe results.
4. **Critic**: reviews diffs and suggests improvements.
5. **RL update**: compute reward, update policy.
6. **Git commit**: commit with message template; open PR if configured.
7. **Log**: append actionable summary, diffs, test output to `scrum/sprint_{N}.md`; index artifacts into Chroma.

Limit group chat to `iterations_per_sprint`. On tool errors, retry with backoff; always write failures to the sprint MD.

---

## Parsing Markdown configs

* Accept tables **or** fenced YAML blocks (preferred).
* Implement `schemas.py` (Pydantic) for:

  * `Settings`: all fields with defaults you listed (num\_sprints, iterations\_per\_sprint, llm\_binding, paths, RL, RAG, node, etc.).
  * `AgentDefinition`: name, role, system\_message.

Fallback to safe defaults if fields are missing.

---

## Defaults (as you specified, clarified)

* Agents: Planner, Coder, Tester, Critic, RAG (auto-detected from `agents.md`).
* `num_sprints`: 3
* `iterations_per_sprint`: 5
* `llm_binding`: LM Studio @ `http://localhost:1234/v1`, model `llama3`, `api_key: lmstudio`
* `vector_db_path`: `./project_db`
* RL: `epsilon=0.1`, `alpha=0.1`, `gamma=0.9`, `state_buckets=10`
* `git_branch_prefix`: `sprint-`
* `human_input_mode`: `ALWAYS` | `NEVER` | `AUTO` (default `ALWAYS`)
* `cache_seed`: 42
* `debug_mode`: false

---

## Example: Terminal File Manager sprint seeds (optional helper)

To help the Planner start, if `project_goal` matches “terminal file manager”, create a seed backlog in `scrum/sprint_1.md`:

* Pane layout (left tree, right list/preview), directory navigation, status line.
* vi keybindings: `h j k l`, `gg`, `G`, `:q`, `/` search, `yy`/`dd` on files.
* Operations: copy/move/delete/rename, mkdir, view preview for text/images (ASCII placeholder), file info.
* Cross-platform support (Linux/macOS/Windows).
* Tests:

  * Keybinding simulation suite.
  * E2E smoke test: navigate tmp fs, create & delete files, assert state transitions.

---

## Non-goals / constraints

* Do not require cloud services; run offline by default.
* If GitHub auth isn’t configured, create local commits/branches only (no failure).
* Keep RAG index local and incremental; avoid indexing `node_modules`.

---

## What to generate now (Copilot)

1. Full Python package as above, with working CLI and stubs filled.
2. Robust `node_ops.py` that can:

   * Initialize TS project (with `blessed` or `react-blessed`) and Jest.
   * Run build/test commands and parse results for RL reward metrics.
3. Sample `config/settings.md` and `config/agents.md` written at bootstrap if absent.
4. A minimal TUI project skeleton demonstrating vi keybindings and one Jest keybinding test.
5. Documentation in `README.md` explaining LM Studio setup, offline usage, and the sprint loop.

---

### Why these changes help with your Ranger-like TUI goal

* **Explicit Node/TUI toolchain** ensures the Coder/Tester agents have the right scaffolding and can run deterministic tests offline.
* **Keybinding tests** give the RL module concrete, automatable rewards beyond “tests pass”.
* **Fenced YAML in Markdown** makes parsing reliable (tables are messy).
* **pipx + optional venv** avoids env confusion while still allowing a project-local venv when desired.
* **Chroma + summarization** keeps prompts small and repeatable across sprints.

If you want, I can also sketch the initial `package.json`, `tsconfig.json`, `jest.config.ts`, and a tiny `src/index.ts` with vi key handlers that the engine should emit in sprint 1.
