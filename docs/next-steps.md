# MindIE Agent 后续演进路线图

[English](next-steps.en.md) · [返回文档中心](README.md)

当前系统架构与知识闭环设计见 [系统架构与模块分工](architecture.md) 与 [知识与经验闭环设计](knowledge-system.md)，所有迭代遵循 [工程设计原则与演进准则](design-principles.md)。

首发版本 [`0.0.1`](releases/0.0.1.md) 的验证范围与组件组合保留在历史发布记录中。当前推进主产品及四个宿主插件统一 `0.0.2` 的发布闭环；共享组件继续维护各自独立版本号。

本轮重构以核心业务逻辑正确为基准，简化热路径自检、本地单向故障状态、跨仓影子代码与过时兼容层。重构完成、回归测试通过、真实宿主验收与正式 Release 是分别核对的状态，不能以“十仓已修改”宣称四级测试与最终组合已全部完成。

---

## 现阶段推进重点

1. **完成 `0.0.2` 发布闭环并保持 benchmark 常态交付**
   - 修复授权迁移、Windows 上下文保护、调用链超时与源码身份等真实回归；将最终组件 SHA 接入插件实际安装路径，在该组合上核对本地测试、A2/A3 集成、真实宿主与升级验收。
   - 每个代码仓随每次 Release 发布 benchmark JSON、Markdown 与哈希；主仓聚合十仓证据及具体限制，按[配套发布规则](release-compatibility-and-update.md)确认组件正式发布后再交付插件。既有 Tag 与发行记录如有冲突，先明确处置与证据，不能静默覆盖。
   - 继续独立推进真实昇腾任务的端到端评测，衡量知识与经验闭环在算子排障、模型迁移和性能调优中的收益。核心微 benchmark 和功能验收不转换成未经对照实验支持的提效百分比。
2. **更多宿主与领域扩展**
   - **DSH 适配器演进**：在 [`mindie-agent-dsh`](https://github.com/mindie-agent/mindie-agent-dsh) 中持续打磨原生入口、Stop 采集/脱敏/摘要索引、自动 fork 贡献、反馈与诊断，并扩展 `mindie-bench` 的 G3 原生采集与真实远端 NPU 评测。
   - **独立开箱即用 Skills 持续扩充**：在 [`awesome-mindie-skills`](https://github.com/mindie-agent/awesome-mindie-skills) 中沉淀更多昇腾 Profiling、精度比对与算子开发专项指南。
3. **上游宿主问题跟进**
   - 持续跟踪 OpenAI Codex CLI 子代理（Subagent）中断信号向在途工具调用传递的上游修复进展；待上游合入发布后及时补齐验证并更新兼容性声明，不在插件内引入高侵入性的私有杀进程轮询器。
4. **`coordinator` 远端环境管理与 `remote-dev` / `npu-top` 边界收敛**
   - 已将面向 Agent 的 SSH 主机管理（`mindie_hosts`）、昇腾 NPU/节点/权重盘探测（`mindie_probe`）、容器绑定与自动开通（`mindie_container`）以及轻量 NPU/端口租约仲裁（`mindie_lease`）统一收口至 [`coordinator`](https://github.com/mindie-agent/coordinator)，并自动桥接 `machines.json` -> `remote-dev` 的 `endpoints.json`；[`npu-top`](https://github.com/mindie-agent/npu-top) 专注于面向人类的 Web 实时看板与 90 天热力图。
   - 两者当前按需独立安装。四个宿主插件实际打包 `knowledge`、`remote-dev` 与 `diagnostics`，今后若自动暴露 coordinator 工具，需要单独完成依赖接入、工具注册与宿主验证。
5. **持续打磨“零打扰”开发体验**
   - 保持“一句话让 Agent 自动安装、日常开发零手动命令、后台无感更新”的轻量体验，让开发者把精力 100% 放在昇腾与推理核心工程问题上。
