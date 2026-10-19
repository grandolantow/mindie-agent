<p align="center">
  <img src="assets/brand/mindie-agent-logo.png" alt="MindIE Agent logo" width="128" height="128">
</p>

<h1 align="center">MindIE Agent</h1>

<p align="center">
  <strong>Open-Source Agent Toolchain and Engineering Knowledge Base for Ascend NPU AI Infra Design, Development, and Testing</strong>
</p>

<p align="center">
  <a href="https://github.com/mindie-agent/mindie-agent/blob/main/docs/releases/0.0.2.en.md"><img src="https://img.shields.io/badge/release-v0.0.2-7045F5.svg" alt="Release v0.0.2"></a>
  <a href="https://github.com/mindie-agent/mindie-agent-cc"><img src="https://img.shields.io/badge/Claude_Code-Plugin-D97757.svg" alt="Claude Code Plugin"></a>
  <a href="https://github.com/mindie-agent/mindie-agent-codex"><img src="https://img.shields.io/badge/OpenAI_Codex-Plugin-10A37F.svg" alt="OpenAI Codex Plugin"></a>
  <a href="https://github.com/mindie-agent/mindie-agent-kimi"><img src="https://img.shields.io/badge/Kimi_Code-Plugin-2563EB.svg" alt="Kimi Code Plugin"></a>
  <a href="https://github.com/mindie-agent/mindie-agent-dsh"><img src="https://img.shields.io/badge/DeepSeek_Harness-Plugin-0EA5E9.svg" alt="DeepSeek Harness Plugin"></a>
  <a href="https://github.com/mindie-agent/awesome-mindie-skills"><img src="https://img.shields.io/badge/Ascend_AI_Infra-vLLM--Ascend_%7C_AscendC_%7C_Triton-0F766E.svg" alt="Ascend NPU AI Infra"></a>
</p>

<p align="center">
  <a href="./README.md">中文</a> · <strong>English</strong> · <a href="#quick-install">Quick Install</a> · <a href="#scope-and-current-coverage">Scope & Roadmap</a> · <a href="#system-architecture">Architecture</a> · <a href="#usage-and-examples">Usage</a> · <a href="#repositories-and-components">Components</a> · <a href="./docs/README.en.md">Docs</a>
</p>

---

<!-- mindie-value-results:start -->
### 0.0.2 measured results

Small-sample results on fixed tasks, reported separately by host, model and comparison. They are not averaged across models and do not establish a general productivity gain.

G0: native host. G1: add remote-dev. G2: also add knowledge retrieval, shipped Skills and explicit retrieval guidance. G3: capture an earlier task's experience for later tasks.

| Study / host / model | Repeats per task | Pair | Baseline solved/attempts | Candidate solved/attempts | Delivery-time ratio (baseline/candidate) | Mutually solved pairs |
| --- | ---: | --- | ---: | ---: | ---: | ---: |
| dp2 / codex / home/codex/gpt-6.1-sol (xhigh) | 3 | G0 → G2 | 2/3 | 3/3 | 0.975x | 2 |
| dp2 / codex / home/codex/gpt-6.1-sol (xhigh) | 3 | G0 → G1 | 2/3 | 2/3 | 0.963x | 1 |
| dp2 / codex / home/codex/gpt-6.1-sol (xhigh) | 3 | G1 → G2 | 2/3 | 3/3 | 0.789x | 2 |
| stale / codex / home/codex/gpt-6.1-sol (xhigh) | 3 | G1 → G2 | 3/3 | 3/3 | 0.595x | 3 |
| quarot / codex / home/codex/gpt-6.1-sol (xhigh) | 3 | G0 → G2 | 3/3 | 3/3 | 0.689x | 3 |
| quarot / codex / home/codex/gpt-6.1-sol (xhigh) | 3 | G0 → G1 | 3/3 | 3/3 | 1.025x | 3 |
| quarot / codex / home/codex/gpt-6.1-sol (xhigh) | 3 | G1 → G2 | 3/3 | 3/3 | 0.673x | 3 |
| claude-code / claude-code / deepseek-flash | 3 | G0 → G2 | 2/3 | 2/3 | 0.678x | 2 |
| dsh / dsh / deepseek-flash | 3 | G0 → G2 | 2/3 | 3/3 | 0.600x | 2 |
| kimi / kimi / k3 (max) | 3 | G0 → G2 | 2/3 | 1/3 | not measured | 0 |
| knowledge-transfer / codex / home/codex/gpt-6.1-sol (xhigh) | 3 | G1 → G2 | 6/6 | 6/6 | 0.685x | 6 |
| knowledge-transfer / codex / home/codex/gpt-6.1-sol (xhigh) | 3 | G2 → G3 | 6/6 | 6/6 | 1.011x | 6 |

