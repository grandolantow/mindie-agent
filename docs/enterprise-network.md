# 企业网络下的配置与传输

[English](enterprise-network.en.md) · [返回文档中心](README.md)

## 链路与职责

| 链路 | 执行方 | 网络配置来源 |
| --- | --- | --- |
| 插件注册、源码与知识 Feed 拉取 | 宿主插件管理器、Git | 当前进程的代理、Git 配置与系统证书 |
| Python、组件 wheel 与 PyPI 依赖下载 | 四宿主安装器及更新器调用的 uv | 当前进程代理、系统证书、显式 CA 和包源设置 |
| Gitleaks、DSH Release 下载 | Python 标准库 HTTPS | 系统证书、显式 CA 与当前进程代理 |
| 知识贡献 PR、故障 Issue 上传 | Git 与 gh | 当前授权、gh 登录及服务启动时的网络环境 |
| knowledge 本机 RPC、Kimi 插件 API、DSH 摘要 API | 共享知识客户端与插件 Python 适配器 | 回环地址直接连接 |
| Bench 模型出口与本机 RPC | mindie-bench 网关及 shim | 模型出口读取代理与 `NO_PROXY`，本机 RPC 直接连接 |
| SSH 文件上传、下载及产物同步 | remote-dev | SSH 配置、目标主机及容器；HTTP 代理不参与 SSH 协议 |
| 资源协调、NPU 观测 | coordinator、npu-top | 远端 SSH 与本地 API；远端镜像拉取使用远端 Docker 的网络配置 |

## 修复设计

依据[设计原则](design-principles.md)第 1、8、9、10、14、15 条：

1. **安装与更新复用系统信任库。** 原生启动命令在下载 Python 前启用 uv 系统证书；内部安装器使用兼容旧版 uv 的环境变量设置默认值，保留用户的 `UV_SYSTEM_CERTS`、`UV_NATIVE_TLS` 选择和显式 CA。`SSL_CERT_FILE`、`SSL_CERT_DIR` 和包源配置继续生效。Kimi 的首次安装与更新统一使用 uv，移除依赖 ensurepip 版本的另一套安装路径。
2. **后台知识服务继承网络环境。** 在共享 `knowledge` 服务上下文中声明代理、CA、包源及 gh 配置路径变量，沿用现有一次性启动上下文。四个插件不各自维护网络状态机。安装配置只保存变量名，值由实际唤醒服务的进程提供。
3. **故障上报服务使用已有环境文件入口。** 启用服务时，自动将必要的代理、CA 和 gh 配置路径写入该服务目录下的私有环境文件；不复制 API Token。显式指定的环境文件优先。网络设置变化时更新现有服务，上传授权和已有回执保持原样。Kimi 的定时更新复用共享组件的同一环境文件实现，当前调用显式提供的变量优先。
4. **回环请求不经过企业代理。** knowledge 本机 RPC、Kimi 插件注册、DSH 摘要和 Bench 的 SSH、知识与重放 RPC 使用标准库 `ProxyHandler({})`，不依赖用户维护 `NO_PROXY`。
5. **外部写入保持现有结果语义。** 不重试结果不确定的 Git push、PR、Issue 或模型请求。证书错误保留原始失败；证书库来自操作系统或用户指定的 CA，不自动信任网络返回的证书。
6. **Bench 模型出口遵循企业 HTTP 代理。** 父进程网关读取 `HTTPS_PROXY` / `ALL_PROXY` 和 `NO_PROXY`，复用标准库 HTTP CONNECT 隧道与系统 TLS 校验；代理认证只发送给代理，不进入模型请求或日志。本机 HTTP relay 直接连接。保留原有流式传输、计量、超时与无自动重试语义。当前企业代理为 `http://` 类型；不支持的代理协议在发送模型请求前明确报错，不降级为直连。

变更只落在对应组件和插件仓；主仓维护本设计和入口文档。后台更新继续复用既有准备、空闲切换和超时预算。

## GitHub 登录引导

