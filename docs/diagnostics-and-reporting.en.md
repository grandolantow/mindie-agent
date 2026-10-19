# Diagnostics & Opt-In Fault Reporting

[中文](diagnostics-and-reporting.md) · [Back to Documentation Center](README.en.md)

This document explains how MindIE Agent records bounded local diagnostic logs, helps Agents pinpoint the exact stage and cause of a tool failure, and supports opt-in GitHub Issue reporting with strict privacy guarantees and deduplication.

- Governed by: [Engineering Design Principles](design-principles.en.md)
- Core Component Repository: [`mindie-agent/diagnostics`](https://github.com/mindie-agent/diagnostics)
- Current Verification Details: [`0.0.2` Release Notes](releases/0.0.2.en.md) (initial release: [`0.0.1`](releases/0.0.1.en.md))

---

## 1. Core Goal: Clear, Actionable, Privacy-Safe Diagnostics

When a remote command or background indexing step fails, a vague error string wastes time for both you and your Agent. MindIE Agent's diagnostic system is designed around two simple goals:
- **Give the Agent immediate clarity**: Every tool failure tells the caller which stage failed, which side effects already completed, and which local diagnostic ID holds the detailed context—so the Agent can fix the issue or switch strategies immediately.
- **Zero daily ceremony**: Neither you nor the Agent needs to manage log pipelines, run end-of-task log analyzers, or worry about automatic background retries.

---

## 2. Unified Contribution Switch & Everyday Experience

1. **Bounded Local Structured Logs (Always Available)**:
   - Components write structured local logs at real operational boundaries. When a tool call fails, the error response includes a random diagnostic correlation ID, a static error category, and a recovery hint alongside the original exit status and cleanup outcome.
2. **A Single Contribution Switch Controls Knowledge Sharing and Fault Reporting**:
   - Setup explains both outgoing actions: contributing redacted knowledge packages within approved project scope and filing allowlisted tool fault metadata in the product repository. **The switch is off by default and takes effect only when explicitly enabled**.
   - The installation profile's `mindie-consent.json` is the sole authority for contribution consent. Reporter configuration stores the destination repository, log roots, and a reference to that consent file; fault recording, queue ingestion, and final submission all verify the same `choice` and `choice_revision`.
   - **Three Distinct States**: The system keeps **configuration written**, **background reporter worker running**, and **external GitHub Issue published** strictly separate. Enabling the switch configures knowledge sharing and provisions the native background reporter, returning their readiness outcomes separately; service startup errors remain visible and can self-heal on subsequent runs. Disabling the switch immediately stops new outgoing sends on both paths while local diagnostic logs and queries remain available.
   - **No Silent Expansion on Upgrade**: Existing `disabled`, `later`, and `read-only` choices stay off across upgrades. Legacy knowledge-only `contribute` records lacking the unified consent revision do **not** automatically gain fault-reporting permission on upgrade; users opt in explicitly once through the unified contribution entry.
   - **Reuses the Verified `gh` Channel**: Automatic reporting uses the authenticated GitHub CLI (`gh`) verified during installation. Plugin-bundled `knowledge`, `remote-dev`, and the background reporter share the same profile diagnostics path; standalone `remote-dev` deployments retain their explicitly configured reporting policy.

---

## 3. Component Responsibilities

| Module / Role | Responsibility |
| --- | --- |
| **Harness Plugin Adapters** (`mindie-agent-cc` / `-codex` / `-kimi` / `-dsh`) | Log native entrypoint, Hook, MCP startup, and protocol errors; provide setup toggles and human-readable status |
| **Runtime Components** (`knowledge` / `remote-dev`) | Record stage, version, monotonic duration, exit code, and cleanup outcome at the exact boundary where an internal fault occurs, cleanly separating normal user-command exits from internal tool bugs |
| **Diagnostics Engine** (`diagnostics`) | Enforce log schemas, allowlist-only redaction, bounded disk rotation, fingerprint deduplication, finite retry budgets, and GitHub Issue creation |
| **GitHub Maintainers** | Investigate reported fault evidence and ship fixes |

When a shared component has already logged an internal fault, it passes a trusted diagnostic reference ID to the outer plugin layer so the same error is never logged or reported twice.

---

## 4. Strict Privacy Boundary: What Can and Cannot Leave Your Machine

Public GitHub Issues are assembled deterministically from **allowlisted metadata fields** without calling any LLM:

- **Allowed in public Issues (code & execution metadata only)**:
  - Component name, package version or Git commit SHA, operation name, stage, static error category/code, duration, exit code, and cleanup outcome. A stable public fault fingerprint supports deduplication; random diagnostic correlation IDs and process clocks stay local.
- **Strictly excluded from public Issues**:
  - **Never included**: User commands, command arguments, environment variables, raw `stdout`/`stderr`, free-text exception messages, conversation transcripts, config files, credentials/tokens, native task IDs, remote job IDs, local or remote file paths, and hostnames or IP addresses.
- **What never triggers an Issue**:
  - Invalid arguments, missing configuration, user cancellation (Interrupt), disabled features, permission errors, ordinary network/SSH authentication failures, and **non-zero exit codes or timeouts from your own remote commands** are normal operational outcomes and never file product-defect Issues.
  - Only unhandled internal exceptions, abnormal crashes of owned helper subprocesses, protocol corruption, or missing package files qualify as reportable tool faults.

---

## 5. Deduplication & Recoverable Delivery Queue (Loop Prevention)

To prevent duplicate Issues and retain pending reports across transient network outages:

1. **Cross-task fingerprint deduplication**:
   - Faults sharing the same component version, operation, stage, error category, and internal stack frame location produce a deterministic fingerprint. Switching sessions or host CLIs never creates a duplicate Issue for an already reported bug; read-only GitHub lookup links matching faults to the existing Issue without spamming comments.
2. **Bounded requests and recoverable pending reports**:
   - Each processing cycle operates under a bounded request deadline. Temporary network or GitHub authentication failures preserve pending records, surface the actual error, and defer retries rather than dropping faults after transient read-only lookup failures.
   - Only a submission that may have reached GitHub without a response is marked `unknown` and reconciled read-only on the next cycle before any write. A subprocess that never started or a request explicitly rejected by the server is never misclassified as `unknown`.
   - If GitHub confirms Issue creation but local receipt persistence fails, the local storage error is reported separately without reversing the completed external result. Disabling the contribution switch stops unsent queue items immediately; re-enabling processes only events recorded under the new consent revision.
3. **No self-reporting loops**:
   - Failures inside the reporter itself stay strictly local so the reporter never files Issues about its own reporting errors.

---

## 6. Local Log Rotation & Artifact Separation

- **Bounded disk usage**: Local logs enforce per-entry and per-segment size limits and automatically prune expired segments during routine maintenance (even when remote Issue reporting is disabled).
- **Reader & writer safety**: Log rotation protects active writers and registered reader cursors so unread segments are never clobbered.
- **User job outputs are never truncated as logs**: In `remote-dev`, `stdout`/`stderr` streams from your remote commands are preserved as formal job output artifacts under the job lifecycle—never truncated by diagnostic log limits.
