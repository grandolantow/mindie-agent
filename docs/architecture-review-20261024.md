# 并行架构评审与修复（2026-10-24）

[返回文档中心](README.md) · [前次简化记录](architecture-simplification-20261023.md)

主仓负责架构和文档，运行时代码在组件仓库中修复。本轮通过四路 Cursor 并行检查知识引擎、四个宿主适配器、远端执行与编排、评测与诊断，再进行独立源码复核。下列结论只覆盖实际检查和验证的路径。

## 预算和交付只有一个属主

`knowledge/graded/budget.py` 对最终交付的 query、explain 和 mixed payload 统一估算，包含探索上下文及用量字段。固定协议包已经超过请求预算时，以 `budget_met=False` 和 `minimum_tokens` 表达真实下限；单条 explain 合入历史兼容字段后也必须重新判定。

观测写入以最终交付集合为准。一个单元同时出现在结果、卡片和基础卡片中只计一次；不同 revision 分别保留回执。混合子查询不提前登记交付，由最终响应完成裁剪后在一个事务中批量记录。继承前提仅登记为可读，不冒充独立交付。若结果行已裁掉而单元仍在探索 mounted_units 中交付，也必须计数；其多个别名和结果行共用同一去重集合。

导航可以省略正文，仍应保留预算内的旧材料引用。分页游标在已交付预览之后继续，因此只能去掉预览的 excerpt，不能移除其引用后仍沿用原游标。复核修正了 Cursor 一度无条件删除旧材料行的方案，以真实 Store 和 MaterialStore 遍历全部续页并逐条 explain 验证。

四个宿主只负责 MCP 参数、宿主身份和协议适配，直接传递知识引擎已生成的探索结果。再次剥离 L3、重建事实包或归一化 conditional_avoid 会丢失字段，并使引擎预算与实际响应不符。插件变更须在各自已发布的运行时 pin 上成立，不依赖本轮尚未发布的新预算字段。

## 清理错误与远端观测

SSH LocalForward 的调用体和 close 同时失败时，应保留主错误并附加清理诊断。拆分后的实现误用未绑定的 transport，导致 NameError 取代主错误，现已恢复已有的 record_cleanup_failure 调用。attached stream 中确认子进程退出后重复强杀的两段不可达重试已删除，保留有界 wait 和 OwnedProcess 生命周期。

coordinator 刷新运行中的准备任务时，因遗漏 preparation_control 导入，把内部 NameError 记录为 uncertain。恢复正确导入后，原有观测机制能够读取并持久化真实远端状态。这里的修复不改变远端提交、取消或物理设备租约协议。

## 评测与成本边界

默认策略选择器不能读取私有评判答案并生成一份假续跑结果。没有真实执行器时，策略选择阶段与任务续跑分开报告，任务结果标为未执行，续跑和设备成本保持未知。真实执行器只能拿到不含私有判官及参考答案的任务视图。mindie-bench 的可选知识依赖此前仍锁在缺少策略导航 API 的 0.13.0，造成策略测试整组跳过；本轮将该 pin 和 lock 更新到已发布的 0.13.1，并用绑定 PR 源码的隔离运行时验证。

确定性策略选择不消耗模型调用。预留预算与观测到的模型调用分别记录；缺少用量保持未知，已知的选择器和执行器子账仍分别保留。返回的有效结果即使超时也保留其观测结果与用量，单独报告预算合规性；派发执行器后结果未知时不能将实验总成本写成已知的选择器小计。

报告根据实际输入生成结论，并对过滤后的组件视图重新计算证据范围。回放 listener 数、fixture 校准、CPU 行为验证与真实 NPU 或模型收益分别表述。任务验证器执行目标源码的 CPU 行为，检查已知故障、金标修复及无效/部分修复；这些结果不能替代 NPU 验收，也不追溯改变已有 trial 的历史判分。

## 并发修改的归属

另一项工作同时修复手动 /mindie-agent 启用门禁。本轮经用户授权联系该聊天协调，保留其 activation、Skill 和宿主门禁改动。预算和插件 PR 使用独立 Git checkout 提取自己的补丁，原共享 checkout 的未提交工作保留。两项工作不通过整体 stage 重叠文件来交付。