Solved/attempts uses the selected settled evals, with failures in the denominator. Timing includes only tasks solved by both sides: above 1 means the candidate was faster on those pairs; below 1 means slower.

**Knowledge transfer: knowledge-transfer / home/codex/gpt-6.1-sol** — 3 runs, each with 1 seed + 2 distinct eval tasks.
Query returned the seed in 5/6 evals; explain read it in 5/6. Misses remain in the results. Workflow totals below include seed and capture, unlike the eval-only paired timing above.

| Condition | Selected workflow (s) | All executed, including historical attempts (s) |
| --- | ---: | ---: |
| G1 | 1814.9 | 2612.6 |
| G2 | 2662.1 | 4140.8 |
| G3 | 2726.2 | 3312.7 |

**Component scenarios**

- npu-top: 3 replay runs; 24 devices and 16/16 process assignments correct per run; live container-owner checks passed 3/3. Human accuracy: not measured; task time (s): not measured. Replays are not independent hardware samples.
- diagnostics: 3 local HTTP runs turned 9 fault occurrences into 3 reports and 3 POSTs; evidence retained 3/3, redaction 3/3, requests stopped after withdrawal 3/3. Delivery took 60.58-60.64 s, including the production retry wait; GitHub availability and human triage gains were not measured.
- coordinator: 3 contention runs; successful listeners 3 → 6, port conflicts 3 → 0, duplicate device selections 3 → 0. The baseline uses check-then-act, not another atomic scheduler.

[Full results, condition definitions and costs](docs/releases/0.0.2/value-results.md) retain original failures, unknown outcomes, historical attempts and targeted retests. Setup and diagnostic model usage is accounted for separately from task value.
<!-- mindie-value-results:end -->

---

## Quick Install

### Option 1: Let Your Coding Agent Install It

If you use **Claude Code**, **OpenAI Codex CLI**, **Kimi Code**, or **DeepSeek Harness (DSH)**, paste this prompt into your session:

```text
Please install MindIE Agent for me: https://github.com/mindie-agent/mindie-agent
```

When your Agent reads this page, it checks `git`, `uv`, and `gh` (GitHub CLI) authentication, identifies its own host environment, and installs the matching `v0.0.2` plugin and runtime.

<details>
<summary><b>Agent Auto-Install Steps (Parsed by AI Coding Agents — Click to Expand)</b></summary>