安装、首次配置或修复认证时，由 `/mindie-agent` 按下面的流程处理。登录选择属于 Agent 引导；凭据保存与使用复用 `gh`，不新增认证服务或 Token 配置格式。

1. **先复用已有认证。** 安装缺失的 `gh`，执行 `gh api --hostname github.com user --jq .login`。成功且账号符合当前配置时直接继续，不重复询问登录方式。`gh auth status` 用于诊断凭据来源；其他已保存账号失效不应阻止当前有效账号。
2. **需要登录时选择方式。** 用户已说明处于企业网络，或检测到代理/自定义 CA 配置、浏览器授权受阻时，优先推荐 Token；普通网络默认使用浏览器登录，也允许用户选择 Token。代理和 CA 仅是选择建议的依据，不代表浏览器一定不可用。连接超时、代理 407 和证书错误先按网络问题处理，不能冒充 Token 失效。
3. **选 Token 后只补齐缺失的一步。** 已有 Token 就直接使用；没有则打开 [GitHub Token 创建页](https://github.com/settings/tokens/new?scopes=repo%2Cread%3Aorg%2Cgist&description=MindIE%20Agent)，引导完成创建后回到终端。普通持久登录使用 `gh` 支持的 classic PAT（`repo`、`read:org`、`gist`）；有效期由用户或组织策略决定。组织要求 SSO 时完成对应授权。受组织策略约束的 fine-grained Token 按实际目标仓库配置权限，不要求用户换成不被允许的类型。
4. **用原生提示接收并保存。** 在用户可操作的终端运行 `gh auth login --hostname github.com --git-protocol https`，选择 `Paste an authentication token`，由用户在隐藏输入提示中粘贴。若用户已提供私有 Token 文件路径，Agent 直接通过标准输入执行 `gh auth login --hostname github.com --git-protocol https --with-token`，无需再次输入。Token 不进入对话、命令行参数、仓库、MindIE 配置或日志；保存由 `gh` 管理，不添加 `--insecure-storage`。环境中的旧 Token 会覆盖已保存登录，修复时需同时处理实际调用进程的旧变量。
5. **验证后继续原任务。** 再次读取账号，执行 `gh auth setup-git --hostname github.com`，并只读检查本次操作涉及的仓库。后续源码/知识同步、Git push、PR 和 Issue 操作复用同一 `gh` 身份；登录不改变已有贡献选择与项目范围。401 处理凭据失效，403/404 结合目标仓库、权限和 SSO 定位，不循环要求用户重登，也不创建测试 PR/Issue 来验证登录。

用户提供文件时，以下命令中的路径变量由 Agent 使用实际路径填入；文件内容不打印：

```powershell
Get-Content -Raw -LiteralPath $TokenFile | gh auth login --hostname github.com --git-protocol https --with-token
if ($LASTEXITCODE -ne 0) { throw "GitHub token login failed" }
```

```sh
gh auth login --hostname github.com --git-protocol https --with-token < "$TOKEN_FILE"
```

**后续复用范围：** `gh` 保存的登录可供同一用户、同一 `GH_CONFIG_DIR` 下的新进程使用。验证持久登录时，在不带 `GH_TOKEN` / `GITHUB_TOKEN` 的子进程中再次读取账号，避免环境变量掩盖未保存的登录；后台服务沿用已有网络环境与 `gh` 配置路径传递。若用户选择仅通过 `GH_TOKEN` 使用凭据（fine-grained PAT 优先采用此方式），由其现有凭据注入机制供应实际调用进程。知识服务已有一次性环境传递；诊断服务自动生成的网络文件不保存 Token，独立服务须使用已有的显式私有环境文件入口或 `gh` 保存的登录。仅当前终端成功不能报告为重启后的后台认证已就绪。

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
- 本地企业网络无法直连 A2/A3，属于已确认的环境边界。该环境不执行 A2/A3 实机测试，常规 CI 验证本地组件与进程、网络协议契约。

验证覆盖真实 Release 下载、私有环境文件的跨进程消费、既有服务启动上下文、带代理时的本机 HTTP 请求和失败传播。网络凭据不进入测试输出、公共日志或 PR 正文。
