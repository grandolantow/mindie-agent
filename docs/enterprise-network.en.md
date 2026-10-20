# Configuration and transport on enterprise networks

[中文](enterprise-network.md) · [Documentation](README.en.md)

## Routes and owners

| Route | Owner | Network configuration |
| --- | --- | --- |
| Plugin registration, source and knowledge Feed fetches | Native plugin managers and Git | Caller proxy, Git configuration and system certificates |
| Python, component wheels and PyPI packages | uv invoked by plugin installers and updaters | Caller proxy, system trust, explicit CA and package indexes |
| Gitleaks and DSH Release downloads | Python standard-library HTTPS | System trust, explicit CA and caller proxy |
| Knowledge PRs and diagnostic Issues | Git and gh | Existing consent, gh login and service launch environment |
| Knowledge RPC, Kimi plugin API and DSH summary API | Shared knowledge client and Python adapters | Direct loopback connection |
| Bench model egress and local RPC | mindie-bench gateway and shims | Proxy and `NO_PROXY` for model egress; direct local RPC |
| SSH uploads, downloads and artifact synchronization | remote-dev | SSH configuration and selected host/container |
| Resource coordination and NPU observation | coordinator and npu-top | SSH and local APIs; remote Docker owns image-download networking |

## Design

Following [design principles](design-principles.en.md) 1, 8, 9, 10, 14 and 15:

1. Enable system trust in native launch commands before uv downloads Python. Internal installers use the environment default supported by older uv versions and retain explicit `UV_SYSTEM_CERTS` and `UV_NATIVE_TLS` choices. Custom `SSL_CERT_FILE`, `SSL_CERT_DIR` and indexes remain effective. Kimi uses uv for both initial setup and updates instead of maintaining a separate ensurepip-dependent installer.
2. Declare proxy, CA, package-index and gh configuration variables in the shared knowledge service context. Reuse the existing one-use context transfer. Installation configuration stores names; the process waking the service supplies values.
3. Reuse the diagnostic service's environment-file mechanism. Automatically write selected proxy, CA and gh configuration paths into its private service directory, without copying API tokens. An explicitly configured file takes precedence. Refresh network settings while preserving consent and publication receipts. Kimi scheduled updates reuse this shared implementation, with explicit current caller values taking precedence.
4. Use `ProxyHandler({})` for knowledge's own RPC client, Kimi registration, DSH summaries, and Bench SSH, knowledge and replay RPC. Local operations must work without a caller-maintained `NO_PROXY`.
5. Preserve publication outcomes. Never replay uncertain Git pushes, PRs, Issues or model calls. Retain certificate errors and use system or explicitly configured trust; never trust a certificate merely because a peer returned it.
6. Route Bench model egress using the parent process's `HTTPS_PROXY` / `ALL_PROXY` and `NO_PROXY`. Reuse standard-library HTTP CONNECT and system TLS verification. Send proxy credentials only to the proxy, never to the provider or journal. Connect directly to local HTTP relays. Preserve streaming, metering, timeouts and no automatic retries. The current enterprise proxy uses `http://`; reject unsupported proxy protocols before model submission instead of silently connecting directly.

Runtime changes belong to their component and plugin repositories. This repository owns the design and entry documentation. Updates retain existing preparation, idle switching and timeout budgets.

## Enterprise-network observations

On October 20, 2026, using an authenticated HTTP proxy on Windows:

- GitHub API, source clones, Release asset redirects and PyPI were reachable.
- Git clones of the code repositories and both knowledge domains succeeded with certificate verification enabled.
- The GitHub Release wheel for `mindie-diagnostics 0.4.3` failed under uv's default trust with `invalid peer certificate: UnknownIssuer`. The same request succeeded with system certificates.
- PyPI succeeded in the same environment, so a PyPI-only probe would miss the installation failure.
- With system trust, Python 3.13.16 and a component Release wheel downloaded successfully, followed by a complete Codex locked runtime installation (166 packages).
- This machine had `http.sslVerify=false`. After confirming that verification works with its existing enterprise proxy, the setting was restored to `true`; GitHub access with the default Git configuration passed.
- Git pushes and GitHub PR creation for the fixes succeeded, exercising actual upload paths.
- Real local HTTP/TLS tests covered authenticated CONNECT, explicit CA trust, `NO_PROXY`, streaming usage and loopback requests with a broken proxy.
- TCP port 22 probes timed out for A2 `173.125.1.2` and A3 `192.168.13.165`, `.156` and `.154`. SSH file transfers to these hosts have not completed live validation on this network.

Verification covers real Release downloads, environment-file consumption across processes, existing service context transfer, proxied loopback requests and error propagation. Network credentials stay out of test output, public logs and PR descriptions.