> **Instructions for AI Agents**: When the user asks you to install `mindie-agent`, run the following four steps in order:
>
> #### Step 1: Check prerequisites and `gh` authentication
> Plugin fetches, release verification, knowledge sync, automated PR submission, and opt-in fault reporting all use an authenticated `gh` (GitHub CLI) channel. Run:
> ```bash
> git --version && uv --version && gh --version
> gh auth status
> GH_USER=$(gh api user --jq .login) && echo "GitHub channel verified for account: $GH_USER"
> gh auth setup-git
> ```
> - If `gh` is missing, help the user install it first (macOS: `brew install gh`; Windows: `winget install --id GitHub.cli`; Ubuntu / WSL: `sudo apt update && sudo apt install -y gh`).
> - If `gh auth status` fails or `gh api user` cannot reach GitHub, stop and guide the user through `gh auth login` (or setting a valid `GH_TOKEN`) and `gh auth setup-git` until `gh api user --jq .login` returns their GitHub username.
>
> #### Step 2: Prepare contribution only when enabled
> Installation does not require a Star or a repository Fork. Stars are optional support for the project. When the user enables community contribution for a target knowledge repository `<owner/repo>`, create or reuse its remote Fork with `gh repo fork <owner/repo> --clone=false` and bind `$GH_USER/<repo>` as the push target.
>
> #### Step 3: Install the plugin matching your host CLI
> Run only the branch matching your environment (check `claude --version`, `codex --version`, `kimi --version`, or `dsh --version` if needed):
>
> - **Claude Code (`CLAUDECODE` env or `claude` CLI)**:
>   ```bash
>   claude plugin marketplace add "https://github.com/mindie-agent/mindie-agent-cc.git#v0.0.2"
>   claude plugin install mindie-agent@mindie-agent-cc --scope user
>   claude --init-only
>   claude plugin list --json
>   claude mcp list
>   ```
>   *Verification*: `claude plugin list --json` shows `mindie-agent@mindie-agent-cc` (`0.0.2`) enabled, and `claude mcp list` shows both `mindie-knowledge` and `remote-dev` as `Connected`.
>
> - **OpenAI Codex CLI (`CODEX_CI` / `CODEX_THREAD_ID` env or `codex` CLI)**:
>   ```bash
>   codex plugin marketplace add https://github.com/mindie-agent/mindie-agent-codex.git --ref v0.0.2
>   codex plugin add mindie-agent@mindie-agent --json
>   codex plugin list --json
>   ```
>   *Verification*: `codex plugin list --json` shows `mindie-agent@mindie-agent` (`0.0.2`) enabled. Remind the user that starting a new session initializes the locked runtime via `SessionStart`.
>
> - **Kimi Code CLI (`KIMI_CODE_HOME` env or `kimi` CLI)**:
>   ```bash
>   MINDIE_TMP="${TMPDIR:-/tmp}/mindie-agent-kimi-install"
>   rm -rf "$MINDIE_TMP"
>   git clone --depth 1 --branch v0.0.2 https://github.com/mindie-agent/mindie-agent-kimi.git "$MINDIE_TMP"
>   SETUP_OUT=$(python3 "$MINDIE_TMP/scripts/setup.py")
>   echo "$SETUP_OUT"
>   NATIVE_PKG=$(printf '%s\n' "$SETUP_OUT" | python3 -c 'import sys, json; text=sys.stdin.read(); data=json.loads(text[text.find("{"):]); print(data["native_package"])')
>   python3 "$MINDIE_TMP/scripts/install_kimi_plugin.py" --kimi-home "${KIMI_CODE_HOME:-$HOME/.kimi-code}" --plugin-root "$NATIVE_PKG"
>   ```
>   *Verification*: `install_kimi_plugin.py` succeeds; let the user know `/mindie-agent` is ready in Kimi Code.
>
> - **DeepSeek Harness (DSH; `DSH_PROFILE` / `DSH_HOME` env or `dsh` CLI)**:
>   ```bash
>   MINDIE_TMP="${TMPDIR:-/tmp}/mindie-agent-dsh-install"
>   rm -rf "$MINDIE_TMP"
>   git clone --depth 1 --branch v0.0.2 https://github.com/mindie-agent/mindie-agent-dsh.git "$MINDIE_TMP"
>   uv run --quiet --no-project --python 3.11 "$MINDIE_TMP/scripts/setup.py"
>   ```
>   Then install and enable the plugin bundle in the DSH Web **Plugins** page:
>   ```text
>   git+https://github.com/mindie-agent/mindie-agent-dsh.git#v0.0.2
>   ```
>   Or inside a DSH session with the `plugin_manager` tool:
>   ```text
>   plugin_manager(action="install_bundle", target="git+https://github.com/mindie-agent/mindie-agent-dsh.git#v0.0.2")
>   ```
>   *Verification*: `setup.py` reports `status: ready` with `knowledge 0.12.2 / remote-dev 0.10.1 / diagnostics 0.4.3`, and the Plugins page shows `mindie-agent-dsh` enabled. Remind the user to open a new session to use `/mindie-agent`.
>   *Note*: If an earlier DSH `0.0.2` (`828c375...`) is already installed, the updater will not automatically select the same version string; follow the [same-version refresh guide](https://github.com/mindie-agent/mindie-agent-dsh/blob/main/docs/same-version-refresh.md) to explicitly refresh both the runtime and plugin bundle and restart the entire DSH process (see [`0.0.2` Release Notes](docs/releases/0.0.2.en.md#5-dsh-002-same-version-refresh-notice)).
>
> - **Cursor or another generic MCP client (standalone `remote-dev` SSH server)**:
>   Add `remote-dev` to `.mcp.json` (or `.cursor/mcp.json`):
>   ```json
>   {
>     "mcpServers": {
>       "remote-dev": {
>         "type": "stdio",
>         "command": "uvx",
>         "args": ["--from", "git+https://github.com/mindie-agent/remote-dev@v0.10.1", "remote-dev", "server"]
>       }
>     }
>   }
>   ```
>
> #### Step 4: Summarize for the user
> Report:
> 1. Verified `gh` authentication (`$GH_USER`);
> 2. Installed plugin name, version, and MCP status;
> 3. How to use it: type `/mindie-agent` to invoke Ascend domain knowledge and Skills, while `remote-dev` tools trigger automatically when prompts involve remote servers or containers;
> 4. That **community knowledge sharing and automatic fault reporting share a single contribution switch** (off by default). Explicitly enabling it forks/binds the target knowledge repository on demand and provisions the background fault reporter. Public fault Issues contain allowlisted execution metadata only—never conversations, command arguments, paths, or credentials.

</details>

### Option 2: Manual Terminal Install

Ensure `git`, `uv`, and an authenticated `gh` (GitHub CLI) are installed first:

```bash
gh auth status && gh auth setup-git
```

Then run the command for your client:

| Client | Install Command | Repository |
| --- | --- | --- |
| **Claude Code** | `claude plugin marketplace add "https://github.com/mindie-agent/mindie-agent-cc.git#v0.0.2" && claude plugin install mindie-agent@mindie-agent-cc --scope user && claude --init-only` | [`mindie-agent-cc`](https://github.com/mindie-agent/mindie-agent-cc) |
| **OpenAI Codex CLI** | `codex plugin marketplace add https://github.com/mindie-agent/mindie-agent-codex.git --ref v0.0.2 && codex plugin add mindie-agent@mindie-agent --json` | [`mindie-agent-codex`](https://github.com/mindie-agent/mindie-agent-codex) |
| **Kimi Code CLI** | `git clone --branch v0.0.2 https://github.com/mindie-agent/mindie-agent-kimi.git && cd mindie-agent-kimi && python3 scripts/setup.py` | [`mindie-agent-kimi`](https://github.com/mindie-agent/mindie-agent-kimi) |
| **DeepSeek Harness (DSH)** | `git clone --depth 1 --branch v0.0.2 https://github.com/mindie-agent/mindie-agent-dsh.git /tmp/mindie-agent-dsh && uv run --quiet --no-project --python 3.11 /tmp/mindie-agent-dsh/scripts/setup.py`, then enable `git+https://github.com/mindie-agent/mindie-agent-dsh.git#v0.0.2` on the DSH **Plugins** page | [`mindie-agent-dsh`](https://github.com/mindie-agent/mindie-agent-dsh) |
| **Standalone NPU Dashboard (`npu-top`)** | `uvx --from "https://github.com/mindie-agent/npu-top/releases/download/v0.1.9/npu_top-0.1.9-py3-none-any.whl" npu-top serve` | [`npu-top`](https://github.com/mindie-agent/npu-top) |

---

## Scope and Current Coverage

MindIE Agent targets the **Ascend NPU AI Infra lifecycle—spanning architecture design, feature development, operator implementation, and testing/verification**—by equipping existing coding CLIs with domain knowledge retrieval, SSH-backed remote container execution, and privacy-redacted experience capture.

To keep expectations clear, the table below separates **what ships in `0.0.2` today** from **what is planned on the roadmap**:

| Area | Shipped in `0.0.2` Today | Planned Roadmap |
| --- | --- | --- |
| **Host Plugins & Bundled Runtime** | `0.0.2` plugins for Claude Code, OpenAI Codex CLI, Kimi Code, and DeepSeek Harness, bundling and registering `knowledge` (`v0.12.2`), `remote-dev` (`v0.10.1`), and `diagnostics` (`v0.4.3`) | Broader cross-platform update coverage; evaluate integrating `coordinator` tools into default plugin registration |
| **Ascend Domain Knowledge & Skills** | Focused on `vLLM-Ascend` feature development & testing, `AscendC` / `Triton` kernel development, accuracy verification, and profiling ([`knowledge-vllm-ascend`](https://github.com/mindie-agent/knowledge-vllm-ascend) and [`awesome-mindie-skills`](https://github.com/mindie-agent/awesome-mindie-skills)) | Expand knowledge packages and Skills to additional Ascend software stack components and distributed workloads |
| **Remote NPU Execution & Cluster Tools** | `remote-dev` provides 19 SSH tools for remote file I/O, patching, and persistent container jobs; `coordinator` (`v0.5.2`) and `npu-top` (`v0.1.9`) ship as standalone tools installed on demand for environment management, lease arbitration, and Web monitoring | Reduce `remote-dev` live NPU test suite wall time; deepen multi-node container orchestration |
| **Benchmarks & Evaluation** | Every code repository Release ships reproducible CPU microbenchmarks (`benchmark-results.json` / `.md`), aggregated in the product Release | Controlled end-to-end Ascend task evaluations via `mindie-bench` (`v0.2.0`) |

---

## System Architecture

### 1. Layered Architecture

This repository (`mindie-agent`) owns system architecture, cross-component contracts, and product release records only—it contains no runtime code. Thin host adapters connect to shared runtime components:

```mermaid
flowchart TB
  subgraph Clients["AI Coding Clients (Host CLIs)"]
    CC["Claude Code"]
    Codex["OpenAI Codex CLI"]
    Kimi["Kimi Code CLI"]
    DSH["DeepSeek Harness"]
  end

  subgraph Adapters["Thin Native Harness Plugins (v0.0.2)"]
    P_CC["mindie-agent-cc"]
    P_Codex["mindie-agent-codex"]
    P_Kimi["mindie-agent-kimi"]
    P_DSH["mindie-agent-dsh"]
  end

  subgraph Bundled["Plugin-Bundled Runtime Components"]
    Knowledge["mindie-knowledge (v0.12.2)<br/>Local BM25/Graph Search · Deterministic Redaction · Block Indexing"]
    RemoteDev["remote-dev (v0.10.1)<br/>19 SSH Remote Tools · Container Exec · Persistent Jobs"]
    Diag["mindie-diagnostics (v0.4.3)<br/>Bounded JSONL Logs · Allowlist Issue Reporter"]
  end

  subgraph Standalone["Standalone On-Demand Components"]
    Coord["coordinator (v0.5.2)<br/>SSH & Container Env Manager · NPU Probe · Lease Queue"]
    NpuTop["npu-top (v0.1.9)<br/>Live Web Dashboard · 90-Day Heatmaps"]
  end

  subgraph Remote["Remote Ascend Fleet & Public Knowledge"]
    Feed[("knowledge-vllm-ascend<br/>Public Markdown Packages")]
    Cluster[("Remote Ascend NPU Hosts & Containers<br/>Ascend 910B (A2) / 910C (A3) / A5")]
  end

  CC --> P_CC
  Codex --> P_Codex
  Kimi --> P_Kimi
  DSH --> P_DSH

  P_CC & P_Codex & P_Kimi & P_DSH --> Knowledge & RemoteDev & Diag
  Knowledge <--> Feed
  Coord -. "Syncs endpoints.json" .-> RemoteDev
  RemoteDev & Coord --> Cluster
  NpuTop -. "Read-only Web UI" .-> Cluster
```

### 2. Development, Testing, and Knowledge Loop

```mermaid
sequenceDiagram
  autonumber
  actor Dev as Developer
  participant Agent as Coding Agent (Claude / Codex / Kimi / DSH)
  participant Know as mindie-knowledge (Local Service)
  participant NPU as remote-dev (Remote Ascend Container)
  participant Repo as Public Corpus / Diagnostics Repo

  Dev->>Agent: Type /mindie-agent + engineering task (Design / Kernel Dev / Testing / Profiling)
  Agent->>Know: 1. Search domain packages (query) & read relevant 16KB blocks on demand (explain)
  Agent->>NPU: 2. Call remote-dev to edit files, apply patches, and run NPU tests in container
  NPU-->>Agent: Return build, unit test, accuracy/perf results & persistent job logs
  Agent-->>Dev: 3. Deliver verified implementation (optionally submit helpful / not_helpful feedback)
  Note over Agent,Repo: Steps 4–6 run asynchronously in the background ONLY when the unified contribution switch is enabled
  Agent->>Know: 4. Session end (Stop Hook) records incremental task cursor
  Know->>Know: 5. Extract public dialogue + deterministic & Gitleaks redaction + small-model block index
  Know->>Repo: 6. Push redacted package branch to personal Fork & open PR (reporter deduplicates allowlisted tool faults)
```

---

## Usage and Examples

In daily use, `/mindie-agent` is the single command entry point:

| Module | Trigger Mode | How It Works |
| --- | --- | --- |
| **Ascend Domain Knowledge & Skills**<br/>(`mindie-knowledge` + Skills) | **Manual Trigger** (`/mindie-agent`) | Type `/mindie-agent <task description>` (or `$mindie-agent` in Codex) when designing features, writing `AscendC`/`Triton` kernels, building tests, or debugging on Ascend. Initial setup, status checks, and toggling the contribution switch also use `/mindie-agent` + natural language. |
| **Remote Ascend Host & Container Execution**<br/>(`remote-dev`) | **Auto-Triggered** (Always-on MCP) | Mentioning a remote server, container, or NPU build/test command in conversation automatically invokes `remote_read`, `remote_edit`, `remote_bash`, and background job tools. |
| **Experience Capture & Fault Reporting**<br/>(`knowledge` + `diagnostics`) | **Background Async** (Single Unified Switch) | Off by default. Once explicitly enabled, session completion triggers background redaction, block indexing, and knowledge PR creation, while the native reporter files deduplicated, allowlisted tool fault Issues. Disabling the switch immediately stops both outgoing paths. |

### Example Prompts

#### Example 1: Operator Design and Test Plan
```text
/mindie-agent I want to design and implement a custom fused operator in vllm-ascend (with Triton / AscendC kernel support) and add unit + accuracy tests. Check MindIE knowledge and existing conventions to propose the design and test plan.
```

#### Example 2: Sync Code and Run Pytest Inside a Remote Ascend Container
```text
Connect to the vllm-dev container on host 192.0.2.21 (port 22), sync my new operator implementation and unit tests into /workspace/vllm-ascend, and run the full pytest accuracy and benchmark suite on the NPU.
```

#### Example 3: Joint Knowledge Lookup and Remote Profiling
```text
/mindie-agent Using Ascend inference and kernel tuning experience, help me profile decode latency bottlenecks on our remote NPU dev machine, pull the key profiling metrics, and verify an optimization patch.
```

---

## Repositories and Components

### 1. Product Entry & Skills Catalogue

| Repository | Role |
| --- | --- |
| **[`mindie-agent`](https://github.com/mindie-agent/mindie-agent)** *(This Repo)* | System architecture, engineering design principles, release compatibility contracts, ten-repository benchmark aggregation, and release notes (documentation only, no runtime code) |
| **[`awesome-mindie-skills`](https://github.com/mindie-agent/awesome-mindie-skills)** | Curated open-source Agent Skills for Ascend NPU AI Infra, currently covering `vLLM-Ascend`, `AscendC`/`Triton` kernels, accuracy testing, and profiling |

### 2. Native Harness Plugins (Unified at `v0.0.2`)

| Repository | Host Client | Role |
| --- | --- | --- |
| **[`mindie-agent-cc`](https://github.com/mindie-agent/mindie-agent-cc)** | **Claude Code** | Native Claude Code plugin: lifecycle hooks, MCP stdio bridges, and locked runtime management |
| **[`mindie-agent-codex`](https://github.com/mindie-agent/mindie-agent-codex)** | **OpenAI Codex CLI** | Native OpenAI Codex CLI plugin: marketplace installation, incremental `rollout.jsonl` public transcript extraction, and service continuity |
| **[`mindie-agent-kimi`](https://github.com/mindie-agent/mindie-agent-kimi)** | **Kimi Code CLI** | Native Kimi Code plugin: compatibility-checked atomic updates, `wire.jsonl` public dialogue extraction, and MCP bridging |
| **[`mindie-agent-dsh`](https://github.com/mindie-agent/mindie-agent-dsh)** | **DeepSeek Harness (DSH)** | Native DSH plugin: provides the `/mindie-agent` Skill, read-only knowledge MCP, official `remote-dev` MCP, and zstd session capture without overriding built-in DSH presets |

### 3. Shared Runtime & Standalone Components

| Repository | Package / Version | Role |
| --- | --- | --- |
| **[`knowledge`](https://github.com/mindie-agent/knowledge)** | `mindie-knowledge` (`v0.12.2`) | Knowledge and experience engine: local SQLite/BM25 and file-graph retrieval, deterministic privacy redaction, 16KB block indexing, Git PR publishing, and usefulness feedback |
| **[`knowledge-vllm-ascend`](https://github.com/mindie-agent/knowledge-vllm-ascend)** | *(Markdown Corpus)* | Public engineering knowledge packages for `vLLM-Ascend`, operator development, and NPU testing |
| **[`remote-dev`](https://github.com/mindie-agent/remote-dev)** | `remote-dev` (`v0.10.1`) | SSH remote development execution substrate: 19 local tool twins, container execution (consuming `coordinator`'s `endpoints.json`), pooled RPC, and persistent background jobs |
| **[`diagnostics`](https://github.com/mindie-agent/diagnostics)** | `mindie-diagnostics` (`v0.4.3`) | Structured diagnostics library: bounded 4×1 MiB JSONL rotation, offline redacted bundles, and allowlisted GitHub Issue reporting controlled by the unified contribution switch |
| **[`coordinator`](https://github.com/mindie-agent/coordinator)** | `mindie-coordinator` (`v0.5.2`) | *Standalone on-demand install*: Agent-facing SSH host & multi-node container mesh management (`mindie_hosts`), container binding/provisioning (`mindie_container`), agentless NPU/server probing (`mindie_probe`), NPU/port lease arbitration (`mindie_lease`), and snapshot task execution (`mindie_run`) |
| **[`npu-top`](https://github.com/mindie-agent/npu-top)** | `npu-top` (`v0.1.9`) | *Standalone on-demand install*: Human-facing Ascend NPU Web dashboard (`127.0.0.1:8788`) and 90-day SQLite utilization heatmaps (sharing `machines.json`) |
| **[`mindie-bench`](https://github.com/mindie-agent/mindie-bench)** | `mindie-bench` (`v0.2.0`) | Evaluation and release benchmark harness: task evaluation sandbox, retrieval scorer, and the unified runner/collector for per-release repository benchmarks |

---

## Engineering Design Principles

MindIE Agent follows a documented set of **[Engineering Design Principles](./docs/design-principles.en.md)** ([中文](./docs/design-principles.md)):

- **Optimize for Total User Cost**: Reduce comprehension, setup, waiting, and debugging overhead rather than adding procedural ceremony to routine work.
- **Clear Boundaries & Progressive Disclosure**: Tools handle internal state complexity; Skills stay concise and load secondary references on demand; knowledge entries remain advisory reference material with explicit applicability conditions.
- **Reuse Native Mechanisms**: Delegate environment locking, package installation, and process-tree cleanup to host CLIs, `uv`, and OS-native primitives.
- **Honest State & Visible Errors**: Keep `completed`, `failed`, and `unknown` external side effects distinct, and never conflate "configuration written" with "background worker running" or "external publication completed."

---

## Documentation Center

See **[`docs/README.en.md`](./docs/README.en.md)** (**[中文文档中心](./docs/README.md)**) for the full documentation index:

| Topic | 中文 | English |
| --- | --- | --- |
| **System Architecture & Module Boundaries** | [docs/architecture.md](./docs/architecture.md) | [docs/architecture.en.md](./docs/architecture.en.md) |
| **Engineering Design Principles** | [docs/design-principles.md](./docs/design-principles.md) | [docs/design-principles.en.md](./docs/design-principles.en.md) |
| **Knowledge & Experience System** | [docs/knowledge-system.md](./docs/knowledge-system.md) | [docs/knowledge-system.en.md](./docs/knowledge-system.en.md) |
| **Harness Boundary, Consent & Lifecycle** | [docs/harness-boundary-and-lifecycle.md](./docs/harness-boundary-and-lifecycle.md) | [docs/harness-boundary-and-lifecycle.en.md](./docs/harness-boundary-and-lifecycle.en.md) |
| **Native Runtime & Process Reuse** | [docs/native-runtime-reuse.md](./docs/native-runtime-reuse.md) | [docs/native-runtime-reuse.en.md](./docs/native-runtime-reuse.en.md) |
| **Release Compatibility & Silent Update** | [docs/release-compatibility-and-update.md](./docs/release-compatibility-and-update.md) | [docs/release-compatibility-and-update.en.md](./docs/release-compatibility-and-update.en.md) |
| **Diagnostics & Fault Reporting** | [docs/diagnostics-and-reporting.md](./docs/diagnostics-and-reporting.md) | [docs/diagnostics-and-reporting.en.md](./docs/diagnostics-and-reporting.en.md) |
| **Tiered Testing & Release Benchmarks** | [docs/testing-architecture.md](./docs/testing-architecture.md) | [docs/testing-architecture.en.md](./docs/testing-architecture.en.md) |
| **Roadmap & Next Steps** | [docs/next-steps.md](./docs/next-steps.md) | [docs/next-steps.en.md](./docs/next-steps.en.md) |
| **`v0.0.2` Release Notes** | [docs/releases/0.0.2.md](./docs/releases/0.0.2.md) | [docs/releases/0.0.2.en.md](./docs/releases/0.0.2.en.md) |

---

## 📊 Repository & Download Statistics

<p align="center">
  <a href="https://github.com/mindie-agent/mindie-agent/blob/telemetry-data/README.md">
    <img src="https://raw.githubusercontent.com/mindie-agent/mindie-agent/telemetry-data/dashboard.en.svg" alt="MindIE Agent Repository & Download Statistics" width="100%">
  </a>
</p>
