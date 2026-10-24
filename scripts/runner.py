#!/usr/bin/env python3
"""自动化编排与派工辅助工具。

提供三项实用能力：
1. plan: 解析指定编排（playbook），生成填充了角色依赖与并行组的运行计划；
2. suggest: 根据代码或文件变更路径，智能推荐需派发的岗位清单；
3. triage: 汇总指定目录下的各岗位报告，提取 P0-P3 发现并生成结构化分诊单。
"""
import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# 路径按 / . _ - 与驼峰切成小写词后整词匹配；扩展名、文件名单独匹配。
SUGGESTION_RULES = [
    {
        "words": {"auth", "login", "token", "guard", "permission", "permissions", "rbac", "session", "jwt", "oauth"},
        "roles": ["security-reviewer", "qa-permission-tester"],
        "reason": "涉及身份鉴权与权限校验，需要重点防范水平/垂直越权与凭证泄露",
    },
    {
        "words": {"price", "pricing", "billing", "invoice", "subscription", "order", "orders", "payment", "checkout"},
        "roles": ["finance-pricing", "risk-control-reviewer", "legal-counsel"],
        "reason": "涉及计费模型、订单与付费档位，需要核算毛利边界、防范套利并厘清权责",
    },
    {
        "words": {"point", "points", "reward", "rewards", "invite", "coupon", "promotion", "activity"},
        "roles": ["risk-control-reviewer", "security-reviewer"],
        "reason": "涉及积分、奖励与邀请裂变，需要重点审查上限配额、并发穿透与幂等性",
    },
    {
        "words": {"schema", "migration", "migrations", "entity", "entities", "model", "models", "database", "sql"},
        "roles": ["architect-reviewer", "security-reviewer"],
        "reason": "涉及数据模型与数据库变更，需要评估租户隔离、索引性能与锁表回滚风险",
    },
    {
        "words": {"ui", "component", "components", "view", "views", "page", "pages"},
        "exts": {"vue", "jsx", "tsx", "wxml"},
        "roles": ["interaction-designer", "visual-design-reviewer", "ux-writer"],
        "reason": "涉及前端界面与交互布局，需走查异常空态、文案可行动性及多主题对比度",
    },
    {
        "words": {"style", "styles", "theme", "themes"},
        "exts": {"css", "scss", "less", "wxss"},
        # 样式文件只派视觉岗位，不因所在目录（如 pages/）再派其他岗位。
        "only_by_ext": True,
        "roles": ["visual-design-reviewer"],
        "reason": "只涉及样式与主题，需核对层级、间距、配色与各主题下的对比度",
    },
    {
        "words": {"manual", "doc", "docs", "faq", "handbook", "readme"},
        "roles": ["ux-writer", "support-desk", "qa-cross-platform"],
        "reason": "涉及文档与指引更新，需核对后台/小程序实操步骤与文案术语的一致性",
    },
    {
        "words": {"docker", "dockerfile", "k8s", "deploy", "ci", "cd", "release", "nginx", "workflows"},
        "roles": ["release-sre"],
        "reason": "涉及部署与环境配置，需要核实备份恢复验证、容量水位与回滚措施",
    },
    {
        "names": {"app.json", "project.config.json"},
        "exts": {"wxml", "wxs"},
        "roles": ["qa-cross-platform", "qa-performance"],
        "reason": "涉及小程序页面与配置，需核对小程序与 Web 端一致性及包体、首屏表现",
    },
]


def path_words(path):
    """把路径切成小写词集合（按分隔符和驼峰）。"""
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", path.replace("\\", "/"))
    return {w for w in re.split(r"[^A-Za-z0-9]+", spaced.lower()) if w}


def role_names(root=None):
    base = Path(root or REPO_ROOT) / "roles"
    return sorted(p.stem for p in base.glob("*/*.md") if not p.name.startswith("_"))


def playbook_names(root=None):
    base = Path(root or REPO_ROOT) / "playbooks"
    return sorted(p.stem for p in base.glob("*.md"))


def load_playbook(playbook_path):
    p = Path(playbook_path)
    if not p.is_file():
        raise FileNotFoundError(f"未找到编排文件: {playbook_path}")
    text = p.read_text(encoding="utf-8")
    title_match = re.search(r"^#\s+(.+)$", text, flags=re.M)
    title = title_match.group(1).strip() if title_match else p.stem

    sections = {}
    current_sec = None
    buf = []
    for line in text.splitlines():
        sec_m = re.match(r"^##\s+(.+)$", line)
        if sec_m:
            if current_sec:
                sections[current_sec] = "\n".join(buf).strip()
            current_sec = sec_m.group(1).strip()
            buf = []
        elif current_sec:
            buf.append(line)
    if current_sec:
        sections[current_sec] = "\n".join(buf).strip()

    roles = re.findall(r"`([a-z][a-z0-9]*(?:-[a-z0-9]+)+)`", text)
    unique_roles = []
    for r in roles:
        if r not in unique_roles:
            unique_roles.append(r)
    return {
        "title": title,
        "sections": sections,
        "roles": unique_roles,
        "raw": text,
    }


