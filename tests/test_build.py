import contextlib
import hashlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build as build_mod  # noqa: E402
import check as check_mod  # noqa: E402
import runner as runner_mod  # noqa: E402


def digest_tree(base):
    out = {}
    for p in sorted(Path(base).rglob("*")):
        if p.is_file():
            out[p.relative_to(base).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return out


def good_card(name="demo-role", dept="qa", extra_lines=60):
    secs = ["使命", "什么时候派", "开工先读", "工作步骤", "必查清单", "不做的事", "交付", "交接给谁"]
    lines = ["---", f"name: {name}", "title: 示例", f"dept: {dept}", "description: 示例角色，演示用",
             "cadence: 按需", "inputs: 项目档案", "outputs: 报告", "handoff: demo-role", "---", ""]
    for s in secs:
        lines += [f"## {s}", ""]
        lines += [f"- 条目 {i}" for i in range(extra_lines // len(secs) + 1)]
        lines.append("")
    return "\n".join(lines) + "\n"


def make_repo(tmp, card_text):
    root = Path(tmp)
    (root / "roles" / "qa").mkdir(parents=True)
    (root / "roles" / "_shared.md").write_text("## 共用边界\n\n只读优先。\n", encoding="utf-8")
    (root / "roles" / "qa" / "demo-role.md").write_text(card_text, encoding="utf-8")
    (root / "playbooks").mkdir()
    return root


class BuildTests(unittest.TestCase):
    def test_build_is_deterministic(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            build_mod.build(ROOT, Path(a) / "dist")
            build_mod.build(ROOT, Path(b) / "dist")
            d1, d2 = digest_tree(Path(a) / "dist"), digest_tree(Path(b) / "dist")
            self.assertEqual(d1, d2)
            self.assertGreater(len(d1), 0)

    def test_agent_frontmatter_only_four_keys(self):
        with tempfile.TemporaryDirectory() as t:
            build_mod.build(ROOT, Path(t) / "dist")
            f = next((Path(t) / "dist" / "claude-code" / "agents").glob("*.md"))
            head = f.read_text(encoding="utf-8").split("---")[1]
            keys = {ln.split(":")[0] for ln in head.strip().split("\n")}
            self.assertTrue(keys <= {"name", "description", "tools", "model"})

    def test_no_antigravity_output(self):
        with tempfile.TemporaryDirectory() as t:
            build_mod.build(ROOT, Path(t) / "dist")
            self.assertFalse((Path(t) / "dist" / "antigravity").exists())

    def test_shared_appended(self):
        with tempfile.TemporaryDirectory() as t:
            build_mod.build(ROOT, Path(t) / "dist")
            shared_head = (ROOT / "roles" / "_shared.md").read_text(encoding="utf-8").strip().split("\n")[0]
            for f in (Path(t) / "dist").rglob("*.md"):
                self.assertIn(shared_head, f.read_text(encoding="utf-8"))


class CheckTests(unittest.TestCase):
    def test_real_repo_passes(self):
        errors, nr, npb = check_mod.check(ROOT, 33, 7)
        self.assertEqual(errors, [])
        self.assertEqual((nr, npb), (33, 7))

    def test_good_synthetic_card_passes(self):
        with tempfile.TemporaryDirectory() as t:
            make_repo(t, good_card())
            errors, nr, _ = check_mod.check(t)
            self.assertEqual(errors, [])
            self.assertEqual(nr, 1)

    def test_missing_section_is_caught(self):
        bad = good_card().replace("## 必查清单", "## 其他")
        with tempfile.TemporaryDirectory() as t:
            make_repo(t, bad)
            errors, _, _ = check_mod.check(t)
            self.assertTrue(any("缺少章节 ## 必查清单" in e for e in errors), errors)

    def test_forbidden_word_is_caught(self):
        bad = good_card() + "\n" + "草" + "稿" + "\n"
        with tempfile.TemporaryDirectory() as t:
            make_repo(t, bad)
            errors, _, _ = check_mod.check(t)
            self.assertTrue(any("禁词" in e for e in errors), errors)

    def test_local_denylist_is_used(self):
        with tempfile.TemporaryDirectory() as t:
            make_repo(t, good_card() + "\nAcmeSecret\n")
            (Path(t) / ".denylist.local").write_text("# 私有词\nAcmeSecret\n", encoding="utf-8")
            errors, _, _ = check_mod.check(t)
            self.assertTrue(any("AcmeSecret" in e for e in errors), errors)

    def test_duplicate_name_and_bad_handoff_caught(self):
        with tempfile.TemporaryDirectory() as t:
            root = make_repo(t, good_card().replace("handoff: demo-role", "handoff: ghost-role"))
            (root / "roles" / "qa" / "other.md").write_text(good_card(), encoding="utf-8")
            errors, _, _ = check_mod.check(t)
            self.assertTrue(any("handoff" in e for e in errors), errors)
            self.assertTrue(any("重复" in e for e in errors), errors)

    def test_too_short_card_caught(self):
        with tempfile.TemporaryDirectory() as t:
            make_repo(t, "\n".join(good_card().split("\n")[:30]) + "\n")
            errors, _, _ = check_mod.check(t)
            self.assertTrue(any("行数" in e for e in errors), errors)


class RunnerTests(unittest.TestCase):
    def test_generate_run_plan(self):
        plan_text = runner_mod.generate_run_plan(ROOT / "playbooks" / "pre-release.md")
        self.assertIn("运行计划", plan_text)
        self.assertIn("chief-of-staff", plan_text)
        self.assertIn("可并行组", plan_text)

    def test_suggest_roles(self):
        files = ["src/auth/token.ts", "src/billing/pricing.vue", "deploy/docker-compose.yml"]
        suggestions = runner_mod.suggest_roles(files)
        roles = {s["role"] for s in suggestions}
        self.assertIn("security-reviewer", roles)
        self.assertIn("qa-permission-tester", roles)
        self.assertIn("finance-pricing", roles)
        self.assertIn("release-sre", roles)

    def suggested(self, *files):
        return {s["role"] for s in runner_mod.suggest_roles(list(files))}

    def test_suggest_no_substring_false_positives(self):
        self.assertEqual(self.suggested("scripts/build.py", "src/api/endpoint.ts", "src/guide.md"), set())
        self.assertEqual(self.suggested("src/user/border.css"), {"visual-design-reviewer"})
        self.assertEqual(self.suggested("Dockerfile"), {"release-sre"})

    def test_suggest_miniprogram_and_camel_case(self):
        roles = self.suggested("pages/index/index.wxml")
        self.assertIn("interaction-designer", roles)
        self.assertIn("qa-cross-platform", self.suggested("app.json"))
        self.assertIn("security-reviewer", self.suggested("src/AuthGuard.ts"))
        self.assertIn("release-sre", self.suggested(".github/workflows/test.yml"))

    def test_suggest_style_files_only_visual(self):
        for f in ("src/styles/theme.css", "pages/index/index.wxss", "src/app.scss"):
            self.assertEqual(self.suggested(f), {"visual-design-reviewer"}, f)

    def test_suggest_reads_stdin(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "runner.py"), "suggest", "-"],
                              input="src/auth/token.ts\nscripts/build.py\n",
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("security-reviewer", proc.stdout)
        self.assertNotIn("release-sre", proc.stdout)

    def write_report(self, d, name, body):
        (Path(d) / name).write_text(body, encoding="utf-8")

    def test_generate_triage(self):
        with tempfile.TemporaryDirectory() as t:
            self.write_report(t, "security-reviewer.md", "\n".join([
                "# 岗位报告：security-reviewer",
                "",
                "### SEC-001 存在越权漏洞",
                "- 级别：P0",
                "- 证据：src/auth/guard.ts:42",
                "- 建议：增加租户归属校验",
            ]))
            triage_text = runner_mod.generate_triage(t)
            self.assertIn("多岗位分诊汇总单", triage_text)
            self.assertIn("SEC-001", triage_text)
            self.assertIn("阻断", triage_text)

    def test_triage_dated_filename_role_and_unknown(self):
        with tempfile.TemporaryDirectory() as t:
            body = "### A-1 标题\n- 级别：P1\n"
            self.write_report(t, "security-reviewer-2026-10-22.md", body)
            self.write_report(t, "mystery-note.md", body)
            text = runner_mod.generate_triage(t)
            self.assertIn("`security-reviewer`", text)
            self.assertIn("`未识别`", text)
            self.assertIn("mystery-note.md", text)

    def test_triage_missing_level_not_p2(self):
        with tempfile.TemporaryDirectory() as t:
            self.write_report(t, "code-reviewer.md",
                              "### C-1 无级别\n- 证据：x\n\n### C-2 多选\n- 级别：P0 / P1\n")
            text = runner_mod.generate_triage(t)
            self.assertIn("缺级别", text)
            self.assertIn("缺级别: 2", text)
            self.assertIn("阻断", text)
            self.assertNotIn("一般与打磨项（P2 / P3）\n\n| ", text)

    def test_triage_pipe_escape_and_two_columns(self):
        with tempfile.TemporaryDirectory() as t:
            self.write_report(t, "code-reviewer.md",
                              "### C-1 标题含 a|b\n- 级别：P1\n- 建议：改 x|y\n- 建议去向：缺陷\n")
            text = runner_mod.generate_triage(t)
            self.assertIn("a\\|b", text)
            self.assertIn("| 建议 | 建议去向 |", text)
            row = next(ln for ln in text.splitlines() if ln.startswith("| P1"))
            self.assertIn("改 x\\|y | 缺陷", row)

    def test_plan_runs_from_any_directory(self):
        old = os.getcwd()
        with tempfile.TemporaryDirectory() as t:
            os.chdir(t)
            try:
                out = io.StringIO()
                saved, sys.stdout = sys.stdout, out
                try:
                    code = runner_mod.main(["plan", "pre-release"])
                finally:
                    sys.stdout = saved
            finally:
                os.chdir(old)
        self.assertEqual(code, 0)
        self.assertIn("运行计划", out.getvalue())

    def test_plan_unknown_name_fails(self):
        proc = subprocess.run([sys.executable, str(ROOT / "scripts" / "runner.py"), "plan", "no-such"],
                              capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("pre-release", proc.stderr)

    def test_plan_with_reports_brings_previous_p0(self):
        with tempfile.TemporaryDirectory() as t:
            self.write_report(t, "security-reviewer.md", "### SEC-9 旧越权\n- 级别：P0\n")
            (Path(t) / "triage-20261001.md").write_text(runner_mod.generate_triage(t), encoding="utf-8")
            plan = runner_mod.generate_run_plan(ROOT / "playbooks" / "pre-release.md", reports_dir=t)
            self.assertIn("上次 P0/P1，开工前逐条核对是否已关闭", plan)
            self.assertIn("SEC-9", plan)
        with tempfile.TemporaryDirectory() as t:
            plan = runner_mod.generate_run_plan(ROOT / "playbooks" / "pre-release.md", reports_dir=t)
            self.assertIn("无上次分诊单", plan)

    def test_triage_archive_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as t, tempfile.TemporaryDirectory() as a:
            self.write_report(t, "code-reviewer.md", "### C-1 x\n- 级别：P2\n")
            for _ in range(3):
                with contextlib.redirect_stdout(io.StringIO()):
                    runner_mod.main(["triage", t, "--archive", a])
            names = sorted(p.name for p in Path(a).iterdir())
            self.assertEqual(len(names), 3)
            self.assertTrue(names[0].startswith("triage-") and names[0].endswith(".md"))
            self.assertTrue(any(n.endswith("-2.md") for n in names))
            self.assertTrue(any(n.endswith("-3.md") for n in names))


if __name__ == "__main__":
    unittest.main()
