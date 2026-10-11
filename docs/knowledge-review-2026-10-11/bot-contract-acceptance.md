# 2026-10-11 Bot 发布契约验收

本轮补齐 10 月 9 日发现的 Bot 可信校验器与公开契约不一致的问题，沿用既有三条 routine。此前的[原生闭环与升级证据](../knowledge-review-2026-10-09/native-acceptance.md)保留其原始版本与失败事实。当前仍是开发版本。

## 可信安装与审核规则

现有 Grok Bot「VA 知识维护」报告完成非 editable 校验器更新：知识核心 `7c99fbb387304c0e4b26ca85c1839bed8b7534be`，`mindie-knowledge 0.11.0`。可信 checkout 干净，HEAD 与 pin 标记一致，导入来自既有 venv 的 site-packages，安装代码与可信 checkout 逐文件一致。旧安装及维护记录保留。安装过程修复了损坏的 pip；这一事实不证明它造成了此前 routine 失败。

操作员在原生应用中刷新并回读了三条已保存 routine：

| routine | 现有触发方式 |
| --- | --- |
| 社区知识 PR 审查 | 指定内容仓库的 pr-opened、pr-closed、pr-merged |
| 社区知识漏事件补查 | 每日 09:06，Asia/Shanghai |
| 社区知识纠错与 Skill 提案 | 每周六 10:03，Asia/Shanghai |

审核从最终待合入的精确 base 读取 `publication-contract.json` 并计算 SHA256；可信安装代码、checkout、pin 标记必须对应其中的 validator 声明。可信校验器以精确 head、base、契约摘要校验完整任务包，结果必须为 `content_only=true`、`review_mode=content`，精确 head 的 `publication-head` 成功后才可合入。代码、契约及 workflow 等开发变更不自动合入。head 或 base 变化后机械校验失效；未知写入先按原身份对账。

保留原权限、锁与回执，不增加 listener、routine、限额、强制模型重写、质量认证或普通任务的必查步骤。补查只检查实际必要组件；恢复迹象、mtime 相同或 pip 损坏不能单独作为业务失败依据。

Bot 的既有环境仅用于 publication、redact 和社区操作。`pip check` 仍报告缺少 `langmem`、`reme-ai` 和 `mindie-diagnostics`；这些模块未在上述实际成功路径加载，因此该环境不记作完整知识 runtime 安装。新的本机隔离运行时按适配器声明完整安装依赖，`uv pip check` 通过。

## 旧 PR 的精确复核