def _table_cells(line):
    parts = re.split(r"(?<!\\)\|", line.strip())
    return [c.strip().replace("\\|", "|") for c in parts[1:-1]]


def latest_triage(reports_dir):
    """返回目录里最新的 triage-YYYYMMDD[-n].md，没有则返回 None。"""
    rep = Path(reports_dir)
    if not rep.is_dir():
        return None
    best = None
    for f in rep.glob("triage-*.md"):
        m = re.fullmatch(r"triage-(\d{8})(?:-(\d+))?\.md", f.name)
        if m:
            key = (m.group(1), int(m.group(2) or 1))
            if best is None or key > best[0]:
                best = (key, f)
    return best[1] if best else None


def previous_open_items(reports_dir):
    """从最新分诊单里取出 P0/P1 与缺级别的表格行。"""
    f = latest_triage(reports_dir)
    if f is None:
        return None, []
    rows = []
    in_section = False
    for line in f.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            in_section = line.startswith("## 重点分诊项") or line.startswith("## 缺级别")
            continue
        if in_section and line.startswith("|"):
            cells = _table_cells(line)
            if not cells or cells[0] in ("级别", "---") or set(cells[0]) <= set("- "):
                continue
            rows.append(cells)
    return f, rows


def generate_run_plan(playbook_path, root_dir=None, reports_dir=None):
    pb = load_playbook(playbook_path)
    lines = [
        f"# 运行计划：{pb['title']}",
        "",
        "- 编排文件：" + Path(playbook_path).name,
        "- 涉及岗位数：" + str(len(pb["roles"])),
        "",
    ]
    if reports_dir is not None:
        f, rows = previous_open_items(reports_dir)
        lines.append("## 上次 P0/P1，开工前逐条核对是否已关闭")
        lines.append("")
        if f is None:
            lines.append("无上次分诊单。")
        elif not rows:
            lines.append(f"上次分诊单 {f.name} 中没有 P0 / P1 与缺级别项。")
        else:
            lines.append(f"来源：{f.name}")
            lines.append("")
            for cells in rows:
                lines.append("- [ ] " + " ｜ ".join(c for c in cells if c))
        lines.append("")
    lines += ["## 岗位执行序列", ""]
    for idx, r in enumerate(pb["roles"], 1):
        lines.append(f"{idx}. `{r}`")
    lines.append("")

    if "岗位与顺序" in pb["sections"]:
        lines.append("## 顺序说明")
        lines.append("")
        lines.append(pb["sections"]["岗位与顺序"])
        lines.append("")

    if "可并行" in pb["sections"]:
        lines.append("## 可并行组")
        lines.append("")
        lines.append(pb["sections"]["可并行"])
        lines.append("")

    if "收尾标准" in pb["sections"]:
        lines.append("## 收尾验收标准")
        lines.append("")
        lines.append(pb["sections"]["收尾标准"])
        lines.append("")

    return "\n".join(lines)


def suggest_roles(files):
    hits = {}
    matched_reasons = {}
    for f in files:
        f_norm = f.replace("\\", "/")
        words = path_words(f_norm)
        base = f_norm.rsplit("/", 1)[-1].lower()
        ext = base.rsplit(".", 1)[-1] if "." in base else ""
        exclusive = [r for r in SUGGESTION_RULES if r.get("only_by_ext") and ext in r.get("exts", set())]
        for rule in exclusive or SUGGESTION_RULES:
            if (words & rule.get("words", set())
                    or base in rule.get("names", set())
                    or ext in rule.get("exts", set())):
                for role in rule["roles"]:
                    hits.setdefault(role, []).append(f)
                    matched_reasons[role] = rule["reason"]

    results = []
    for role, matched_files in sorted(hits.items()):
        results.append({
            "role": role,
            "reason": matched_reasons[role],
            "matched_files": sorted(set(matched_files)),
        })
    return results


def _single_level(value):
    levels = set(re.findall(r"P[0-3]", value))
    return levels.pop() if len(levels) == 1 else None


