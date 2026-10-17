# MindIE Agent 后续演进路线图

[English](next-steps.en.md) · [返回文档中心](README.md)

当前系统架构与知识闭环设计见 [系统架构与模块分工](architecture.md) 与 [知识与经验闭环设计](knowledge-system.md)，所有迭代遵循 [工程设计原则与演进准则](design-principles.md)。

首发版本 [`0.0.1`](releases/0.0.1.md) 已完成发布，覆盖 Claude Code 与 OpenAI Codex CLI 在 macOS、原生 Windows 与 Windows WSL 上的六个主流开发环境；DeepSeek Harness 适配器 [`mindie-agent-dsh`](https://github.com/mindie-agent/mindie-agent-dsh) `0.0.1` 已正式发布：原生入口、Stop 采集/脱敏/摘要索引、自动 fork 贡献、反馈与诊断，macOS/4090 WSL/Lenovo Windows 实机验收。

---

## 现阶段推进重点

1. **真实业务复用收益评测（End-to-End Benchmark）**
   - 独立推进端到端的昇腾工程任务评测，客观衡量知识与经验闭环在算子排障、模型迁移和性能调优中的实际提效幅度（在基准评测完成前，我们不在版本说明中做未经实测的量化夸大宣传）。
2. **更多宿主与领域扩展**
   - **DSH 适配器补全**：在 [`mindie-agent-dsh`](https://github.com/mindie-agent/mindie-agent-dsh) 后续版本中补齐 Stop 采集、有用性反馈与经验贡献，完成 Windows/Linux 与真实远端 NPU 验收；`0.0.1` 保持只读知识与 `remote-dev` 的稳定边界。
   - **独立开箱即用 Skills 持续扩充**：在 [`awesome-mindie-skills`](https://github.com/mindie-agent/awesome-mindie-skills) 中沉淀更多昇腾 Profiling、精度比对与算子开发专项指南。
3. **上游宿主问题跟进**
   - 持续跟踪 OpenAI Codex CLI 子代理（Subagent）中断信号向在途工具调用传递的上游修复进展；待上游合入发布后及时补齐验证并更新兼容性声明，不在插件内引入高侵入性的私有杀进程轮询器。
4. **`coordinator` 远端环境管理与 `remote-dev` / `npu-top` 边界收敛**
   - 已将面向 Agent 的 SSH 主机管理（`mindie_hosts`）、昇腾 NPU/节点/权重盘探测（`mindie_probe`）、容器绑定与自动开通（`mindie_container`）以及轻量 NPU/端口租约仲裁（`mindie_lease`）统一收口至 [`coordinator`](https://github.com/mindie-agent/coordinator)，并自动桥接 `machines.json` -> `remote-dev` 的 `endpoints.json`；[`npu-top`](https://github.com/mindie-agent/npu-top) 专注于面向人类的 Web 实时看板与 90 天热力图。
5. **持续打磨“零打扰”开发体验**
   - 保持“一句话让 Agent 自动安装、日常开发零手动命令、后台无感更新”的轻量体验，让开发者把精力 100% 放在昇腾与推理核心工程问题上。
