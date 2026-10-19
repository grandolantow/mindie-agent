# MindIE Agent Roadmap & Next Steps

[中文](next-steps.md) · [Back to Documentation Center](README.en.md)

For the current system architecture and knowledge loop design, see [Architecture & Module Boundaries](architecture.en.md) and [Knowledge & Experience System](knowledge-system.en.md). All iterations follow the [Engineering Design Principles](design-principles.en.md).

The [current `0.0.2` release record](releases/0.0.2.en.md) lists the product and four aligned Harness plugins, their component combination, benchmarks, and acceptance limits. Runtime components retain independent version sequences; historical [`0.0.1`](releases/0.0.1.en.md) evidence remains separate.

This refactor prioritizes business correctness while simplifying hot-path self-checks, permanent local fault states, duplicated shadow code, and obsolete compatibility layers. Completed refactoring, passing regression tests, real host acceptance, and a published Release are separate states. Changes across ten repositories do not establish that all four testing tiers or the final installed combination have passed.

---

## Current Engineering Priorities

1. **Continuously Verify Unified Contribution and Deliver Release Benchmarks**
   - Keep knowledge contribution, fault recording, ingestion, and pre-publication authorization tied to the same authority. Extend real host installation, upgrade, and background workflow coverage, prioritizing faults reported during actual operation.
   - Retain benchmark JSON, Markdown, and checksums with every code repository Release. Aggregate ten reports and their limits in the product record, publishing components before plugins under the [paired-release rules](release-compatibility-and-update.en.md). Reduce the remote-dev live batch duration that currently exceeds the Tier 2 target.
   - Continue separate end-to-end Ascend task evaluation for operator debugging, model migration, and inference tuning. Core microbenchmarks and functional acceptance do not establish productivity percentages without a controlled comparison.
2. **Broader Host & Domain Coverage**
   - **DSH Adapter Evolution**: Continue refining native entry, Stop capture/redaction/summary indexing, auto-fork contribution, feedback, and diagnostics in [`mindie-agent-dsh`](https://github.com/mindie-agent/mindie-agent-dsh), and extend `mindie-bench` with G3 native capture and live remote-NPU evaluation.
   - **Expand Standalone Skills**: Grow [`awesome-mindie-skills`](https://github.com/mindie-agent/awesome-mindie-skills) with additional ready-to-use workflows for Ascend profiling, accuracy verification, and kernel development.
3. **Upstream Host Issue Tracking**
   - Track upstream fixes in OpenAI Codex CLI for delivering cancellation signals to in-flight tool calls when a child agent (`spawn_agent`) is interrupted, updating our compatibility range once upstream ships the fix rather than adding intrusive process-hunting workarounds.
4. **Unified Remote Environment Management in `coordinator` (`coordinator` + `remote-dev` + `npu-top`)**
   - Agent-facing SSH host/key/mesh management (`mindie_hosts`), agentless Ascend NPU/server/mount probing (`mindie_probe`), container binding/provisioning (`mindie_container`), and lightweight NPU/port lease coordination (`mindie_lease`) are now unified in [`coordinator`](https://github.com/mindie-agent/coordinator) with automatic `machines.json` -> `remote-dev` `endpoints.json` bridging, while [`npu-top`](https://github.com/mindie-agent/npu-top) focuses purely on the human-facing Web dashboard and 90-day utilization heatmaps.
   - Both are currently optional, independently installed components. The four plugins package `knowledge`, `remote-dev`, and `diagnostics`; automatically exposing coordinator tools requires a separate dependency integration, registration, and host validation step.
5. **Keep Everyday Workflows Zero-Ceremony**
   - Maintain a frictionless experience—one-sentence Agent-native installation, zero daily activation commands, and silent background updates—so developers can focus entirely on Ascend engineering.