def parse_report_findings(report_text):
    findings = []
    current_finding = None

    for line in report_text.splitlines():
        f_match = re.match(r"^###\s+([A-Za-z0-9_.-]+)\s+(.+)$", line)
        if f_match:
            if current_finding:
                findings.append(current_finding)
            current_finding = {
                "id": f_match.group(1).strip(),
                "title": f_match.group(2).strip(),
                "level": None,
                "evidence": "",
                "suggestion": "",
                "action": "",
            }
            continue

        if current_finding:
            lvl_m = re.match(r"^-\s*级别[：:]\s*(.*)$", line)
            if lvl_m:
                current_finding["level"] = _single_level(lvl_m.group(1))
            evi_m = re.match(r"^-\s*证据[：:]\s*(.+)$", line)
            if evi_m:
                current_finding["evidence"] = evi_m.group(1).strip()
            act_m = re.match(r"^-\s*建议去向[：:]\s*(.+)$", line)
            if act_m:
                current_finding["action"] = act_m.group(1).strip()
            else:
                sug_m = re.match(r"^-\s*建议[：:]\s*(.+)$", line)
                if sug_m:
                    current_finding["suggestion"] = sug_m.group(1).strip()

    if current_finding:
        findings.append(current_finding)
    return findings


def match_role(stem, names):
    """用角色名做最长前缀匹配，匹配不到返回 None。"""
    best = None
    for n in names:
        if stem.startswith(n) and (len(stem) == len(n) or not stem[len(n)].isalpha()):
            if best is None or len(n) > len(best):
                best = n
    return best


def _cell(text):
    return re.sub(r"\s+", " ", str(text)).replace("|", "\\|").strip()


def generate_triage(reports_dir, roles_root=None):
    rep_dir = Path(reports_dir)
    if not rep_dir.is_dir():
        raise NotADirectoryError(f"未找到报告目录: {reports_dir}")

    names = role_names(roles_root)
    all_findings = []
    report_files = sorted(f for f in rep_dir.glob("*.md") if not f.name.startswith("triage-"))
    unknown_files = []

    for rf in report_files:
        role_name = match_role(rf.stem, names)
        if role_name is None:
            role_name = "未识别"
            unknown_files.append(rf.name)
        text = rf.read_text(encoding="utf-8")
        for item in parse_report_findings(text):
            item["source_file"] = rf.name
            item["role"] = role_name
            all_findings.append(item)

    counts = {"P0": 0, "P1": 0, "P2": 0, "P3": 0}
    missing = [f for f in all_findings if f["level"] is None]
    for it in all_findings:
        if it["level"] is not None:
            counts[it["level"]] += 1

    lines = [
        "# 多岗位分诊汇总单",
        "",
        f"- 扫描报告数：{len(report_files)}",
        f"- 发现总数：{len(all_findings)} 条（P0: {counts['P0']}，P1: {counts['P1']}，P2: {counts['P2']}，P3: {counts['P3']}，缺级别: {len(missing)}）",
    ]
    if unknown_files:
        lines.append("- 未识别岗位的报告：" + "、".join(unknown_files))
    lines.append("")

    blockers = counts["P0"] + len(missing)
    if blockers > 0:
        lines.append("> [!CAUTION]")
        lines.append(f"> 触发阻断：存在 {counts['P0']} 条 P0 级严重隐患、{len(missing)} 条缺级别发现（按 P0 对待），建议立即终止发布流程并排查。")
        lines.append("")

    lines.append("## 重点分诊项（P0 / P1）")
    lines.append("")
    critical = [f for f in all_findings if f["level"] in ("P0", "P1")]
    if not critical:
        lines.append("未发现 P0 / P1 级严重问题。")
    else:
        lines.append("| 级别 | 编号 | 来源岗位 | 标题 | 建议 | 建议去向 | 证据 |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- |")
        for it in sorted(critical, key=lambda x: x["level"]):
            evi = (it["evidence"][:30] + "...") if len(it["evidence"]) > 30 else it["evidence"]
            lines.append(f"| {it['level']} | {_cell(it['id'])} | `{it['role']}` | {_cell(it['title'])} | {_cell(it['suggestion'])} | {_cell(it['action'])} | {_cell(evi)} |")
    lines.append("")

    lines.append("## 缺级别（按 P0 对待，需补级别）")
    lines.append("")
    if not missing:
        lines.append("无缺级别发现。")
    else:
        lines.append("| 级别 | 编号 | 来源岗位 | 标题 | 来源文件 |")
        lines.append("| --- | --- | --- | --- | --- |")
        for it in missing:
            lines.append(f"| 缺级别 | {_cell(it['id'])} | `{it['role']}` | {_cell(it['title'])} | {_cell(it['source_file'])} |")
    lines.append("")

    lines.append("## 一般与打磨项（P2 / P3）")
    lines.append("")
    normal = [f for f in all_findings if f["level"] in ("P2", "P3")]
    if not normal:
        lines.append("无一般问题记录。")
    else:
        lines.append("| 级别 | 编号 | 来源岗位 | 标题 | 建议 | 建议去向 |")
        lines.append("| --- | --- | --- | --- | --- | --- |")
        for it in sorted(normal, key=lambda x: x["level"]):
            lines.append(f"| {it['level']} | {_cell(it['id'])} | `{it['role']}` | {_cell(it['title'])} | {_cell(it['suggestion'])} | {_cell(it['action'])} |")
    lines.append("")

    return "\n".join(lines)


