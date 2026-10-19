# MindIE Agent Architecture & Module Boundaries

[中文](architecture.md) · [Back to Documentation Center](README.en.md)

This document explains what MindIE Agent does, how its repositories are organized, and how remote Ascend execution, the knowledge & experience loop, NPU observability, and fault diagnostics work together.

- For task identity and lifecycle rules, see [Harness Boundary & Lifecycle](harness-boundary-and-lifecycle.en.md).
- For knowledge package format and search design, see [Knowledge & Experience System](knowledge-system.en.md).
- Every component is governed by the [Engineering Design Principles](design-principles.en.md).
- For verified host versions and paired component releases, see the [`0.0.1` Release Record](releases/0.0.1.en.md).

---

## 1. Product Scope & Trigger Modes

MindIE Agent upgrades your existing AI coding CLI (**Claude Code**, **OpenAI Codex CLI**, **Kimi Code**, **DeepSeek Harness**) into an Ascend NPU and LLM inference engineering powerhouse.

- **No reinvented wheels**: We do not ship a proprietary foundation model, replace your host's conversation UI, or take over your source code repository. You work naturally inside your existing terminal and business codebase.
- **Two clear trigger modes (Manual On-Demand vs. Default Auto-Triggered)**:
  - **Manual `/mindie-agent` Trigger (Knowledge, Experience & Skill System)**: When troubleshooting Ascend workloads, adapting operators, or tuning inference, type `/mindie-agent` (or `$mindie-agent` in Codex; DSH uses its native `/mindie-agent` user gesture) followed by your problem description to invoke the Ascend Skill workflow, search verified historical experience packages, and bind the session's experience loop—staying completely out of the way during ordinary non-Ascend coding.
  - **Default Auto-Trigger for `remote-dev` (Remote Ascend Execution)**: `remote-dev` is registered as an always-ready MCP server. Whenever you mention a remote host, container, or NPU command in normal conversation, your Agent automatically invokes `remote-dev` for remote file I/O, patching, and background job execution without needing any slash command.
- **Configure once, persist across sessions**: After setting your contribution preference, public target repository, and project scope once, eligible tasks associate automatically. Historical experience is purely advisory reference material for the Agent—never a mandatory step.
- **Hard Prerequisite: Stable GitHub Channel (`gh` CLI) & Two-Stage Scoped Fork Policy**: Plugin marketplace fetches, locked release verification, `knowledge-vllm-ascend` sync, automated knowledge PR publication (via `gh api` and `!gh auth git-credential`), and opt-in fault reporting all rely on an authenticated `gh` (GitHub CLI) channel. Because the `@mindie-agent` organization hosts 10+ repositories, we enforce a **clean, on-demand Two-Stage Fork Policy**: (1) **Install Time**: After verifying `gh auth status` and `gh auth setup-git`, the Agent Auto-Install Playbook **Stars** and **Forks** (`--clone=false`) **only** the main entry repository `mindie-agent/mindie-agent` (never mass-forking individual plugin or knowledge repos during installation); (2) **When Community Knowledge Contribution Is Enabled (On-Demand)**: Only when the user explicitly opts into contributing to a target public knowledge repository (such as `mindie-agent/knowledge-vllm-ascend`) does the Agent **Star** and **Fork** that specific knowledge repository on demand and bind `fork` (`<GH_USER>/<repo>`) for cross-fork PR publishing.
- **Domain focus**: Our initial focus domain is `vLLM` / `vLLM-Ascend` inference and operator engineering, designed so additional domains can plug in cleanly using the same package architecture.

---

## 2. Repository & Component Ownership

MindIE Agent uses a clean, decoupled architecture across **native Harness plugins**, **shared runtime components**, and **open Markdown knowledge repositories**:

