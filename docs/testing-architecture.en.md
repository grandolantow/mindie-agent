# Tiered Testing Architecture & Case Design Guidelines

[中文](testing-architecture.md) · [Back to Documentation Center](README.en.md)

This document defines the unified **Test Validity Redlines** and **Four-Tier Testing Pyramid (Tier 0 – Tier 3)** across all MindIE Agent repositories (`knowledge`, `remote-dev`, `coordinator`, `npu-top`, `diagnostics`, native Harness plugins, and `mindie-bench`). Designed around **always-available live Ascend A2 (910B) and A3 (910C) NPU clusters**, our testing architecture maximizes defect-detection signal while keeping execution fast.

These are design targets, not a claim that every repository has completed all four tiers or meets the listed duration budgets. Release records must name the actual source, cases, environment, duration, and missing coverage. A successful single probe does not establish acceptance of the complete release combination.

- Governed by: [Engineering Design Principles](design-principles.en.md) · [Architecture & Module Boundaries](architecture.en.md)

---

## 1. Test Validity Redlines (Every Test Must Earn Its Keep)

A test is valuable only if it catches real production bugs or contract regressions at minimal time and maintenance cost. Across all repositories, the following five categories of filler or deceptive tests are strictly prohibited:

1. **No Defensive Paranoia Filler Tests**:
   - Never write tests that merely exercise Python type checks, trivial attribute assignments, defensive `ValueError` / `TypeError` branches, or repetitive `chmod 0o777` / `symlink` hypothetical scenarios without testing core business invariants.
2. **No Tests Ratifying Silent Fallbacks or Fake Success**:
   - Never write tests asserting that an underlying database failure, subprocess timeout, or binding error returns `exit 0` / `{}` / `status="active"`. Failure tests must verify that errors are surfaced honestly and that local bookkeeping timeouts never overwrite succeeded remote results.
3. **No Static Constant, Enum, or Signature Roll-Call Tests**:
   - Never write tests that simply assert the literal contents of static dictionaries, constant tables, enum string lists, `inspect.signature` parameter defaults, or schema field names.
4. **No Regex/Grep Tests Against Documentation or Prompt Prose**:
   - Never grep `README.md`, `SKILL.md`, prompt templates, or markdown headings in unit tests. Documentation is maintained through architectural review; tests must verify executable runtime behavior.
5. **No Production-Script Tampering or Unfaithful `MagicMock` Fabrication**:
   - Never overwrite production script files (e.g., replacing `admission_ops.py` with fake stubs) inside a test to force a pass;
   - Never use `MagicMock` payloads that diverge from real server/hardware responses to fake a passing test. Offline parser tests must run against real Ascend hardware **Golden Captures**, and state-machine tests must exercise real in-memory loops (such as `InMemoryHostQueue`) or real temporary SQLite/Git instances.

---

## 2. The Four-Tier Testing Pyramid (Tier 0 – Tier 3, Live A2/A3 NPU Ready)

```mermaid
flowchart TB
    T3["Tier 3: End-to-End Host CLI & mindie-bench Live Canary Acceptance (&lt; 90s)<br/>Drive real host CLIs and mindie-bench Canary tasks end to end"]
    T2["Tier 2: Non-Destructive Live A2/A3 NPU Integration @pytest.mark.live_npu (&lt; 25s)<br/>Connect to A2 (173.125.1.2) & A3 (192.168.13.165/.156/.154) in isolated sandboxes"]
    T1["Tier 1: Local Component Contract & Process Boundary Tests (&lt; 15s)<br/>Reuse session-scoped Git/SQLite templates; verify cross-process locks, python -I & millisecond timeouts"]
    T0["Tier 0: Pure In-Memory Core Logic Unit Tests (&lt; 5s)<br/>Zero subprocesses · Zero network · Zero sleep · Real hardware Golden Captures · InMemoryHostQueue loops"]
    T0 --> T1 --> T2 --> T3
```

| Tier | Time Budget | When to Run | Coverage Scope & Hard Rules |
| --- | --- | --- | --- |
| **Tier 0**<br/>Pure In-Memory Core Unit Tests | **`< 5s`** | Every save / Every commit | **Zero external subprocesses, zero network, zero `sleep`**. Covers parsers (backed by real A2 910B / A3 910C / A5 hardware Golden Captures), state-machine transitions (`InMemoryHostQueue` and real in-memory loops), deterministic privacy redaction, `TechnicalTokenizerV1` tokenization, and protocol translation. |
| **Tier 1**<br/>Local Component Contract & Process Boundary Tests | **`< 15s`** | Component changes / Pre-PR gate | **Reuses session-scoped pre-built Git/SQLite templates** (`shutil.copytree` in milliseconds). Verifies cross-process file locks, `python -I` isolated startup, MCP stdio framing, and millisecond injectable timeout reclamation. **Never run network `pip install` or 10MB+ `fsync` disk bombs inside tests**. |
| **Tier 2**<br/>Non-Destructive Live A2/A3 NPU Integration (`@pytest.mark.live_npu`) | **`< 25s`** | Routine gate for remote execution, probing, containers, leases, or NPU tools | Connects directly to the standing **A2 (`173.125.1.2`)** and **A3 (`192.168.13.165` / `.156` / `.154`)** clusters using isolated sandbox directories (e.g., `state_dir="/tmp/mindie-npu-test-<uuid>"`) without disturbing active workloads. Verifies live `npu-smi` probing, multi-Die `Phy-ID` mapping, Docker container pass-through, Linux `/proc` process-tree draining, and lease anti-preemption. |
| **Tier 3**<br/>End-to-End Host CLI & `mindie-bench` Live Acceptance | **`< 90s`** | Plugin releases / Cross-repo integration / Benchmark changes | Drives real host CLIs (Claude Code, Codex, Kimi Code, DSH) and `mindie-bench` Canary tasks through the full loop: prompt trigger, knowledge retrieval, remote NPU verification, and experience capture. |

