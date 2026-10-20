# 企业网络下的配置与传输

[English](enterprise-network.en.md) · [返回文档中心](README.md)

## 链路与职责

| 链路 | 执行方 | 网络配置来源 |
| --- | --- | --- |
| 插件注册、源码与知识 Feed 拉取 | 宿主插件管理器、Git | 当前进程的代理、Git 配置与系统证书 |
| Python、组件 wheel 与 PyPI 依赖下载 | 四宿主安装器及更新器调用的 uv | 当前进程代理、系统证书、显式 CA 和包源设置 |
| Gitleaks、DSH Release 下载 | Python 标准库 HTTPS | 系统证书、显式 CA 与当前进程代理 |
| 知识贡献 PR、故障 Issue 上传 | Git 与 gh | 当前授权、gh 登录及服务启动时的网络环境 |
| Kimi 本机插件 API、DSH 本机摘要 API | 插件 Python 适配器 | 回环地址直接连接 |
| Bench 模型出口与本机 RPC | mindie-bench 网关及 shim | 模型出口读取代理与 `NO_PROXY`，本机 RPC 直接连接 |
| SSH 文件上传、下载及产物同步 | remote-dev | SSH 配置、目标主机及容器；HTTP 代理不参与 SSH 协议 |
| 资源协调、NPU 观测 | coordinator、npu-top | 远端 SSH 与本地 API；远端镜像拉取使用远端 Docker 的网络配置 |

## 修复设计

依据[设计原则](design-principles.md)第 1、8、9、10、14、15 条：

1. **安装与更新复用系统信任库。** 原生启动命令在下载 Python 前启用 uv 系统证书；内部安装器使用兼容旧版 uv 的环境变量设置默认值，保留用户的 `UV_SYSTEM_CERTS`、`UV_NATIVE_TLS` 选择和显式 CA。`SSL_CERT_FILE`、`SSL_CERT_DIR` 和包源配置继续生效。Kimi 的首次安装与更新统一使用 uv，移除依赖 ensurepip 版本的另一套安装路径。
2. **后台知识服务继承网络环境。** 在共享 `knowledge` 服务上下文中声明代理、CA、包源及 gh 配置路径变量，沿用现有一次性启动上下文。四个插件不各自维护网络状态机。安装配置只保存变量名，值由实际唤醒服务的进程提供。
3. **故障上报服务使用已有环境文件入口。** 启用服务时，自动将必要的代理、CA 和 gh 配置路径写入该服务目录下的私有环境文件；不复制 API Token。显式指定的环境文件优先。网络设置变化时更新现有服务，上传授权和已有回执保持原样。Kimi 的定时更新复用共享组件的同一环境文件实现，当前调用显式提供的变量优先。
4. **回环请求不经过企业代理。** Kimi 插件注册、DSH 摘要和 Bench 的 SSH、知识与重放 RPC 使用标准库 `ProxyHandler({})`，不依赖用户维护 `NO_PROXY`。
5. **外部写入保持现有结果语义。** 不重试结果不确定的 Git push、PR、Issue 或模型请求。证书错误保留原始失败；证书库来自操作系统或用户指定的 CA，不自动信任网络返回的证书。
6. **Bench 模型出口遵循企业 HTTP 代理。** 父进程网关读取 `HTTPS_PROXY` / `ALL_PROXY` 和 `NO_PROXY`，复用标准库 HTTP CONNECT 隧道与系统 TLS 校验；代理认证只发送给代理，不进入模型请求或日志。本机 HTTP relay 直接连接。保留原有流式传输、计量、超时与无自动重试语义。当前企业代理为 `http://` 类型；不支持的代理协议在发送模型请求前明确报错，不降级为直连。

变更只落在对应组件和插件仓；主仓维护本设计和入口文档。后台更新继续复用既有准备、空闲切换和超时预算。

## 企业网络实测

2026-10-20，在启用认证 HTTP 代理的 Windows 环境中：

- GitHub API、源码克隆、Release 附件重定向和 PyPI 均可访问。
- Git 命令启用证书校验后，代码仓与两个领域知识仓克隆成功。
- uv 默认下载 `mindie-diagnostics 0.4.3` 的 GitHub Release wheel 报 `invalid peer certificate: UnknownIssuer`；相同请求使用系统证书成功。
- 同一环境的 PyPI 请求成功，因此只测试 PyPI 不足以验证首次安装与更新。
- 使用系统证书后，真实下载 Python 3.13.16、组件 Release wheel，并完成 Codex 锁定运行时安装（166 个包）。
- 本机 Git 原有 `http.sslVerify=false`。验证现有企业代理在开启校验时正常工作后，已将该设置恢复为 `true`，默认配置下的 GitHub 访问复测成功。
- 修复分支的 Git push 与 GitHub PR 创建成功，覆盖了实际上传链路。
- 本地真实 HTTP/TLS 测试覆盖带认证 CONNECT、显式 CA、`NO_PROXY`、流式计量，以及错误代理下的回环请求。
- A2 `173.125.1.2` 与 A3 `192.168.13.165`、`.156`、`.154` 的 TCP 22 探测均超时；当前网络尚未完成这些主机的 SSH 文件传输实测。

验证覆盖真实 Release 下载、私有环境文件的跨进程消费、既有服务启动上下文、带代理时的本机 HTTP 请求和失败传播。网络凭据不进入测试输出、公共日志或 PR 正文。
