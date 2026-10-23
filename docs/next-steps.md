# MindIE Agent 演进路线与下一步计划

[English](next-steps.en.md) · [返回文档中心](README.md)

系统整体架构与知识闭环设计请参阅 [系统架构与模块分工](architecture.md) 与 [知识与经验闭环设计](knowledge-system.md)，工程准则请参阅 [工程设计原则与演进准则](design-principles.md)。

系统已完成首个正式里程碑版本 **[`v0.1.0`](releases/0.1.0.md)**（[实测报告](releases/0.1.0/value-results.md) · [作者自述](releases/0.1.0/design-philosophy.md)）与发布通道清单（[`channels/0.1.json`](../channels/0.1.json)）构建，落地 `knowledge` 的 L1–L4 渐进式披露、Token 预算门控、`G3` C6 经验蒸馏飞轮与 `G4` `mode="explore"` 无偏探索，补齐 7 大昇腾公共知识库（`450` 个结构化单元），发布 `profiler` 与 `sim` 两大性能分析与建模组件，支持 `diagnostics` CANN/`plog` 确定性故障分诊与 `coordinator` 昇腾 A5 拓扑预检，并完成双模型 18 任务（`109` 场 Trial）真机评测与三端 × 四插件全量验收（各版本详情见[版本发布记录](README.md#版本记录与路线图)）。

---

## 下一阶段推进重点

1. **端到端多宿主产品矩阵（`P0–P3`）常态化评测与知识飞轮演进**
   - 基于 `mindie-bench` 持续扩展跨模型、跨宿主的端到端研发任务与跨任务经验迁移（`P0–P3`）评测覆盖，跟踪 L1–L4 渐进式披露与子上下文事实包在长周期复杂算子与框架调优任务中的净工程收益。
2. **昇腾 A5（950）实机通信展开与竞争校准回填**
   - 按照 [A5 通信展开与竞争校准计划](a5-communication-calibration-todo.md)，在常备 A5 环境上完成 AICPU/AIV 通信展开、资源竞争样本采集与 `mindie-sim` / `mindie-profiler` 参数回填验证。
3. **7 大昇腾公共知识库与开箱即用 Skills 持续扩充**
   - 在 [`knowledge-vllm-ascend`](https://github.com/mindie-agent/knowledge-vllm-ascend)、[`knowledge-operators`](https://github.com/mindie-agent/knowledge-operators)、[`knowledge-infer-core`](https://github.com/mindie-agent/knowledge-infer-core)、[`knowledge-infer-distributed`](https://github.com/mindie-agent/knowledge-infer-distributed)、[`knowledge-infer-observability`](https://github.com/mindie-agent/knowledge-infer-observability)、[`knowledge-infer-ops-compat`](https://github.com/mindie-agent/knowledge-infer-ops-compat)、[`knowledge-agent-engineering`](https://github.com/mindie-agent/knowledge-agent-engineering) 与 [`awesome-mindie-skills`](https://github.com/mindie-agent/awesome-mindie-skills) 中持续沉淀经过真机验证的分级知识单元与专项指南。
4. **远端环境编排（`coordinator`）、性能组件（`profiler` / `sim`）与宿主插件的按需协同**
   - 当前四个宿主插件默认打包 `knowledge`、`remote-dev` 与 `diagnostics`，而 `coordinator`、`profiler`、`sim` 与 `npu-top` 支持按需独立安装或由工程工作流直接调用；后续将根据高频调优场景进一步优化组件间的一键联动体验。
5. **上游宿主 CLI 问题跟进**
   - 持续跟踪 OpenAI Codex CLI 在中断子代理（`spawn_agent`）时向在途 MCP 工具调用传递取消信号的上游修复进展；待上游合入发布后及时验证并更新 `harness-compatibility.json` 版本区间。
