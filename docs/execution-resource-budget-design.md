# 执行资源预期、代码有界性与规格匹配设计

[返回文档中心](README.md) · [设计原则与 PR 自查清单](design-principles.md) · [架构与领域边界](architecture.md)

本文定义资源约束的归属和接线目标。规格判定、资源授予、进程回收和内存硬限额各自回答不同的问题，不能把其中一项的测试当成其余各项的验收。

## 一、实现边界

2026-10-24 源码审查的基线为 remote-dev `b91874e`、coordinator `7a252d0`。下表记录该基线，配套修复仍应按其 PR 的实际合入状态判断；本文不证明安装中的插件已经采用这些变更。

| 能力 | 已有实现 | 尚未完成的接线或验收 |
| --- | --- | --- |
| 资源规格 | remote-dev 的 `WorkloadExpectation`、`HostHardwareSpec`、`normalize_remote_probe_spec`、`evaluate_placement` | 库存在不等于所有任务会使用它；sim/profiler 的真实 CLI 尚未统一接入资源估算与分流 |
| 远端容量 | coordinator 的 `fleet_probe` 采集主机内存、核数与卡/Die 观测 | RuntimePool 的 prepared-root catalog 不含容量；基线中的资源参数不能仅靠该行完成规格判断 |
| 编译并发 | 主机队列限制编译槽位，构建脚本另算 worker 数；两者的 CPU 侧已读 cgroup 配额 | 内存侧仍只读宿主 `MemAvailable`，且槽位数与每槽 worker 数各按同一份预算计算，尚无一次授予、下游复用的每槽配额 |
| 进程所有权 | Windows Job Object；POSIX owner/进程组；Linux 远端 subreaper 与排空回执 | 所有权和退出回收不证明内存有上限 |
| 内存硬限额 | Windows `OwnedProcess(max_memory_mb=...)` 可设置 Job Memory Limit | 仅显式传参才生效；POSIX 路径没有同等内存执行保证，当前不能据此宣称全平台整树限额 |

已有规格判定库不应成为第二个调度器或守护进程。组件提供工作负载预期；实际执行主机的队列负责授予；执行入口复用结果。

## 二、任务预期与容量事实

工作负载在启动前用业务输入声明 CPU、内存、设备和新增显存需求。`TIER_PRESETS` 属于 remote-dev，文档不维护第二份默认值表；档位只是估算起点，不能代替模型尺寸、Trace 规模或单 worker 峰值。

- sim/profiler 应在各自真实入口按模型层数、token/事件规模、明细模式与 Trace 大小估算活跃工作集。估算函数是待接入的设计，当前不引用不存在的 `a3_host_budget.py` 或把规划中的函数写成已实现 API。
- 编译请求的 worker 内存包含编译器/链接器峰值，不能把进程个数或 NPU 数直接当成内存预算。
- 元数据路径只读取配置与 safetensors 头部，不加载权重、不初始化设备上下文。大文件流式读取；长循环保留活跃状态和有界预览，原始日志复用既有落盘与切片机制。

`HostHardwareSpec` 表示一次容量观测。`cpu_cores` 是物理容量，`usable_cpu_cores` 是并发建议使用的可用核数估计；主机可用内存与容器/cgroup 剩余配额需要分别识别，不能把宿主总量当作容器可用量。

### HBM 与设备计数

- `npu_count`/`free_npus` 在统一执行规格中按可独立租用的物理 Die 计数，与 `ASCEND_RT_VISIBLE_DEVICES` 的 Phy-ID 对齐；fleet 的卡级计数仍可用于展示，不能直接充当 A3 双 Die 的执行容量。存在 `free_phy_ids` 时，空列表也是明确的零值。
- 可用 HBM 使用各设备实测的 `total - used`，缺测不等于全部空闲。设备处于 idle/free-for-leasing 不等于物理 HBM 已用量为零。
- 已用量可能包含固件、驱动或运行时保留；仅凭 `npu-smi` 总表不能将其全部归因于固件。不同机器和环境的基线可不同，不硬编码 2–3 GiB 或其他固定扣减量。
- 卡级补充遥测（`npu-smi info -t usages` 对 `0 / 0` 卡的回退查询）只在能唯一对应一个可租用单元时采用：单 Die 卡或没有 Die 行的旧格式卡。多 Die 卡的卡级总量不拆分到各 Die，该卡保持未测量状态，由“缺测不计入可用”处理。补充遥测只增加占用证据，不清除已观测到的进程占用事实；卡级与 Die 级清单由同一处派生，避免出现“卡忙而 Phy-ID 仍在空闲表”的不一致。
- 当前已用量已从 free 中扣除；任务的 `Expected VRAM` 估算新增权重、KV、激活、通信与运行时分配，避免再次扣除同一基线。
- 空闲 Die 的 HBM 总和只提供主机级可行性信息。例如两个各剩 48 GiB 的 Die，不证明某个需 64 GiB 的单 Die 负载能放下。逐设备可行性必须由实际设备授予者按选中 Phy-ID 判定。

## 三、分流判定与实际授予

```mermaid
flowchart LR
    W[组件的资源预期] --> P[按真实本机与远端规格判定]
    H[主机与设备容量观测] --> P
    P --> L[本机满足时本地执行]
    P --> R[远端满足时选择候选主机]
    P --> X[返回不足或缺测的具体维度]
    R --> Q[既有主机队列授予设备与执行份额]
    L --> E[既有执行入口消费授予结果]
    Q --> E
    E --> C[进程所有权、超时与排空]
```