---

## 3. Tier Design Rules & Best Practices

### 3.1 Tier 0: Hardware Golden Captures & In-Memory Loops Over `MagicMock`
- **Authentic Hardware Captures**: Parser tests for `npu-smi info`, `npu-smi info -t board`, `lscpu`, container mounts, and CANN stack traces must use verbatim Golden Captures collected from real A2 (910B), A3 (910C dual-Die), and A5 nodes.
- **Zero-`sleep` Time Advancement**: Test retry backoffs, lease expiration, incremental checkpoints, and sliding windows via injectable monotonic clocks (`clock` / `now_fn`), never `time.sleep(...)`.

### 3.2 Tier 1: Session-Scoped Template Fixtures & Injectable Timeouts
- **Pre-built Template Reuse**: Any test requiring a Git repository (`git init` + `commit`) or SQLite schema initialization must clone from a `scope="session"` template fixture via `shutil.copytree`, keeping per-test setup in the single-digit millisecond range.
- **Millisecond Process Lifecycle Verification**: Exercise subprocess cancellation, hang recovery, and `owner-pipe` / `systemd` / Job Object cleanup by injecting `50ms–100ms` timeouts rather than multi-second waits.

### 3.3 Tier 2: Non-Destructive Live A2/A3 NPU Sandbox Rules (`@pytest.mark.live_npu`)
- **Always-On Cluster Access**: Standing SSH access to A2 (`173.125.1.2`) and A3 (`192.168.13.165` / `.156` / `.154`) is standard in our development environment. Changes touching hardware topology, remote file sync, or container execution must be verified with `@pytest.mark.live_npu`.
- **Strict Non-Interference & Sandbox Isolation**:
  - All remote state and scratch files must live inside an isolated `/tmp/mindie-npu-test-<uuid>` directory and be cleaned up on fixture teardown;
  - Never modify, restart, or preempt running production containers, training/inference jobs, or shared host configuration files;
  - Lease and process-tree drain tests operate strictly on self-spawned lightweight test processes and sandboxed lease namespaces.

### 3.4 Tier 3: Host CLI & `mindie-bench` Canary Loop
- In `mindie-bench`, the test suite focuses on recipe materialization, workspace isolation (source projection / worktree), verifier soundness, telemetry/cost settlement, and live Canary task execution—keeping the benchmark harness fast, deterministic, and free of dead-branch filler tests.

## 4. CI Separation & Release Benchmarks

Ordinary PR/branch CI and pre-release local contract stages use `pytest -m "not live_npu"` or an equivalent explicit component entrypoint. They do not automatically access standing clusters or invoke paid host models. Every real NPU case carries `live_npu`; an environment-variable opt-in may supplement this marker but cannot replace it. Direct calls to `mcp_server.handle()` remain component contracts. Tier 3 host acceptance requires the actual host CLI path.

Every code repository owns `benchmarks/release.json` and executable workloads. Each benchmark iteration performs real business operations and checks their output, recording independent repetitions, sample counts, iterations, values, and units. The release workflow first verifies local contracts and formally published dependencies, then measures the clean candidate using an immutable `mindie-bench` runner. Required cases must pass, and source SHAs before and after measurement must equal the tag, before publication can proceed.

| Evidence | Supported conclusion | Validation it cannot replace |
| --- | --- | --- |
| Local business regression tests | Specified consent, protocol, state, and error contracts hold | Actual host or NPU behavior |
| CPU microbenchmark | Latency or throughput of a core operation on fixed inputs | Network/NPU performance or Agent productivity |
| Non-destructive A2/A3 integration | Observed behavior on the named hardware, containers, and source | Unexecuted platforms or a complete host loop |
| Real host and Canary | End-to-end behavior for the named version, platform, and task | A statistically designed productivity comparison |

Each Release includes `benchmark-results.json`, `benchmark-results.md`, and `benchmark-SHA256SUMS`, covered by the full `SHA256SUMS`. Public reports contain publishable workload descriptions and measurements; raw failure logs, user inputs, and credentials are not published with them. The product repository aggregates ten code repositories without adding a documentation benchmark. See [Benchmark Evidence on Every Release](release-compatibility-and-update.en.md#benchmark-evidence-on-every-release).
