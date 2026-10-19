#!/usr/bin/env python3
"""MindIE Agent org-wide GitHub telemetry collector and SVG/Markdown dashboard generator.

[Role]
Collects repository metadata (Stars, Forks), 14-day Git traffic (Clones, Views), and
permanent Release asset download counts across the @mindie-agent GitHub organization,
merges daily time-series into a cumulative JSON ledger, and renders bilingual SVG
dashboards (dashboard.zh.svg, dashboard.en.svg) plus a detailed Markdown report.

[Invariants]
- Daily traffic records in telemetry-history.json are keyed by ISO date (YYYY-MM-DD)
  and monotonically updated via max(existing, latest) so historical counts beyond
  GitHub's 14-day retention window are permanently preserved.
- Release package downloads exclude checksum/benchmark metadata files (*SHA256SUMS,
  benchmark-*) from the primary package counter while tracking total asset downloads.
- All XML/SVG text interpolations are strictly HTML-escaped to guarantee valid SVG 1.1.

[Timeouts & Locks]
- Each GitHub REST API request enforces a bounded 15-second HTTP timeout.
- Total script execution Across 15+ repositories completes within < 60 seconds.

[Side-Effect Policy]
- Read-only against GitHub REST APIs; writes output artifacts strictly into the
  caller-specified --output-dir without mutating the active git branch directly.
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone, timedelta
import html
import json
import os
from pathlib import Path
import urllib.error
import urllib.request

ORG = "mindie-agent"
HTTP_TIMEOUT_SECONDS = 15

# Core repositories displayed in the dashboard in architectural order.
CORE_REPOS: list[tuple[str, str, str, str, str]] = [
    # (repo, category_zh, category_en, role_zh, role_en)
    ("mindie-agent", "产品总入口", "Product Entry", "顶层架构、工程原则与发行记录", "Architecture, principles & release records"),
    ("awesome-mindie-skills", "社区生态", "Ecosystem", "昇腾 AI Infra 精选 Skills 目录", "Curated Ascend AI Infra Agent Skills"),
    ("mindie-agent-codex", "宿主插件", "Host Plugin", "OpenAI Codex CLI 原生插件", "OpenAI Codex CLI native plugin"),
    ("mindie-agent-cc", "宿主插件", "Host Plugin", "Claude Code 原生插件", "Claude Code native plugin"),
    ("mindie-agent-kimi", "宿主插件", "Host Plugin", "Kimi Code CLI 原生插件", "Kimi Code CLI native plugin"),
    ("mindie-agent-dsh", "宿主插件", "Host Plugin", "DeepSeek Harness (DSH) 插件", "DeepSeek Harness (DSH) adapter"),
    ("knowledge", "共享底座", "Core Runtime", "本地 BM25 检索与确定性脱敏引擎", "BM25 retrieval & deterministic redaction"),
    ("knowledge-vllm-ascend", "领域知识源", "Knowledge Feed", "vLLM-Ascend 与算子开发工程知识库", "vLLM-Ascend & operator knowledge corpus"),
    ("remote-dev", "共享底座", "Core Runtime", "19 个 SSH/容器远端开发孪生工具", "19 SSH/container remote dev tool twins"),
    ("coordinator", "共享底座", "Core Runtime", "远端昇腾环境、NPU 探测与租约管理", "Ascend fleet, NPU probe & lease manager"),
    ("npu-top", "可视化监控", "Observability", "昇腾 NPU Web 实时看板与 90 天热力图", "Ascend NPU live web UI & 90d heatmap"),
    ("diagnostics", "共享底座", "Core Runtime", "有界日志轮转与白名单故障诊断上报", "Bounded JSONL logs & issue reporting"),
    ("mindie-bench", "评测门禁", "Benchmark", "发布门禁与性能/生产力评测运行器", "Release gate & benchmark runner"),
]

PLUGIN_REPOS: list[tuple[str, str, str]] = [
    ("mindie-agent-codex", "OpenAI Codex CLI", "#10A37F"),
    ("mindie-agent-cc", "Claude Code", "#D97757"),
    ("mindie-agent-kimi", "Kimi Code CLI", "#2563EB"),
    ("mindie-agent-dsh", "DeepSeek Harness", "#0EA5E9"),
]


def github_get(path: str, token: str) -> object:
    url = f"https://api.github.com{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "mindie-agent-telemetry-dashboard",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT_SECONDS) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"GitHub API HTTP {exc.code} on {path}: {body}") from exc


def is_auxiliary_asset(name: str) -> bool:
    return name.endswith("SHA256SUMS") or name.startswith("benchmark-") or name == "product-release-provenance.json"


def load_history(history_path: Path) -> dict:
    if not history_path.is_file():
        return {"schema_version": 1, "org": ORG, "repositories": {}}
    return json.loads(history_path.read_text(encoding="utf-8"))


def merge_daily_series(
    existing_days: dict[str, dict[str, int]],
    api_items: list[dict],
) -> dict[str, dict[str, int]]:
    merged = dict(existing_days)
    for item in api_items:
        day = item["timestamp"][:10]
        count = int(item.get("count", 0))
        uniques = int(item.get("uniques", 0))
        prev = merged.get(day, {"count": 0, "uniques": 0})
        merged[day] = {
            "count": max(int(prev.get("count", 0)), count),
            "uniques": max(int(prev.get("uniques", 0)), uniques),
        }
    return dict(sorted(merged.items()))


def collect_org_telemetry(token: str, history: dict) -> tuple[dict, list[dict]]:
    repos_meta = history.setdefault("repositories", {})
    rows: list[dict] = []

    for repo, cat_zh, cat_en, role_zh, role_en in CORE_REPOS:
        info = github_get(f"/repos/{ORG}/{repo}", token)
        assert isinstance(info, dict)
        clones_data = github_get(f"/repos/{ORG}/{repo}/traffic/clones", token)
        assert isinstance(clones_data, dict)
        views_data = github_get(f"/repos/{ORG}/{repo}/traffic/views", token)
        assert isinstance(views_data, dict)
        releases = github_get(f"/repos/{ORG}/{repo}/releases?per_page=100", token)
        assert isinstance(releases, list)

        repo_hist = repos_meta.setdefault(repo, {"daily_clones": {}, "daily_views": {}})
        repo_hist["daily_clones"] = merge_daily_series(
            repo_hist.get("daily_clones", {}),
            clones_data.get("clones", []),
        )
        repo_hist["daily_views"] = merge_daily_series(
            repo_hist.get("daily_views", {}),
            views_data.get("views", []),
        )

        cum_clones = sum(d["count"] for d in repo_hist["daily_clones"].values())
        cum_clone_uniques = sum(d["uniques"] for d in repo_hist["daily_clones"].values())
        cum_views = sum(d["count"] for d in repo_hist["daily_views"].values())
        cum_view_uniques = sum(d["uniques"] for d in repo_hist["daily_views"].values())

        clones_14d = int(clones_data.get("count", 0))
        clones_14d_uniq = int(clones_data.get("uniques", 0))
        views_14d = int(views_data.get("count", 0))
        views_14d_uniq = int(views_data.get("uniques", 0))

        # Ensure cumulative totals are at least the 14-day window total
        cum_clones = max(cum_clones, clones_14d)
        cum_clone_uniques = max(cum_clone_uniques, clones_14d_uniq)
        cum_views = max(cum_views, views_14d)
        cum_view_uniques = max(cum_view_uniques, views_14d_uniq)

        pkg_dl = 0
        all_asset_dl = 0
        latest_tag = "-"
        if releases:
            latest_tag = str(releases[0].get("tag_name") or "-")
        for rel in releases:
            for asset in rel.get("assets", []):
                dc = int(asset.get("download_count", 0))
                all_asset_dl += dc
                if not is_auxiliary_asset(str(asset.get("name", ""))):
                    pkg_dl += dc

        stars = int(info.get("stargazers_count", 0))
        forks = int(info.get("forks_count", 0))
        repo_hist["latest_snapshot"] = {
            "stars": stars,
            "forks": forks,
            "clones_14d": clones_14d,
            "clones_14d_uniques": clones_14d_uniq,
            "cumulative_clones": cum_clones,
            "cumulative_clone_uniques": cum_clone_uniques,
            "views_14d": views_14d,
            "views_14d_uniques": views_14d_uniq,
            "cumulative_views": cum_views,
            "pkg_downloads": pkg_dl,
            "all_asset_downloads": all_asset_dl,
            "latest_release": latest_tag,
        }

        rows.append(
            {
                "repo": repo,
                "cat_zh": cat_zh,
                "cat_en": cat_en,
                "role_zh": role_zh,
                "role_en": role_en,
                "stars": stars,
                "forks": forks,
                "clones_14d": clones_14d,
                "clones_14d_uniq": clones_14d_uniq,
                "cum_clones": cum_clones,
                "cum_clone_uniq": cum_clone_uniques,
                "views_14d": views_14d,
                "views_14d_uniq": views_14d_uniq,
                "cum_views": cum_views,
                "pkg_dl": pkg_dl,
                "all_asset_dl": all_asset_dl,
                "latest_tag": latest_tag,
            }
        )

    return history, rows


def fmt_num(n: int) -> str:
    return f"{n:,}"


def render_svg(rows: list[dict], updated_at_cst: str, lang: str) -> str:
    is_zh = lang == "zh"
    by_repo = {r["repo"]: r for r in rows}
    main_row = by_repo["mindie-agent"]

    total_stars = sum(r["stars"] for r in rows)
    total_forks = sum(r["forks"] for r in rows)
    total_14d_clones = sum(r["clones_14d"] for r in rows)
    total_cum_clones = sum(r["cum_clones"] for r in rows)
    total_pkg_dl = sum(r["pkg_dl"] for r in rows)
    total_all_dl = sum(r["all_asset_dl"] for r in rows)

    plugin_14d_clones = sum(by_repo[p[0]]["clones_14d"] for p in PLUGIN_REPOS)
    plugin_cum_clones = sum(by_repo[p[0]]["cum_clones"] for p in PLUGIN_REPOS)
    plugin_14d_uniq = sum(by_repo[p[0]]["clones_14d_uniq"] for p in PLUGIN_REPOS)

    title = (
        "MindIE Agent 社区生态与使用统计看板"
        if is_zh
        else "MindIE Agent Ecosystem & Telemetry Dashboard"
    )
    subtitle = (
        f"GitHub 官方 API 自动汇总 · 每 12 小时刷新 · 最近更新：{updated_at_cst} (UTC+8)"
        if is_zh
        else f"Auto-aggregated via GitHub REST API · Refreshed every 12h · Last synced: {updated_at_cst} (UTC+8)"
    )

    kpis = [
        (
            "主仓 Star / Fork (安装触达)" if is_zh else "Main Repo Stars / Forks",
            f"{fmt_num(main_row['stars'])} ★  ·  {fmt_num(main_row['forks'])} ⑂",
            f"全组织累计 {fmt_num(total_stars)} Stars · {fmt_num(total_forks)} Forks"
            if is_zh
            else f"Org total: {fmt_num(total_stars)} Stars · {fmt_num(total_forks)} Forks",
            "#7045F5",
        ),
        (
            "四大宿主插件 Clone 量" if is_zh else "Host Plugin Clones",
            f"{fmt_num(plugin_cum_clones)}" + (" 次" if is_zh else ""),
            f"近 14 天 {fmt_num(plugin_14d_clones)} 次 ({fmt_num(plugin_14d_uniq)} 独立 IP)"
            if is_zh
            else f"14d: {fmt_num(plugin_14d_clones)} clones ({fmt_num(plugin_14d_uniq)} unique)",
            "#10A37F",
        ),
        (
            "全组织 Git Clone 总量" if is_zh else "Org-Wide Git Clones",
            f"{fmt_num(total_cum_clones)}" + (" 次" if is_zh else ""),
            f"近 14 天 {fmt_num(total_14d_clones)} 次 · 覆盖 {len(rows)} 个核心仓"
            if is_zh
            else f"14d: {fmt_num(total_14d_clones)} clones across {len(rows)} core repos",
            "#2563EB",
        ),
        (
            "Release 产物累计下载" if is_zh else "Release Package Downloads",
            f"{fmt_num(total_pkg_dl)}" + (" 次" if is_zh else ""),
            f"含校验/评测附件共 {fmt_num(total_all_dl)} 次永久下载"
            if is_zh
            else f"{fmt_num(total_all_dl)} total asset downloads (all-time)",
            "#0F766E",
        ),
    ]

    width = 960
    row_height = 32
    table_top = 340
    table_height = 42 + len(rows) * row_height
    height = table_top + table_height + 46

    lines: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" fill="none">',
        "  <style>",
        "    .font { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', Helvetica, Arial, sans-serif; }",
        "    .mono { font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace; }",
        "    .title { font-size: 18px; font-weight: 700; fill: #0F172A; }",
        "    .subtitle { font-size: 12px; font-weight: 400; fill: #64748B; }",
        "    .kpi-label { font-size: 12px; font-weight: 600; fill: #475569; }",
        "    .kpi-val { font-size: 22px; font-weight: 700; fill: #0F172A; }",
        "    .kpi-sub { font-size: 11px; font-weight: 400; fill: #64748B; }",
        "    .sec-title { font-size: 13px; font-weight: 700; fill: #1E293B; }",
        "    .th { font-size: 11.5px; font-weight: 700; fill: #475569; }",
        "    .td-repo { font-size: 12px; font-weight: 600; fill: #0F172A; }",
        "    .td-cat { font-size: 11px; font-weight: 500; fill: #475569; }",
        "    .td-num { font-size: 12px; font-weight: 500; fill: #1E293B; }",
        "    .td-sub { font-size: 11px; font-weight: 400; fill: #64748B; }",
        "    .footer { font-size: 11px; fill: #64748B; }",
        "  </style>",
        f'  <rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="12" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1.5"/>',
        f'  <rect x="1" y="1" width="{width - 2}" height="68" rx="12" fill="#F8FAFC"/>',
        f'  <line x1="1" y1="69" x2="{width - 1}" y2="69" stroke="#E2E8F0" stroke-width="1"/>',
        f'  <text x="24" y="34" class="font title">{html.escape(title)}</text>',
        f'  <text x="24" y="54" class="font subtitle">{html.escape(subtitle)}</text>',
    ]

    # Render 4 KPI Cards
    card_w = 216
    card_gap = 16
    for idx, (label, val, sub, accent) in enumerate(kpis):
        cx = 24 + idx * (card_w + card_gap)
        cy = 84
        lines.extend(
            [
                f'  <rect x="{cx}" y="{cy}" width="{card_w}" height="88" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1"/>',
                f'  <rect x="{cx}" y="{cy}" width="4" height="88" rx="2" fill="{accent}"/>',
                f'  <text x="{cx + 14}" y="{cy + 24}" class="font kpi-label">{html.escape(label)}</text>',
                f'  <text x="{cx + 14}" y="{cy + 54}" class="font kpi-val">{html.escape(val)}</text>',
                f'  <text x="{cx + 14}" y="{cy + 74}" class="font kpi-sub">{html.escape(sub)}</text>',
            ]
        )

    # Render Client Plugin Share Bar Section
    bar_sec_y = 192
    sec_label = (
        "🔌 四大宿主客户端插件安装与 Clone 分布（累计 / 近 14 天独立 IP）"
        if is_zh
        else "🔌 Host Client Plugin Clone Distribution (Cumulative / 14d Unique IPs)"
    )
    lines.extend(
        [
            f'  <rect x="24" y="{bar_sec_y}" width="{width - 48}" height="130" rx="8" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1"/>',
            f'  <text x="40" y="{bar_sec_y + 24}" class="font sec-title">{html.escape(sec_label)}</text>',
        ]
    )

    # Stacked horizontal bar
    stack_x = 40
    stack_y = bar_sec_y + 36
    stack_w = width - 80
    stack_h = 14
    lines.append(f'  <rect x="{stack_x}" y="{stack_y}" width="{stack_w}" height="{stack_h}" rx="7" fill="#E2E8F0"/>')

    cur_x = float(stack_x)
    denom = max(plugin_cum_clones, 1)
    for repo_name, _, color in PLUGIN_REPOS:
        c_val = by_repo[repo_name]["cum_clones"]
        seg_w = (c_val / denom) * stack_w
        if seg_w > 0:
            lines.append(
                f'  <rect x="{cur_x:.1f}" y="{stack_y}" width="{max(seg_w, 4.0):.1f}" height="{stack_h}" rx="3" fill="{color}"/>'
            )
            cur_x += seg_w

    # 4 legend boxes below stacked bar
    leg_w = (width - 80) // 4
    for idx, (repo_name, host_name, color) in enumerate(PLUGIN_REPOS):
        r_data = by_repo[repo_name]
        lx = 40 + idx * leg_w
        ly = bar_sec_y + 70
        pct = (r_data["cum_clones"] / denom) * 100.0
        stat_line = (
            f"累计 {fmt_num(r_data['cum_clones'])} ({pct:.1f}%) · 14d 独立 {fmt_num(r_data['clones_14d_uniq'])}"
            if is_zh
            else f"Total {fmt_num(r_data['cum_clones'])} ({pct:.1f}%) · 14d uniq {fmt_num(r_data['clones_14d_uniq'])}"
        )
        lines.extend(
            [
                f'  <circle cx="{lx + 6}" cy="{ly}" r="5" fill="{color}"/>',
                f'  <text x="{lx + 16}" y="{ly + 4}" class="font td-repo">{html.escape(host_name)}</text>',
                f'  <text x="{lx + 16}" y="{ly + 22}" class="mono td-sub">{html.escape(repo_name)}</text>',
                f'  <text x="{lx + 16}" y="{ly + 38}" class="font td-sub">{html.escape(stat_line)}</text>',
            ]
        )

    # Render Repository Breakdown Table
    lines.extend(
        [
            f'  <rect x="24" y="{table_top}" width="{width - 48}" height="{table_height}" rx="8" fill="#FFFFFF" stroke="#E2E8F0" stroke-width="1"/>',
            f'  <rect x="24" y="{table_top}" width="{width - 48}" height="38" rx="8" fill="#F1F5F9"/>',
            f'  <line x1="24" y1="{table_top + 38}" x2="{width - 24}" y2="{table_top + 38}" stroke="#CBD5E1" stroke-width="1"/>',
        ]
    )

    col_repo = 40
    col_cat = 225
    col_ver = 330
    col_sf = 460
    col_c14 = 605
    col_ccum = 730
    col_v14 = 830
    col_dl = 920

    headers = (
        [
            (col_repo, "start", "仓库 (Repository)"),
            (col_cat, "start", "定位分类"),
            (col_ver, "start", "最新 Release"),
            (col_sf, "end", "Star / Fork"),
            (col_c14, "end", "近14天 Clone (独立)"),
            (col_ccum, "end", "累计 Clone"),
            (col_v14, "end", "近14天浏览 (独立)"),
            (col_dl, "end", "Release 下载"),
        ]
        if is_zh
        else [
            (col_repo, "start", "Repository"),
            (col_cat, "start", "Category"),
            (col_ver, "start", "Latest Release"),
            (col_sf, "end", "Star / Fork"),
            (col_c14, "end", "14d Clones (Uniq)"),
            (col_ccum, "end", "Total Clones"),
            (col_v14, "end", "14d Views (Uniq)"),
            (col_dl, "end", "Release DL"),
        ]
    )

    for cx, anchor, h_text in headers:
        lines.append(
            f'  <text x="{cx}" y="{table_top + 24}" text-anchor="{anchor}" class="font th">{html.escape(h_text)}</text>'
        )

    for idx, r in enumerate(rows):
        ry = table_top + 38 + idx * row_height
        if idx % 2 == 1:
            lines.append(
                f'  <rect x="25" y="{ry}" width="{width - 50}" height="{row_height}" fill="#F8FAFC"/>'
            )
        if idx > 0:
            lines.append(
                f'  <line x1="24" y1="{ry}" x2="{width - 24}" y2="{ry}" stroke="#F1F5F9" stroke-width="1"/>'
            )

        ty = ry + 21
        cat = r["cat_zh"] if is_zh else r["cat_en"]
        tag_disp = r["latest_tag"]
        if len(tag_disp) > 16:
            tag_disp = tag_disp[:15] + "…"
        sf_str = f"{r['stars']} / {r['forks']}"
        c14_str = f"{fmt_num(r['clones_14d'])} ({fmt_num(r['clones_14d_uniq'])})"
        ccum_str = fmt_num(r["cum_clones"])
        v14_str = f"{fmt_num(r['views_14d'])} ({fmt_num(r['views_14d_uniq'])})"
        dl_str = fmt_num(r["pkg_dl"]) if r["pkg_dl"] > 0 else "-"

        lines.extend(
            [
                f'  <text x="{col_repo}" y="{ty}" class="mono td-repo">{html.escape(r["repo"])}</text>',
                f'  <text x="{col_cat}" y="{ty}" class="font td-cat">{html.escape(cat)}</text>',
                f'  <text x="{col_ver}" y="{ty}" class="mono td-sub">{html.escape(tag_disp)}</text>',
                f'  <text x="{col_sf}" y="{ty}" text-anchor="end" class="mono td-num">{html.escape(sf_str)}</text>',
                f'  <text x="{col_c14}" y="{ty}" text-anchor="end" class="mono td-num">{html.escape(c14_str)}</text>',
                f'  <text x="{col_ccum}" y="{ty}" text-anchor="end" class="mono td-num">{html.escape(ccum_str)}</text>',
                f'  <text x="{col_v14}" y="{ty}" text-anchor="end" class="mono td-sub">{html.escape(v14_str)}</text>',
                f'  <text x="{col_dl}" y="{ty}" text-anchor="end" class="mono td-num">{html.escape(dl_str)}</text>',
            ]
        )

    footer_y = table_top + table_height + 26
    footer_note = (
        "注：安装协议默认通过 gh 执行 Star & Fork (--clone=false)，主仓 Star/Fork 代表独立安装用户基数；底层组件 Clone 含插件环境初始化与 CI 验证流量。"
        if is_zh
        else "Note: Standard installation stars & forks mindie-agent (--clone=false); runtime component clones include plugin bootstrap & CI verification."
    )
    lines.append(f'  <text x="24" y="{footer_y}" class="font footer">{html.escape(footer_note)}</text>')
    lines.append("</svg>\n")
    return "\n".join(lines)


def render_markdown_report(rows: list[dict], updated_at_cst: str) -> str:
    total_stars = sum(r["stars"] for r in rows)
    total_forks = sum(r["forks"] for r in rows)
    total_14d_clones = sum(r["clones_14d"] for r in rows)
    total_cum_clones = sum(r["cum_clones"] for r in rows)
    total_pkg_dl = sum(r["pkg_dl"] for r in rows)
    total_all_dl = sum(r["all_asset_dl"] for r in rows)

    md = [
        "# 📊 MindIE Agent 社区生态与使用统计报表 (Telemetry Archive)",
        "",
        f"> **最近更新时间**：`{updated_at_cst} (UTC+8)` · 由 GitHub Actions 每 12 小时自动拉取并归档至 `telemetry-data` 分支。",
        "",
        "![MindIE Agent Telemetry Dashboard](./dashboard.zh.svg)",
        "",
        "## 核心仓库实时明细（可点击跳转）",
        "",
        "| 分类 | 仓库 | 最新 Release | Stars | Forks | 近 14 天 Clone (独立) | 历史累计 Clone | 近 14 天浏览 (独立) | Release 产物下载 (全附件) |",
        "| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for r in rows:
        repo_link = f"[`{r['repo']}`](https://github.com/{ORG}/{r['repo']})"
        md.append(
            f"| {r['cat_zh']} | {repo_link} | `{r['latest_tag']}` | {r['stars']} | {r['forks']} "
            f"| {fmt_num(r['clones_14d'])} ({fmt_num(r['clones_14d_uniq'])}) "
            f"| **{fmt_num(r['cum_clones'])}** "
            f"| {fmt_num(r['views_14d'])} ({fmt_num(r['views_14d_uniq'])}) "
            f"| {fmt_num(r['pkg_dl'])} ({fmt_num(r['all_asset_dl'])}) |"
        )
    md.append(
        f"| **合计** | **全组织 {len(rows)} 个核心仓** | — | **{fmt_num(total_stars)}** | **{fmt_num(total_forks)}** "
        f"| **{fmt_num(total_14d_clones)}** | **{fmt_num(total_cum_clones)}** | — | **{fmt_num(total_pkg_dl)}** ({fmt_num(total_all_dl)}) |"
    )
    md.extend(
        [
            "",
            "## 数据文件说明",
            "",
            "- [`dashboard.zh.svg`](./dashboard.zh.svg)：中文首页动态统计看板 SVG",
            "- [`dashboard.en.svg`](./dashboard.en.svg)：英文首页动态统计看板 SVG",
            "- [`telemetry-history.json`](./telemetry-history.json)：按天（`YYYY-MM-DD`）去重累加的历史 Clone 与浏览时间序列账本（突破 GitHub 14 天清除限制）",
            "",
        ]
    )
    return "\n".join(md)


def main() -> None:
    parser = argparse.ArgumentParser(description="Update MindIE Agent telemetry dashboard artifacts.")
    parser.add_argument("--output-dir", required=True, help="Directory containing telemetry-history.json and SVG outputs.")
    args = parser.parse_args()

    token = os.environ.get("TELEMETRY_TOKEN") or os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        raise RuntimeError("Missing TELEMETRY_TOKEN / GH_TOKEN / GITHUB_TOKEN in environment.")

    out_dir = Path(args.output_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    history_path = out_dir / "telemetry-history.json"

    cst_tz = timezone(timedelta(hours=8))
    updated_at_cst = datetime.now(cst_tz).strftime("%Y-%m-%d %H:%M")

    history = load_history(history_path)
    history["updated_at_cst"] = updated_at_cst
    history, rows = collect_org_telemetry(token, history)

    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "dashboard.zh.svg").write_text(render_svg(rows, updated_at_cst, "zh"), encoding="utf-8")
    (out_dir / "dashboard.en.svg").write_text(render_svg(rows, updated_at_cst, "en"), encoding="utf-8")
    (out_dir / "README.md").write_text(render_markdown_report(rows, updated_at_cst), encoding="utf-8")
    print(f"Successfully generated telemetry artifacts in {out_dir} at {updated_at_cst} (UTC+8)")


if __name__ == "__main__":
    main()