Bot 使用新契约只读复核 [内容 PR #40](https://github.com/mindie-agent/knowledge-vllm-ascend/pull/40)：head `f2c2976bba49667cac25485dc49619b2a164c0a1`，base `38ab4b972df8a12d2e5a7243652aeb1d6bd04de1`，契约摘要 `6a5551335fb3a40c9a90ffaee473da34cfd49eb66975783933530252cbb4ebc6`，exit 0、stderr 空；结果为 content-only、22 个任务包、1 个反馈、254061 bytes、2 个变更文件。GitHub 回读确认其原合入提交仍为 `7509675deb0c6d144ecb77c15f20d9101cdf7533`。全零契约摘要被实际拒绝，exit 1。没有重写或重新合入该 PR。

## 新事件验收

新的隔离原生任务实际运行公开 Python 临时文件示例与独立断言，原生 Stop 自动保存公开用户及助手材料，正文模型调用为零。内置 `gpt-5.6-luna / low` 一次索引整理完成；没有注入 Hook、手工激活或修改 300 秒投稿窗口。验收使用独立 bootstrap 解释器，不借用本机更新器可能回收的旧 generation。

首轮自动创建 [PR #41](https://github.com/mindie-agent/knowledge-vllm-ascend/pull/41)，head `c9a1c274c125f82c079811033f0412f6a041e17c`、base `7509675deb0c6d144ecb77c15f20d9101cdf7533`。两项 CI 与独立可信校验均通过，23 个任务包、1 个反馈、258858 bytes。正常事件使用新契约审核，Bot 的完成回执绑定相同 head、base、摘要和 validator。回执未保存三个汇总计数，本记录的计数来自 CI 与独立校验，没有重跑 Bot 审核补数。

应用审批层因旧维护说明误读而拦住合入，操作员按既有授权仅选择一次 `Allow once`；Bot 随后合入 `ba40b8264f7a2e6433b65261209f72cf872b893f`，其树与候选相同。因此这次不能记为完全无人介入。Bot 已更正旧说明，保留普通内容事件的自动合入授权，应用权限没有扩大。

独立消费者全新状态同步上述公开提交，原生会话 `01a129ad-ad96-7cd2-98fc-cf5eab834375` 的 query 命中目标，explain 来源为 `feed`，文件 SHA256 `67bd7f5c432a16ea7a3d4dfe753cdbd4ba240c53403bfd670737206400425414` 与公开块一致，未反馈或再次贡献。

生产者原生会话 `01a129a3-f297-7d12-90f8-ff4048d6477f` 的续轮再次实际运行零字节文件读取、删除后读取及断言；同一个任务只新增第二块，旧块字节不变。两轮各一次整理，首轮结果未重放。默认窗口后自动创建 [增量 PR #42](https://github.com/mindie-agent/knowledge-vllm-ascend/pull/42)，head `285a0a16d92bdc8be3ed7e69ebc12c7f195c615e`、base `ba40b826`，只新增第二块并修改 manifest。两项 CI 与精确可信校验通过，仍为 23 个任务包、1 个反馈、261379 bytes。

解锁后回读原生应用确认：#42 的正常事件审核已经通过，但自动安全检查再次把维护时的只读要求套到合入，Bot 保留待合入回执。操作员按已有授权回答这一个 PR 的合入请求；Bot 先核对 head、当前 main/base 与两项 CI 未变，再带精确 SHA 执行 squash，合入 `d31e52e26c0b79fdda94f633ff12b2a70d8b0773`，GitHub 时间为 `2026-10-11T07:12:34Z`。Bot 报告完成回执已保存，候选与合入树均为 `b80afe8c7285cd4da0125339f8e3a94ad6e5cb0c`。这次接续未再弹出工具审批卡片，但有明确人工合入应答，因此仍不记为完全无人介入；没有扩大应用权限。

同一个独立消费者随后以一次无模型同步读取该合入提交，得到 23 个任务包，契约摘要匹配。原生消费者续轮 query 将目标任务排在第一，explain 分别读取旧固定引用与新块，均为 `source=feed`、`block_count=2`，当前 revision 为 `8fe60000102a06b013ab19fb84c3cc0de8fcf3a82adb69e545769998ed94a825`。旧块 SHA256 仍为 `67bd7f5c432a16ea7a3d4dfe753cdbd4ba240c53403bfd670737206400425414`，新块为 `366cb9272749ab80cae67cb6a7c28effc6bc66d5fce1e31b31e5d05d80f8ef43`；候选、公开合入和本地消费者文件逐一匹配。旧块 next 指向新块，新块 previous 指回旧块、next 为空，没有替换旧正文或读取旧导航。消费者没有重新执行示例、反馈或贡献，capture、整理尝试和 outbox 均为零。

两个隔离服务已确认空闲后停止并释放消费者锁，临时账号认证副本已删除，真实账号认证与验收材料保留。首轮及增量的公开保存、整理、投稿、审核、合入、同步与原生读取已有实际证据；完全无人介入的 Bot 合入仍未通过，不能用规则文本已澄清或本次人工接续成功代替后续正常事件证据。

## 历史故障与边界

10 月 9 日每日补查的原始错误和失败阶段仍不可确认。Bot 未找到该次本地锁记录或回执，随后 10 月 10 日周纠错、11 日补查已有成功记录。只读公开状态对账未发现可归属于那次运行的写入，但不能据此证明没有发生外部写入。该次未知任务没有重放。缺少日志与文件恢复时间均不能作为确定原因。

本轮不重新证明 Windows 原生 Stop、fork 派发、真实远端/NPU 业务或其他 Harness。受控消费者验证公开材料的分发与读取接口，不代表普通任务的复用收益，也不代表已经正式发布。
