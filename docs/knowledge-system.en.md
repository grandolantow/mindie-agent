# Knowledge & Experience System Design

[中文](knowledge-system.md) · [Back to Documentation Center](README.en.md)

This document explains how MindIE Agent turns real-world Ascend NPU debugging and engineering sessions into structured, reusable Markdown knowledge packages—while keeping private data safe and context windows lean.

- Governed by: [Engineering Design Principles](design-principles.en.md) · [Architecture & Module Boundaries](architecture.en.md)
- Core Engine Repository: [`mindie-agent/knowledge`](https://github.com/mindie-agent/knowledge)
- Public Domain Corpus: [`mindie-agent/knowledge-vllm-ascend`](https://github.com/mindie-agent/knowledge-vllm-ascend)

---

## 1. Five Core Design Ideas

1. **Preserve the Complete Primary Conversation—Never Replace It with a Summary**
   - Many memory systems ask an LLM to rewrite a debugging session into a short paragraph, losing the exact stack traces, environment variables, and diagnostic turning points that actually matter.
   - In MindIE Agent, extracting and redacting public conversation turns is done entirely by **deterministic code** and saved as immutable, 16KB-chunked Markdown blocks (`tasks/<32-char task hash>/blocks/<64-char block hash>.md`). No LLM ever rewrites the body text or truncates the middle of a long task.
2. **Use a Lightweight Native Model Only to Build the "Table of Contents"**
   - So Agents don't have to load massive transcripts into context, each Harness plugin uses its lightweight native model strictly to generate block titles, search summaries, and a task-level navigation manifest (`tasks/<32-char task hash>/index.md`, a top-level `mindie-material-task/1` manifest embedding the `mindie-entry/3` navigation directory).
   - When searching, the Agent reads `index.md` first to see the big picture, then loads only the specific block(s) it needs (`blocks/<64-char block hash>.md`).
3. **Dual-Channel Pointer Isolation (`draft` / `feed`) with One Unified Format**
   - Curated community knowledge (`feed`) and private local task drafts (`draft`) are tracked locally via dual-channel pointers in `current.json`, sharing the exact same `mindie-material-task/1` package format and rebuildable ReMe search index (`blocks.sqlite3` incremental checkpoint).
4. **Fail-Closed Privacy & Explicit Consent**
   - Nothing is collected without explicit project-scope consent. Before any bytes are written to disk, sent to the indexing model, or proposed in a public PR, deterministic privacy rules and Gitleaks secret scanning run automatically.
5. **Advisory Knowledge with Real-World Usefulness Feedback**
   - Knowledge entries are helpful reference leads, never mandatory rules. After consulting an entry in a real task, the consuming Agent can submit `helpful` or `not_helpful` feedback to help the corpus evolve.

---

## 2. End-to-End Pipeline: From Session to Knowledge Package

```mermaid
flowchart TB
    T["Verified Host Session Transcript"] --> P["1. Deterministic Public Message Extraction<br/>(Keep only user input, public progress & final answer)"]
    P --> R["2. Deterministic Privacy Rules + Gitleaks Redaction"]
    R --> B["3. Write 16KB-Chunked Immutable Markdown Blocks<br/>(tasks/&lt;32-char task hash&gt;/blocks/&lt;64-char block hash&gt;.md)"]
    B --> I["4. Lightweight Native Model Builds Navigation<br/>(Update tasks/&lt;32-char task hash&gt;/index.md & advance SQLite cursor)"]
    I --> L["5. Update Local Rebuildable ReMe Index (blocks.sqlite3)<br/>(TechnicalTokenizerV1 BM25 + StrictFileGraph + Citation Lineage Merging)"]
    I --> O{"Community Sharing Enabled?"}
    O -->|No (Local Reuse Only)| L
    O -->|Yes| G["6. Automatically Open Public Package PR<br/>(knowledge-vllm-ascend)"]
    G --> Bot["7. Grok Bot Safety & Compliance Review"]
    Bot --> Sync["8. Incremental Client Sync & Update current.json (draft / feed)"]
```

### 2.1 Step 1: Deterministic Public Message Extraction
- The plugin reads only the explicitly verified transcript of the current task—never scanning arbitrary historical sessions.
- **Only three message types are kept**: **User Input**, **Public Assistant Progress**, and **Final Answers**.
- **Internal noise is stripped**: Raw tool call payloads, hidden reasoning chains, system-injected instructions, and duplicate host wrapper events are deterministically removed.

### 2.2 Step 2: Multi-Stage Privacy Redaction & Safety Gate
- Before writing to disk, calling the indexing model, or opening a PR, `mindie_knowledge.redact` and Gitleaks scanning run automatically.
- Secrets, tokens, private keys, private IPv4 ranges, SSH `user@host` endpoints, local home directory paths (`/Users/...`, `/home/...`, `C:\Users\...`), and email addresses are redacted or blocked.
- **Defense in depth**: Pattern redaction complements explicit consent—only tasks inside the user's authorized project scope are admitted.

### 2.3 Step 3: Immutable Blocks & Small-Model Navigation
- Redacted turns are split along 16KB boundaries into immutable `mindie-material-block/1` files (`tasks/<32-char task hash>/blocks/<64-char block hash>.md`).
- The adapter's lightweight model generates titles, retrieval summaries, and applicability `conditions` for new blocks, writing the top-level `mindie-material-task/1` manifest at `tasks/<32-char task hash>/index.md` (embedding the `mindie-entry/3` navigation directory) while maintaining `draft` / `feed` dual-channel pointers in local `current.json`.
- Long tasks advance incrementally via durable cursors. If an indexing model call fails, the saved Markdown blocks remain intact on disk and the unfinished stage is reported honestly without faking completion or blindly retrying uncertain paid calls.

### 2.4 Step 4: Automated PR Publication & Reconciliation via `gh` and On-Demand Personal Forks
- When community sharing is enabled, the publisher uses the verified **`gh` (GitHub CLI) channel** (binding `!gh auth git-credential` for Git pushes and `gh api` for PR operations) to push the contribution branch to the user's `<GH_USER>/<repo>` Fork (e.g., `<GH_USER>/knowledge-vllm-ascend`) and open or update a cross-fork PR against the target public corpus (e.g., [`knowledge-vllm-ascend`](https://github.com/mindie-agent/knowledge-vllm-ascend)).
- **Fork the Target Knowledge Repository on Demand**: Installation requires no Fork. Once the user enables contribution to `<owner/repo>` (default `mindie-agent/knowledge-vllm-ascend`), create or reuse a personal Fork with `gh repo fork <owner/repo> --clone=false` and bind `fork` to `<GH_USER>/<repo>` for branch pushes and PRs. Stars are optional.
- If a network timeout leaves a PR write in an uncertain state (`unknown`), the next run reconciles read-only via `gh api` before attempting any write, never force-pushing or blindly duplicating PRs.

---

## 3. What a Knowledge Package Looks Like (`tasks/<32-char task hash>/`)

Both local draft experience packages (`draft`) and public packages in [`knowledge-vllm-ascend`](https://github.com/mindie-agent/knowledge-vllm-ascend) (`feed`) are tracked locally via `current.json` dual-channel pointers and follow the exact same directory layout under `tasks/<32-char task hash>/`:

```text
current.json                                # Local dual-channel pointer (draft / feed)
tasks/<32-char task hash>/
├── index.md                                # Top-level mindie-material-task/1 manifest (embeds mindie-entry/3 navigation directory, summary & conditions)
└── blocks/
    ├── <64-char block hash>.md             # 16KB-chunked immutable redacted conversation block 1 (mindie-material-block/1)
    ├── <64-char block hash>.md             # 16KB-chunked immutable redacted conversation block 2
    └── ...
```

- **Read the Outline First (`tasks/<32-char task hash>`)**: Returns `index.md` (the top-level `mindie-material-task/1` manifest with embedded `mindie-entry/3` navigation directory) containing the overall problem summary, applicability conditions, and block table of contents.
- **Read Specific Blocks on Demand (`tasks/<32-char task hash>/blocks/<64-char block hash>.md`)**: Returns that exact 16KB immutable block's Markdown body, block hash, and adjacent block pointers so the Agent loads only the context it needs.

---

## 4. Authoritative Markdown Storage & Rebuildable Indexes

- **Markdown Is the Source of Truth**:
  - **Markdown files** on disk (`index.md` and `blocks/<64-char block hash>.md`) are the sole authoritative store for conversation content;
  - **SQLite** stores compact cursors, queues, consent bindings, and external operation receipts;
  - **ReMe** maintains a derived search index built on `TechnicalTokenizerV1` (tailored for Ascend/vLLM technical identifiers), combining **BM25 lexical search + Markdown heading/file graph (`StrictFileGraph`) + citation lineage merging** with incremental checkpoints in `blocks.sqlite3`—without requiring heavy local Embedding vector computation. The index can be rebuilt from the Markdown files at any time. If SQLite is missing or corrupted, the runtime reports a clear error and protects all existing Markdown files rather than treating it as a fresh install.
- **Citations & Feedback**:
  - Literal citations inside blocks participate in citation lineage merging only when the cited package also matches the current query; citation count never implies official certification.
  - Consuming tasks can optionally submit `helpful` or `not_helpful` feedback after real use to improve ranking and guide corpus maintenance.