## 验证与 PR

截至当前记录，已经复核提交：

- [knowledge #97](https://github.com/mindie-agent/knowledge/pull/97)：整包预算、最终交付计数和导航/分页。隔离补丁受影响范围 150 passed、1 skipped；补入事实包交付回归后相关范围 49 passed。
- [remote-dev #43](https://github.com/mindie-agent/remote-dev/pull/43)：SSH 清理和不可达重试。先前非 live 全套 660 passed、43 skipped；最终补丁的 SSH 范围 29 passed、18 subtests passed。CI 七项全部通过。
- [coordinator #63](https://github.com/mindie-agent/coordinator/pull/63)：准备任务状态刷新。定向 18 passed、2 skipped；GitHub CI 五项全部通过。

knowledge 的共享源码广检有四个隔离子进程加载陈旧安装包而失败；coordinator 的本地广检有七项基线同样失败。PR 描述保留这些限制，没有将本地全套写成全绿。其余交付：

- [Codex #58](https://github.com/mindie-agent/mindie-agent-codex/pull/58)、[CC #43](https://github.com/mindie-agent/mindie-agent-cc/pull/43)、[Kimi #46](https://github.com/mindie-agent/mindie-agent-kimi/pull/46)、[DSH #16](https://github.com/mindie-agent/mindie-agent-dsh/pull/16)：四端分别为 14/13/9/5 passed，另有 5/16/6/4 subtests passed，均使用已发布 knowledge 0.13.1。主审将 explain 的测试改为真实 explain_closure 输出与有效引用，补齐实际配置；CC 同时补齐 LF 配置和只读校验器。
- [mindie-bench #24](https://github.com/mindie-agent/mindie-bench/pull/24)：报告、策略与成本语义，以及公开知识依赖 pin 修复。PR 独立运行时的受影响范围 49 passed。
- [mindie-bench #25](https://github.com/mindie-agent/mindie-bench/pull/25)：六个行为判分器及重新生成的 soundness 回执；无功能/常量负对照 7 passed。

最终 mindie-bench 合并源码在锁定运行时中串行非 live 全套为 1368 passed、7 skipped、6 deselected，220.78s，峰值 RSS 约 366.9 MiB。七个跳过涉及未装可选 coordinator/profiler/sim 组件或 Linux 环境；六个未运行用例是 live_npu。修正 pin 后策略测试实际运行，不再因缺 API 整组跳过。diagnostics 无需修补，其非 live 范围为 325 passed、4 skipped。

六个判分器已通过正式 runner 重建 soundness 回执：五个 L2 本地检查，以及现有 A5 容器中的 L3 DSpark，均为 before_reward=0、after_reward=1、model_calls=0。L3 前后设备进程列表为空，HBM 均为 4800 MiB；容器镜像已按当前实际 digest 重新绑定。CPU 方法 oracle 的本地峰值 RSS 为约 209–220 MiB。这些检查不重新判定历史 Trial，也不证明 NPU 模型推理性能。

所有新代码和测试保持 LF，并完成 Pre-PR 自查。当前结果不包含新的 A2/A3 验收、端到端模型收益或正式 Release 发布。

## Cursor 模型与 fallback 证据

使用显式参数 `claude-opus-5-5[context=1m,effort=max,fast=false]`，各路初始化返回 `Claude Opus 5.5 1M Max`。初始化标识不能证明后续服务端始终使用同一模型。

知识库、插件和执行链路三个会话在最终输出中收到明确通知：Opus 5.5 触发安全过滤，平台自动切换为 Opus 4.8。这三个会话均未继续使用，日志中通知后无工具调用；不能将它们宣称为全程 Opus 5.5。主审独立复核、修改并重新验证了交付补丁。评测修复和独立只读评审未观察到切换通知；CLI 不提供逐请求服务端后端身份，未出现通知也不能证明不存在静默路由。

评测路的一次全套验证被重复启动且共用临时目录，主审已终止两组进程并作废该次结果；主审随后在修正依赖和运行配置后执行了上述最终串行全套。此处不以失效结果支持通过结论。
