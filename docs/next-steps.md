# MindIE Agent 演进路线与下一步计划

[English](next-steps.en.md) · [返回文档中心](README.md)

系统整体架构与知识闭环设计请参阅 [系统架构与模块分工](architecture.md) 与 [知识与经验闭环设计](knowledge-system.md)，工程准则请参阅 [工程设计原则与演进准则](design-principles.md)。

当前正式发布版本为 [`0.0.2`](releases/0.0.2.md)（主产品与 Codex、Claude Code、Kimi Code、DSH 四个宿主插件统一版本，底层共享组件与 `mindie-bench` 维护独立版本序列；历史首发记录见 [`0.0.1`](releases/0.0.1.md)）。在 `0.0.2` 中，我们完成了跨仓库核心状态机精简、统一贡献与故障上报开关收敛、固定依赖安装闭环，并建立起十个代码仓库随 Release 自动交付基准测试的机制。

---

## 下一阶段推进重点

1. **真实昇腾工程任务的端到端对照评测**
   - 依托 `mindie-bench`（`v0.2.0`）推进受控环境下的端到端任务评测，在相同任务与硬件条件下客观衡量知识检索与经验闭环对算子开发排障、模型迁移和推理性能调优的实际帮助（将端到端任务收益与每次发布随附的组件 CPU 微基准测试明确分开评估）。
2. **宿主体验与测试效率持续改进**
   - 持续跟踪统一贡献开关下的知识 PR 发布与后台故障上报运行表现，优先修复真实开发场景中触发的工具异常，并扩展跨平台宿主自动升级验证。
   - 优化 `remote-dev` 在常备 A2/A3 集群上的实机集成测试套件执行编排，将整批测试耗时从当前的约 51 秒收敛至 Tier 2 的 25 秒目标区间内。
3. **领域知识与开箱即用 Skills 扩展**
   - 在 [`knowledge-vllm-ascend`](https://github.com/mindie-agent/knowledge-vllm-ascend) 与 [`awesome-mindie-skills`](https://github.com/mindie-agent/awesome-mindie-skills) 中继续扩充面向昇腾 AI Infra 全流程（架构设计、`vLLM-Ascend` 特性开发、`AscendC`/`Triton` 算子实现、精度比对与 Profiling 调优）的知识包与专项指南。
   - 在 `mindie-bench` 中进一步补齐面向 DSH 的 G3 原生会话采集与远端 NPU 实机评测能力。
4. **远端环境编排（`coordinator`）与宿主插件的按需演进**
   - 当前 [`coordinator`](https://github.com/mindie-agent/coordinator)（面向 Agent 的 SSH 主机管理、无代理 NPU/节点探测、容器绑定与租约仲裁）与 [`npu-top`](https://github.com/mindie-agent/npu-top)（面向开发者的 Web 实时监控台与 90 天热力图）作为按需独立安装的组件提供服务，四个宿主插件默认打包 `knowledge`、`remote-dev` 与 `diagnostics`。
   - 后续如将 `coordinator` 工具纳入宿主插件默认工具列表，将单独完成依赖锁定、工具注册与多宿主实机验收。
5. **上游宿主 CLI 问题跟进**
   - 持续跟踪 OpenAI Codex CLI 在中断子代理（`spawn_agent`）时向在途 MCP 工具调用传递取消信号的上游修复进展；待上游合入发布后及时验证并更新 `harness-compatibility.json` 版本区间。