本机满足请求时可以本地执行，包括高配 Windows/macOS/Linux 工作站；不按操作系统名称决定放置。需要远端专属环境或设备时再选择匹配的远端。内存不足一名 worker 时应等待、分流或拒绝，不能仅用 `max(1, ...)` 强行启动。

coordinator 的环境 catalog 负责兼容环境和构建 donor；容量来自同次放置决策的 fleet 快照。显式声明 CPU/内存/HBM 下限时，每个候选主机取一次观测并传给 donor 选择、容器开通检查和后续兼容性判断。未声明这些约束的旧作业不增加探测。探测失败沿用现有 waiting/cache-miss 结果并保留主机错误，不伪装成空集群。

这是候选可行性检查，不能冒充资源保留。编译期间容量可能变化；真正启动设备负载时，已有主机队列仍是当前设备状态和租约的唯一授予者。后续逐设备 HBM 约束应接到这个现有授予点，消费当前观测与请求，不再建立第二套分配账本，也不以准备开始时的旧快照保证启动时显存充足。

规格判定本身是纯算术；采集 fleet 可能需要 SSH。不能把网络探测连同分流都宣称为“毫秒级”。单次 SSH 的 30s 上限不是整次放置的上限：一次探测可能包含主查询、可选的补充查询与缓存写入，候选主机又是串行的，因此不存在一个已证明的外部总时限，也不应由候选数乘单次上限充当该时限。任何外层期限都必须覆盖这些阶段；短于已知内层预算的期限会把 live 探测中途掐断。缓存观测保留其年龄，不能把 cache hit 改写为实时采集。

采样时长落在哪条路径上也要分清。守护进程模式（`_async_progress`）在后台进度工作线程上推进，`status`/`target`/`tail` 以非阻塞方式读取已持久化的事实并报告观测新鲜度，不被探测阻塞；同进程同步调用则要等探测返回。不能因此宣称探测对所有调用零开销，也不能宣称它会阻塞状态查询。

## 四、编译槽位只分配一次预算

当前缺口是“主机槽位数 × 每槽 worker 数”分别按同一份整机内存计算。目标是在现有主机队列授予编译租约时给出每槽份额，下游直接使用，不在每个构建脚本里重新证明整机容量。

1. 实际执行主机读取 CPU 可用配额和内存 headroom；Linux 同时考虑 cgroup CPU 配额、`memory.max - memory.current` 与宿主 `MemAvailable`。本地开发机的 `MAX_JOBS` 不能冒充远端规格。
2. 初期按已配置的并发槽位数静态分份额，避免后续槽位进入时使早先授予失效。对于同质 worker，需满足 `slots * jobs_per_slot <= floor(usable_memory / worker_peak)`，同时受 CPU 配额约束；不够一名 worker 时不授予。
3. `CompileLease` 复用既有授予回执携带份额，`PreparationProcess` 将其传给构建环境。`MAX_JOBS`、`MINDIE_BUILD_JOBS`、`CMAKE_BUILD_PARALLEL_LEVEL` 消费同一个上限；显式降低可以保留，不能绕过授予上限。
4. 在授予到消费的链路与兼容行为完成前，不先删除现有 worker 上限。旧组件无法提供份额时明确说明保护能力未提供，不声称乘积预算已经成立。

这是一项待实施的协议接线，不是已完成的全局资源隔离。是否需要动态份额，留给静态方案的实机观测回答。

## 五、进程回收与内存限额分开验收

Windows Job Object 可以对关联进程设置作业级内存限制；POSIX 进程组和 Linux subreaper 提供所有权、取消和后代排空。[Job Memory Limit](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_extended_limit_information) 与单进程限制不同；[RLIMIT_AS](https://docs.python.org/3/library/resource.html#resource.RLIMIT_AS) 限制单进程地址空间，不能作为整树 RSS 上限的证明。

Linux 的整树内存硬限额应使用实际已部署且有权限的 [cgroup v2 内存控制器](https://docs.kernel.org/admin-guide/cgroup-v2.html#memory-interface-files)；macOS 在没有等价机制时明确报告 observed-only 能力。调用方可按任务需要的执行能力选择目标，不以操作系统名称代替能力探测。任何实现都不能把“传了 max_memory_mb”当作“内核已经执行了该限额”。

清理和记账错误保持可见，但不覆盖已确认的业务结果；外部写的不确定性沿用现有 receipt 语义，不为本地探测或分流创建永久故障状态。

## 六、分期与判别性验收

| 阶段 | 归属与实际改动 | 能证明什么 |
| --- | --- | --- |
| 容量语义 | remote-dev 统一物理 Die/空闲 HBM；coordinator parser 保留实测 HBM，忙闲单独判定 | 真实 A2/A3/A5 golden capture 的单位与可用量正确；不证明任务已实机运行 |
| 放置接线 | coordinator 从真实 catalog 与 fleet seam 执行约束，无约束零新增 probe | TaskClient→service→RuntimePool 的满足/不足/探测失败路径与一次观测复用 |
| 编译份额 | 既有主机队列→CompileLease→PreparationProcess→编译器 | 单测证明乘积上限与接线；实机再验证并发编译的进程数、峰值内存和退出回收 |
| 组件入口 | sim/profiler 在实际 CLI 接入工作集估算与规格分流 | 低规格/高规格主机的分流及不足一个 worker 时不启动；不是全模型仿真精度验收 |
| 内存执行能力 | 各平台既有进程 owner 接入真实内核能力 | Windows/Linux/macOS 分别报告已实现的 hard-limit 或 observed-only；超时回收与内存限制分别验证 |

真实主机验证使用隔离状态目录，不扰动现有工作负载。CPU 单测、容器边界、NPU 执行与模型收益分别记录；没有实机证据的阶段保持待验收。
