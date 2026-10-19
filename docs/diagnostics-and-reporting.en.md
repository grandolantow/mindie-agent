# Diagnostics & Opt-In Fault Reporting

[中文](diagnostics-and-reporting.md) · [Back to Documentation Center](README.en.md)

This document explains how MindIE Agent records bounded local diagnostic logs, helps Agents pinpoint the exact stage and cause of a tool failure, and supports opt-in GitHub Issue reporting with strict privacy guarantees and deduplication.

- Governed by: [Engineering Design Principles](design-principles.en.md)
- Core Component Repository: [`mindie-agent/diagnostics`](https://github.com/mindie-agent/diagnostics)
- Release Verification Details: [`0.0.1` Release Record](releases/0.0.1.en.md)

---

## 1. Core Goal: Clear, Actionable, Privacy-Safe Diagnostics

When a remote command or background indexing step fails, a vague error string wastes time for both you and your Agent. MindIE Agent's diagnostic system is designed around two simple goals:
- **Give the Agent immediate clarity**: Every tool failure tells the caller which stage failed, which side effects already completed, and which local diagnostic ID holds the detailed context—so the Agent can fix the issue or switch strategies immediately.
- **Zero daily ceremony**: Neither you nor the Agent needs to manage log pipelines, run end-of-task log analyzers, or worry about automatic background retries.

---

## 2. One Contribution Switch & Everyday Experience

1. **Bounded Local Structured Logs (Always Available)**:
   - Components write structured local logs at real operational boundaries. When a tool call fails, the error response includes a random diagnostic correlation ID, a static error category, and a recovery hint alongside the original exit status and cleanup outcome.
2. **One contribution switch controls knowledge sharing and fault reporting**:
   - Setup explains both outgoing actions: contributing redacted knowledge within approved project scope and filing allowlisted fault metadata in the product repository. **Both are off until explicitly enabled**; there is no separate fault-reporting choice.
   - The installation profile's `mindie-consent.json` is the sole contribution authority. Reporter configuration stores the destination, log roots, and a reference to that authority. Recording, ingestion, and the final send check the same choice and revision.
   - Enabling prepares both knowledge contribution and the actual native background reporter, returning configuration and service outcomes separately. A saved switch is not proof that the service started. Service failures remain visible and preparation can recover later. Disabling stops new outgoing work in both paths while local logs and queries remain available.
   - Existing deferred or disabled choices remain unchanged. An old knowledge-only approval does not silently expand during upgrade; an explicit unified choice establishes a new consent revision.
   - **Reuses the verified `gh` channel**: Producers and the background reporter use the same profile diagnostics path, preventing an enabled setting from being invisible to recorded faults. Packaged knowledge and `remote-dev` inherit that configuration. Standalone `remote-dev` retains its explicitly configured reporting policy.

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

## 5. Deduplication & Retry Budgets (Loop Prevention)

To prevent duplicate Issues or infinite retry loops during network outages:

1. **Cross-task fingerprint deduplication**:
   - Faults sharing the same component version, operation, stage, error category, and internal stack frame location produce a deterministic fingerprint. Switching sessions or hosts never files a duplicate Issue for an already reported bug; if an open Issue matches, its URL is recorded without spamming comments.
2. **Bounded requests and recoverable pending reports**:
   - Each cycle shares one request deadline. Temporary network or authentication failures retain pending evidence, expose the actual error, and defer retries. A few failed read-only queries must not permanently discard a fault.
   - Only a submission that may have reached GitHub becomes `unknown`. Later cycles reconcile read-only without blindly posting again. A process that never started or an explicitly rejected request is not an uncertain external write.
   - If GitHub confirms an Issue but local receipt storage fails, the local failure is reported separately without reversing the external success. Disabling contribution stops unsent events; reenabling does not backfill events from an earlier consent revision.
3. **No self-reporting loops**:
   - Failures inside the reporter itself stay strictly local so the reporter can never file Issues about its own reporting errors.

---

## 6. Local Log Rotation & Artifact Separation

- **Bounded disk usage**: Local logs enforce per-entry and per-segment size limits and automatically prune expired segments during routine maintenance (even when remote Issue reporting is disabled).
- **Reader & writer safety**: Log rotation protects active writers and registered reader cursors so unread segments are never clobbered.
- **User job outputs are never truncated as logs**: In `remote-dev`, `stdout`/`stderr` streams from your remote commands are preserved as formal job output artifacts under the job lifecycle—never truncated by diagnostic log limits.
