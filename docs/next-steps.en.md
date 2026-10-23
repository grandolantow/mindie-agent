# MindIE Agent Roadmap & Next Steps

[中文](next-steps.md) · [Back to Documentation Center](README.en.md)

For the system architecture and knowledge loop design, see [Architecture & Module Boundaries](architecture.en.md) and [Knowledge & Experience System](knowledge-system.en.md). Engineering guidelines are documented in [Engineering Design Principles](design-principles.en.md).

The ecosystem aligns the product and the four native host plugins (Codex, Claude Code, Kimi Code, and DSH) under a unified milestone + Release Channel Manifest ([`channels/0.1.json`](../channels/0.1.json)) architecture while keeping independent version sequences for shared runtime components and `mindie-bench`. Delivered capabilities include L1–L4 progressive disclosure, token-budget gating, and `mode="explore"` de-biased exploration in `knowledge` across 7 public Ascend domain corpora, standalone `profiler` and `sim` components, deterministic CANN/`plog` fault triage in `diagnostics`, Ascend A5 topology/HCCL preflight support in `coordinator`, and formal benchmark and component-value verification across all twelve code repositories (see [Release Records & Roadmap](README.en.md#release-records--roadmap)).

---

## Upcoming Priorities

1. **End-to-End Multi-Host Product Matrix (`P0–P3`) & Knowledge Flywheel Evolution**
   - Expand cross-model, cross-host end-to-end engineering task and experience-transfer (`P0–P3`) evaluations on `mindie-bench`, tracking net engineering gains from L1–L4 progressive disclosure and subcontext fact packs on complex kernel and serving workloads.
2. **Ascend A5 (950) Live Communication Expansion & Contention Calibration**
   - Execute the [A5 Communication & Contention Calibration Plan](a5-communication-calibration-todo.md) on live A5 hardware to calibrate AICPU/AIV collective expansion and contention parameters in `mindie-sim` and `mindie-profiler`.
3. **Expanding the 7 Public Domain Knowledge Corpora & `awesome-mindie-skills`**
   - Continuously grow verified `L1–L4` units and practical guides across [`knowledge-vllm-ascend`](https://github.com/mindie-agent/knowledge-vllm-ascend), [`knowledge-operators`](https://github.com/mindie-agent/knowledge-operators), [`knowledge-infer-core`](https://github.com/mindie-agent/knowledge-infer-core), [`knowledge-infer-distributed`](https://github.com/mindie-agent/knowledge-infer-distributed), [`knowledge-infer-observability`](https://github.com/mindie-agent/knowledge-infer-observability), [`knowledge-infer-ops-compat`](https://github.com/mindie-agent/knowledge-infer-ops-compat), [`knowledge-agent-engineering`](https://github.com/mindie-agent/knowledge-agent-engineering), and [`awesome-mindie-skills`](https://github.com/mindie-agent/awesome-mindie-skills).
4. **Streamlined Coordination Across `coordinator`, `profiler`, `sim`, and Host Plugins**
   - Today, the four host plugins bundle `knowledge`, `remote-dev`, and `diagnostics` by default, while `coordinator`, `profiler`, `sim`, and `npu-top` are installed standalone on demand or invoked by engineering workflows; we will continue streamlining their on-demand workflow integration.
5. **Upstream Host CLI Tracking**
   - Track upstream fixes in OpenAI Codex CLI for forwarding cancellation signals to in-flight MCP tool calls when a child agent (`spawn_agent`) is interrupted, and update `harness-compatibility.json` once upstream ships the fix.
