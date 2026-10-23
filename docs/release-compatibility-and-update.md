# 版本兼容与无感更新（Release Compatibility & Silent Update）

[English](release-compatibility-and-update.en.md) · [返回文档中心](README.md)

本文说明 MindIE Agent 的双层版本演进架构（特性里程碑与发布通道清单 `Release Channel Manifest`）、组件与插件配套发布规则、单组件独立增量更新、宿主版本兼容性筛选机制，以及三层极速触达与后台无感切换流程。

- 遵循准则：[工程设计原则与演进准则](design-principles.md)
- 当前通道清单：[`channels/0.1.json`](../channels/0.1.json)（`schema: "mindie-release-channel/1"`，`track: "0.1"`）
- 版本与实测记录：[版本发布记录](README.md#版本记录与路线图)

---

## 双层版本演进与发布通道架构（Release Channel Manifest）

MindIE Agent 采用 **`0.Y.0` 特性里程碑 + `0.Y.Z` 通道热修（`channels/0.Y.json`）** 的双层 SemVer 演进机制，将重大版本迭代与日常高频单组件缺陷修复解耦：

| 版本层级 | 版本号形态 | 演进载体与定位 | 宿主插件是否需重发 |
| --- | --- | --- | --- |
| **特性里程碑（Milestone Release）** | `0.Y.0`（如 `0.1.0` → `0.2.0`） | 重大功能演进或跨组件协议升级；配套完整版本发布说明与十二仓全量基准验证 | **是**（四个宿主插件对齐升级至新的 `0.Y.0` 里程碑基线） |
| **通道补丁与单组件热修（Channel Patch / Single-Component Hotfix）** | `0.Y.Z`（如 `0.1.1`、`0.1.2`） | 快速缺陷修复与单组件独立演进；由主仓通道清单（当前活跃通道为 [`channels/0.1.json`](../channels/0.1.json)，`schema: "mindie-release-channel/1"`）驱动 | **否**（仅发布变更组件本身并更新对应通道清单，无需连坐重发 `mindie-agent-codex`、`mindie-agent-cc`、`mindie-agent-kimi`、`mindie-agent-dsh` 四个宿主插件） |

### 1. 通道清单结构（以 `channels/0.1.json` 为例）

[`channels/0.1.json`](../channels/0.1.json) 是当前活跃轨道的唯一权威组件版本清单（`schema: "mindie-release-channel/1"`）：
- **轨道与版本标识**：声明 `track`、`milestone_version` 与当前补丁号 `current_patch_version`（随单组件热修递增）；
- **十二仓精确组件条目（`components`）**：集中登记 `diagnostics`、`profiler`、`sim`、`npu-top`、`remote-dev`、`knowledge`、`coordinator`、四个宿主插件（`mindie-agent-codex`、`mindie-agent-cc`、`mindie-agent-kimi`、`mindie-agent-dsh`）以及 `mindie-bench` 的经过验证版本号（`version`）、GitHub 仓库（`repository`）、Release 标签（`tag`）与不可变 40 位源码提交哈希（`commit` / `revision`）；
- **更新策略声明（`update_policy`）**：
  - `independent_update_allowed: true`：允许在不重发宿主插件的前提下独立更新单个共享组件；
  - `hotfix_trigger_on_error: true`：开启故障/崩溃触发的即时自愈检查；
  - `etag_poll_interval_sec: 3600`：1 小时轻量级 HTTP `ETag` 通道轮询；
  - `background_poll_interval_sec: 86400`：24 小时常规后台全量轮询。

### 2. 单组件独立增量更新（`< 500ms` 空闲原子切换）

当仅单个底层共享组件（例如 `remote-dev` 或 `diagnostics`）修复缺陷并发布新 Tag 时：
1. 维护者只需将该组件的新版本、Tag 与精确 Commit SHA 写入当前通道清单（如 [`channels/0.1.json`](../channels/0.1.json)），并将 `current_patch_version` 递增，无需修改或重发四个宿主插件仓库；
2. 客户端后台更新器对比本地已激活组件版本与通道清单中的目标组件版本，仅针对发生变更的组件执行 `uv` 单包增量替换（复用本地 wheel 缓存与已锁定的其余依赖树）；
3. 待当前 MCP 工具调用、经验采集与索引任务空闲后，在 **`< 500ms`** 窗口内通过排他锁完成唯一安装绑定（Canonical Binding）原子切换。

### 3. 三层极速更新触达（Three-Tier Rapid Rollout）

为了确保关键故障修复与新沉淀的领域知识以最快速度触达开发者，MindIE Agent 建立三层协同触达机制：

1. **(a) 故障/崩溃触发的即时自愈检查（Fault/Crash-Triggered Immediate Self-Healing Check）**：
   - 当 `diagnostics` 或任意 MCP 工具遭遇非预期执行失败或崩溃时（`hotfix_trigger_on_error: true`），更新触发器立即旁路 `24 小时`（`86400s`）常规冷却周期（受最小退避保护以防死循环风暴），在后台异步拉取当前通道清单；
   - 若通道清单中已发布针对该故障组件的热修补丁，立即在后台完成单组件增量准备并在空闲窗口原子自愈切换。
2. **(b) 轻量级 HTTP `ETag` 通道轮询（Lightweight HTTP `ETag` Channel Polling）**：
   - 后台按 `etag_poll_interval_sec: 3600`（1 小时）向通道清单发起带 `If-None-Match` 头的条件请求；通道无更新时直接命中 `304 Not Modified`（零 JSON 解析与环境构建开销），有更新时立即触发增量准备；常规全量检查周期保持 `background_poll_interval_sec: 86400`（24 小时）。
3. **(c) 零代码知识与分诊规则热加载（Zero-Code Knowledge/Rule Feed Hot-Reload）**：
   - 7 大昇腾公共知识库（`L1–L4` 结构化单元）与分诊规则通过 `feed_sync` 通道独立增量拉取并就地热加载，无需走代码发版或重启常驻进程。

---

## 组件与插件配套发布

MindIE Agent 对外发布的是**经过验证的组件与插件组合**。OpenAI Codex CLI、Claude Code、Kimi Code 与 DeepSeek Harness（DSH）四个宿主插件在每个特性里程碑版本跟随主产品统一版本号；底层共享组件（`diagnostics`、`knowledge`、`remote-dev`、`coordinator`、`npu-top`、`profiler`、`sim`）与评测工具 `mindie-bench` 保持各自独立的版本序列，未发生代码改动的组件直接复用已有正式 Release，并在通道热修期间通过 [`channels/0.1.json`](../channels/0.1.json) 独立演进。

### 发布顺序与依赖闭环

里程碑发版遵循**自底向上的拓扑依赖顺序**（单组件通道热修仅需执行对应组件步骤并更新通道清单）：
1. 先发布基础诊断组件 [`diagnostics`](https://github.com/mindie-agent/diagnostics) 与理论仿真求解组件 [`sim`](https://github.com/mindie-agent/sim)；
2. 并行准备并发布依赖它们的 [`remote-dev`](https://github.com/mindie-agent/remote-dev)、[`knowledge`](https://github.com/mindie-agent/knowledge)、[`profiler`](https://github.com/mindie-agent/profiler) 与 [`npu-top`](https://github.com/mindie-agent/npu-top)；
3. 发布锁定正式 `remote-dev` 与 `diagnostics` 版本的 [`coordinator`](https://github.com/mindie-agent/coordinator)；
4. 发布锁定实际运行时依赖的四个宿主插件（[`mindie-agent-codex`](https://github.com/mindie-agent/mindie-agent-codex)、[`mindie-agent-cc`](https://github.com/mindie-agent/mindie-agent-cc)、[`mindie-agent-kimi`](https://github.com/mindie-agent/mindie-agent-kimi)、[`mindie-agent-dsh`](https://github.com/mindie-agent/mindie-agent-dsh)），最后更新 [`channels/0.1.json`](../channels/0.1.json) 并汇总发布主仓库版本说明。
   - 四个宿主插件实际打包并注册 `knowledge`、`remote-dev` 与 `diagnostics`；`coordinator`、`profiler`、`sim` 与 `npu-top` 可作为独立组件按需安装或升级接入。
   - `mindie-bench` 版本独立演进，各仓发布流水线通过固定 Commit SHA 引用其运行器。

在发布任何一个宿主插件 Release 或更新通道清单前，维护者需核对以下清单：

| 发布前检查项 | 核对标准 |
| --- | --- |
| **1. 完整依赖盘点** | 从插件最终源码的 `uv.lock` 或通道清单 `channels/0.1.json` 中提取直接第一方依赖，并结合安装环境盘点间接依赖；列出仓库名、包名、版本号、完整 Commit SHA 与对应 Release Tag |
| **2. 组件已正式发布** | 每个第一方运行时依赖均已发布正式 GitHub Release（`draft=false` 且 `prerelease=false`） |
| **3. 源码与标签严格对齐** | 解引用组件 Release Tag 后的源码 Commit 与插件/通道锁定的 Commit 及安装环境 `direct_url.json` 完全一致；Tag 版本、源码包版本与构建产物元数据一致 |
| **4. 发行产物下载校验** | 从正式 Release 页面下载构建产物，确认包内文件与锁定源码一致 |
| **5. 验收范围清晰记录** | 如实记录实机验收覆盖的客户端版本、操作系统平台、实测源码 SHA 与已知边界 |
| **6. 组合闭环复核** | 确认所有底层依赖组件 Release 均已就绪后再发布插件 Release 或推进 `channels/0.1.json` 的 `current_patch_version` |
| **7. 发布 benchmark 随包交付** | 每个代码仓的新 Release 均附带基于该 Tag 精确源码、在干净工作区上运行通过的基准测试报告 |

### 每次发布的 benchmark 交付

各代码仓在 `benchmarks/release.json` 中声明固定工作负载，由固定版本的 `mindie-bench` 运行器执行。Tag 触发的发布工作流依次完成：版本与源码核验、实际依赖安装、第一方依赖正式 Release 校验、本地合同测试（排除 `live_npu`）、基准测试运行与产物打包。

每个代码仓的新 Release 随构建产物一并交付：

- `benchmark-results.json`：记录仓库、版本、测量前后完整 SHA、工作区干净状态、测试套件摘要、运行环境、每次重复样本值、迭代次数、单位、场景状态与准入结论；
- `benchmark-results.md`：便于直接阅读的测试工作负载、数据与范围说明；

若必选基准场景失败、缺失、超时，或测量期间工作区源码发生变化，发布流水线将直接拦截。公开报告仅包含合成输入描述、环境信息与测量数值，不包含凭据、用户对话或私有路径。

主仓库每次里程碑版本发布均自动校验并汇总 `diagnostics`、`profiler`、`sim`、`npu-top`、`remote-dev`、`knowledge`、`coordinator`、四个宿主插件与 `mindie-bench` 共十二个代码仓的正式评测报告与组件价值实测结果（详见[版本发布记录](README.md#版本记录与路线图)）。

> **说明**：`knowledge` 是代码运行时组件，遵循上述软件 Release 与通道热修规范；而 [`knowledge-vllm-ascend`](https://github.com/mindie-agent/knowledge-vllm-ascend)、[`knowledge-operators`](https://github.com/mindie-agent/knowledge-operators)、[`knowledge-infer-core`](https://github.com/mindie-agent/knowledge-infer-core)、[`knowledge-infer-distributed`](https://github.com/mindie-agent/knowledge-infer-distributed)、[`knowledge-infer-observability`](https://github.com/mindie-agent/knowledge-infer-observability)、[`knowledge-infer-ops-compat`](https://github.com/mindie-agent/knowledge-infer-ops-compat) 与 [`knowledge-agent-engineering`](https://github.com/mindie-agent/knowledge-agent-engineering) 是领域知识内容仓库，按固定的内容契约通过零代码知识流（Feed Hot-Reload）持续合入更新，日常新增知识单元无需同步发布软件版本。

---

## 宿主兼容性声明与版本选择

不同版本的宿主 CLI（如 Claude Code 或 OpenAI Codex CLI）在 Hook 参数、MCP 超时控制和环境变量传递上可能存在差异。为了防止“插件自动升级后在当前旧版宿主上跑崩”，我们采用确定性的兼容筛选机制：

1. **机器可读的兼容性清单（`harness-compatibility.json`）**：
   - 每个插件仓库维护一份 `harness-compatibility.json`，集中登记插件实际调用的所有宿主接口（Hook、MCP、CLI 参数、环境变量）、代码调用位置、官方依据、测试用例以及经过验证的宿主 SemVer 版本区间。
   - 发布前门禁脚本会自动校验：插件声明支持的宿主版本区间，必须完全落在所有必需接口的支持区间交集之内。
2. **自动匹配最高兼容正式版与通道补丁**：
   - 无论是首次安装还是后续更新，共享版本选择器都会根据本机当前安装的宿主版本，利用标准 SemVer 规则选出**当前宿主能用的最高兼容里程碑正式版（Ordinary Release）**，并结合对应轨道的通道清单（如 [`channels/0.1.json`](../channels/0.1.json)）应用最新的 `0.1.x` 单组件热修版本。
   - 绝不自动降级，也绝不把 `draft`、`prerelease` 或开发中的 `main` 分支当成正式版本推送给用户。

---

## 后台静默检查与无感原子切换

客户端通过**轻量级 HTTP `ETag` 通道轮询（每 `3600s` / 1 小时）**、**常规后台全量轮询（每 `86400s` / 24 小时）**以及**故障触发的即时自愈检查（`hotfix_trigger_on_error: true`）**在后台异步检测更新。整个过程遵循“**零打扰、零阻塞、`< 500ms` 空闲原子切换**”原则：

- **日常调用零网络阻塞**：日常工具调用和会话启动只做极轻量的本地时间戳判断（毫秒级），绝不在前台等待网络请求、扫描版本列表或构建虚拟环境；高频触发的短时 Stop Hook 更不会执行任何联网或安装动作。
- **不弹窗、不重置授权**：静默更新不会弹出确认框、不发打扰通知、不要求用户手动敲 Reload，并且完整保留用户已配置的知识贡献开关、项目范围和故障上报设置。
- **失败退避与幂等保护**：如果断网或遇到 GitHub 限流，检查失败会触发退避策略，不会在接下来的每次工具调用中疯狂重试；已经下载准备好的候选版本会直接等待空闲窗口切换，不会重复下载。

### 四步安全切换流程

```mermaid
flowchart LR
    P["1. 后台独立准备<br/>全量构建或 uv 单包增量替换"] --> W["2. 等待服务空闲<br/>有在途 RPC / 采集 / 索引时推迟切换"]
    W --> S["3. 排他锁原子切换 (< 500ms)<br/>退役旧服务 -> 校验新服务就绪 -> 切换唯一绑定"]
    S --> R["4. 平滑恢复服务<br/>后续调用自动读取新绑定，无需手动 Reload"]
```

1. **后台独立准备**：在当前运行环境之外下载目标版本；若是 `0.Y.0` 里程碑升级则执行 `uv sync --locked --no-editable` 构建完整隔离环境，若是 `0.1.x` 单组件通道热修则仅针对变更组件执行 `uv` 单包增量替换并完成包校验。如果准备失败，直接保留当前可用版本，丝毫不影响正在进行的业务。
2. **等待服务空闲**：只要还有正在执行的工具调用、已入队的经验采集或摘要索引任务，就继续使用旧版本服务，绝不强行中断在途任务。
3. **排他锁原子切换（`< 500ms`）**：确认旧服务完全空闲后，短暂获取排他操作锁，干净退役旧后台进程，确认新服务就绪后，在 `< 500ms` 内将解释器、入口脚本与引擎配置作为一个整体原子更新到唯一安装绑定（Canonical Binding）。
4. **平滑承接后续请求**：在亚秒级的短暂切换窗口内，新进入的请求会短暂等待或收到明确的“暂时繁忙、尚未执行”提示；切换完成后，即使是不重启的老会话，下一次触发 Hook 或工具调用时也会自动读取新绑定，真正做到无感升级。