def beijing_date():
    try:
        from zoneinfo import ZoneInfo
        tz = ZoneInfo("Asia/Shanghai")
    except Exception:
        tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y%m%d")


def archive_path(archive_dir, date=None):
    d = Path(archive_dir)
    date = date or beijing_date()
    cand = d / f"triage-{date}.md"
    n = 2
    while cand.exists():
        cand = d / f"triage-{date}-{n}.md"
        n += 1
    return cand


def resolve_playbook(name):
    p = Path(name)
    if name.endswith(".md"):
        if p.is_file():
            return str(p)
    else:
        cand = REPO_ROOT / "playbooks" / f"{name}.md"
        if cand.is_file():
            return str(cand)
        if p.is_file():
            return str(p)
    return None


def main(argv=None):
    parser = argparse.ArgumentParser(description="自动化编排与派工辅助工具")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    plan_parser = subparsers.add_parser("plan", help="根据编排生成运行计划")
    plan_parser.add_argument("playbook", help="编排文件路径或名称（如 pre-release）")
    plan_parser.add_argument("--out", "-o", help="输出文件路径（默认打印至标准输出）")
    plan_parser.add_argument("--reports", help="报告目录，带出其中最新分诊单的 P0/P1 与缺级别项")

    suggest_parser = subparsers.add_parser("suggest", help="根据变更文件推荐派工岗位")
    suggest_parser.add_argument("files", nargs="*", help="变更文件路径列表，写 - 表示从标准输入逐行读取")

    triage_parser = subparsers.add_parser("triage", help="扫描报告目录生成分诊单")
    triage_parser.add_argument("reports_dir", help="存放各岗位报告的目录")
    triage_parser.add_argument("--out", "-o", help="输出分诊单路径（默认打印至标准输出）")
    triage_parser.add_argument("--archive", help="归档目录，写为 triage-YYYYMMDD.md（北京时间，同日不覆盖）")

    args = parser.parse_args(argv)

    if args.cmd == "plan":
        target = resolve_playbook(args.playbook)
        if target is None:
            print(f"未找到编排: {args.playbook}", file=sys.stderr)
            print("可选名称: " + "、".join(playbook_names()), file=sys.stderr)
            return 1
        content = generate_run_plan(target, reports_dir=args.reports)
        if args.out:
            Path(args.out).write_text(content, encoding="utf-8")
            print(f"运行计划已写入: {args.out}")
        else:
            print(content)

    elif args.cmd == "suggest":
        files = args.files
        if files == ["-"]:
            files = [ln.strip() for ln in sys.stdin.read().splitlines() if ln.strip()]
        if not files:
            print("未指定文件列表。示例: python3 scripts/runner.py suggest src/auth/guard.ts")
            return 0
        suggestions = suggest_roles(files)
        if not suggestions:
            print("根据传入文件，未命中特定专项规则，可由幕僚长结合需求统一规划。")
            return 0
        print(f"根据变更特征，建议派发以下 {len(suggestions)} 个专项岗位：\n")
        for s in suggestions:
            print(f"- `{s['role']}`")
            print(f"  原因: {s['reason']}")
            print(f"  匹配文件: {', '.join(s['matched_files'][:3])}")
            print()

    elif args.cmd == "triage":
        try:
            res = generate_triage(args.reports_dir)
        except NotADirectoryError as e:
            print(str(e), file=sys.stderr)
            return 1
        if args.out:
            Path(args.out).write_text(res, encoding="utf-8")
            print(f"分诊单已保存: {args.out}")
        if args.archive:
            Path(args.archive).mkdir(parents=True, exist_ok=True)
            ap = archive_path(args.archive)
            ap.write_text(res, encoding="utf-8")
            print(f"分诊单已归档: {ap}")
        if not args.out and not args.archive:
            print(res)

    return 0


if __name__ == "__main__":
    sys.exit(main())
