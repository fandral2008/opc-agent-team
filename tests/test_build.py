import hashlib
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build as build_mod  # noqa: E402
import check as check_mod  # noqa: E402


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

    def test_shared_appended(self):
        with tempfile.TemporaryDirectory() as t:
            build_mod.build(ROOT, Path(t) / "dist")
            shared_head = (ROOT / "roles" / "_shared.md").read_text(encoding="utf-8").strip().split("\n")[0]
            for f in (Path(t) / "dist").rglob("*.md"):
                self.assertIn(shared_head, f.read_text(encoding="utf-8"))


class CheckTests(unittest.TestCase):
    def test_real_repo_passes(self):
        errors, nr, npb = check_mod.check(ROOT, 33, 6)
        self.assertEqual(errors, [])
        self.assertEqual((nr, npb), (33, 6))

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


if __name__ == "__main__":
    unittest.main()