| Component / Repository | Core Responsibility |
| --- | --- |
| [`mindie-agent`](https://github.com/mindie-agent/mindie-agent) (this repo) | Overall architecture, domain boundaries, engineering design principles, cross-component contracts, and unified release records |
| [`mindie-agent-cc`](https://github.com/mindie-agent/mindie-agent-cc), [`mindie-agent-codex`](https://github.com/mindie-agent/mindie-agent-codex), [`mindie-agent-kimi`](https://github.com/mindie-agent/mindie-agent-kimi), [`mindie-agent-dsh`](https://github.com/mindie-agent/mindie-agent-dsh) | **Native Harness Plugins**: Host task identity verification, first-time setup, Hook bridging, public conversation projection, native lightweight model invocation, plugin installation, and silent background updates |
| [`knowledge`](https://github.com/mindie-agent/knowledge) | **Knowledge & Experience Engine**: Durable admission cursors, deterministic privacy redaction, task package assembly, `TechnicalTokenizerV1`-based ReMe lexical & file-graph search (BM25 + `StrictFileGraph` + citation lineage merging), usefulness feedback, and automated PR creation |
| [`knowledge-vllm-ascend`](https://github.com/mindie-agent/knowledge-vllm-ascend) | **Public Domain Knowledge Corpus**: Reviewed, redacted `vLLM-Ascend` Markdown knowledge packages distributed via GitHub for incremental client sync |
| [`remote-dev`](https://github.com/mindie-agent/remote-dev) | **Remote Ascend Execution Substrate**: SSH-backed remote twins for file I/O, AST/symbol outlines, line-scoped editing, patching, grep/glob search, managed long-running background jobs, cancellation, and artifact syncing—maintaining full native tool & parameter parity across 6 Harnesses (Codex, Claude Code, Cursor, Kimi Code, DSH, Antigravity) while consuming `coordinator`'s synchronized `endpoints.json` and Endpoint Resolver |
| [`coordinator`](https://github.com/mindie-agent/coordinator) | **Upgraded SSH & Remote Ascend Environment Manager (Agent-Facing)**: Owns the shared machine inventory (`machines.json` -> auto-synced `endpoints.json`), SSH key bootstrap & multi-node container mesh (`mindie_hosts`), container binding & provisioning (`mindie_container`), agentless NPU/server/mount probing & capacity ranking (`mindie_probe`), lightweight NPU/port lease coordination (`mindie_lease`), and Git-snapshot task execution (`mindie_run`) |
| [`npu-top`](https://github.com/mindie-agent/npu-top) | **Visual Cluster Telemetry Dashboard (Human-Facing)**: Reads `coordinator`'s `machines.json` to serve a live local Web UI (`127.0.0.1:8788`) and 90-day SQLite utilization heatmaps for humans; Agents query NPU/server/mount status directly via `coordinator`'s `mindie_probe` without requiring the human dashboard server |
| [`diagnostics`](https://github.com/mindie-agent/diagnostics) | **Structured Diagnostics & Fault Reporting**: Bounded local structured logs, actionable fault IDs, and opt-in, deduplicated GitHub Issue reporting |
| [`mindie-bench`](https://github.com/mindie-agent/mindie-bench) | **Evaluation & Release Evidence**: Real task evaluation, public contracts for repository release benchmarks, and report aggregation; keeps correctness, reliability, and performance evidence distinct |

The four current Harness plugins package `knowledge`, `remote-dev`, and their direct or transitive `diagnostics` dependency. Host-specific session identity and transcript parsing remain in each adapter. `coordinator` and `npu-top` are independently installed, optional components: the former provides Agent environment management and task coordination, while the latter provides the human monitoring interface. The plugin locks do not include `coordinator`; installing a plugin therefore does not automatically expose its tools. Future integration requires explicit dependencies, tool registration, and host acceptance.

Product release records aggregate versions, source identities, and benchmark results from ten code repositories: five shared or independent components, four plugins, and `mindie-bench`. This documentation repository maintains the aggregate record without inventing a runtime benchmark of its own. See [Paired Component and Plugin Releases](release-compatibility-and-update.en.md#paired-component-and-plugin-releases) for delivery requirements.

---

## 3. The Knowledge Capture & Experience Reuse Loop

How does a hard-won Ascend debugging session become reusable community knowledge without leaking private data or slowing down your terminal?

```mermaid
flowchart LR
    A["Everyday Ascend Engineering Session"] --> C{"Experience sharing enabled for this project?"}
    C -->|Not configured or disabled| R["Return clear status only when queried"]
    C -->|Configured and enabled| H["Fast Stop Hook<br/>Commits task cursor in milliseconds"]
    H --> L["Extract public dialogue & run deterministic redaction<br/>Save 16KB-chunked immutable Markdown blocks"]
    L --> M["Host's lightweight native model generates block titles,<br/>summaries & short task navigation (tasks/&lt;32-char task hash&gt;/index.md)"]
    M --> P["Assemble complete task package<br/>Automatically open GitHub PR"]
    P --> B["Grok Bot reviews safety & compliance"]
    B --> K["Merge into public corpus<br/>(knowledge-vllm-ascend)"]
    K --> S["Clients incrementally sync & rebuild local search index"]
    S --> N["Future tasks search & read relevant<br/>historical blocks on demand"]
    N -.-> F["Optionally submit helpful / not_helpful<br/>feedback after real use"]
    F -.-> B
```

### Why This Loop Is Both Safe and Fast

1. **Honest, distinct states**: Unconfigured, explicitly disabled, out-of-scope project, and component fault are reported as four distinct states—never disguised as "succeeded with empty output."
2. **Millisecond Stop Hooks**: When a turn finishes, the Stop Hook simply records a lightweight durable admission cursor in SQLite and exits immediately with neutral output so it never blocks your terminal or triggers extra model turns.
3. **100% deterministic body redaction; small models only build the table of contents**:
   - Saved blocks contain only **user input**, **public assistant progress**, and **final answers** (stripping raw tool payloads, hidden reasoning traces, and system prompts). Before touching disk or any model, Gitleaks and deterministic privacy rules strip secrets, private IPs, SSH `user@host` strings, and local home paths.
   - The adapter's lightweight native model **only generates titles, search summaries, and the `tasks/<32-char task hash>/index.md` outline—it never rewrites or truncates the primary conversation blocks**.

---

## 4. Knowledge Package Format & Local State Protection

Tracked locally via `current.json` dual-channel pointers (`draft` / `feed`), every task package is stored under `tasks/<32-char task hash>/` using plain, readable Markdown:
- `index.md`: Top-level `mindie-material-task/1` manifest (embedding the `mindie-entry/3` navigation directory) containing the overall task summary, applicability `conditions`, and an ordered table of blocks.
- `blocks/<64-char block hash>.md`: Immutable, 16KB-chunked conversation blocks (`mindie-material-block/1`). When searching, an Agent inspects `index.md` first and loads only the specific block(s) it needs rather than flooding its context window with an entire transcript.

Under the hood:
- **Markdown files are the sole source of truth** for content;
- **SQLite** stores compact cursors, queues, consent bindings, and external operation receipts;
- **ReMe** maintains a derived search index built on `TechnicalTokenizerV1` (tailored for Ascend/vLLM technical identifiers), combining **BM25 lexical search + Markdown heading/file graph (`StrictFileGraph`) + citation lineage merging** (`blocks.sqlite3` incremental checkpoints, without requiring heavy local Embedding vector computation) that can be rebuilt from the Markdown files at any time. If SQLite is missing or corrupted, the runtime reports a clear error while preserving all existing Markdown files rather than treating the error as a "fresh install" and wiping local data.

---

## 5. Usefulness Feedback & Corpus Evolution

After consulting a knowledge package in a real task, an Agent can optionally submit `helpful` or `not_helpful` feedback:
- Feedback is an advisory signal, not a certification of absolute truth, and skipping feedback is completely fine.
- When `vLLM-Ascend` or CANN evolves and an older workaround becomes obsolete, `not_helpful` feedback gives maintainers and automated review a clear signal to update or retire that entry while preserving Git history.

---

## 6. Silent Background Updates & Fault Diagnostics

- **Compatibility-checked silent updates**: Each plugin Release declares its verified Harness version range in `harness-compatibility.json`. Once 24 hours have elapsed since the last check, routine use asynchronously prepares the highest compatible Release in an isolated `uv` environment and switches atomically when the service is idle—preserving your existing consent settings without manual reloads. See [Release Compatibility & Silent Update](release-compatibility-and-update.en.md).
- **Structured logs & opt-in fault reporting**: Components write bounded local structured logs. Users can independently opt into automatic tool-fault reporting, which uploads only allowlisted execution metadata (component, version, stage, error category, duration, exit code) and **never includes transcripts, command arguments, file paths, or credentials**. See [Diagnostics & Fault Reporting](diagnostics-and-reporting.en.md).
