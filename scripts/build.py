#!/usr/bin/env python3
"""从 roles/ 生成 dist/claude-code/agents/*.md 与 dist/markdown/*.md。"""
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from check import parse_card, role_files  # noqa: E402

AGENT_KEYS = ["name", "description", "tools", "model"]


def _yaml_value(v):
    if any(c in v for c in [": ", "#", "\"", "'"]) or v != v.strip():
        return json.dumps(v, ensure_ascii=False)
    return v


def build(root, out=None):
    root = Path(root)
    out = Path(out) if out else root / "dist"
    shared_path = root / "roles" / "_shared.md"
    shared = shared_path.read_text(encoding="utf-8").strip() + "\n"
    if out.exists():
        shutil.rmtree(out)
    agents_dir = out / "claude-code" / "agents"
    md_dir = out / "markdown"
    agents_dir.mkdir(parents=True)
    md_dir.mkdir(parents=True)
    count = 0
    for p in role_files(root):
        text = p.read_text(encoding="utf-8")
        meta, body = parse_card(text)
        if meta is None:
            raise SystemExit(f"{p}: frontmatter 格式错误")
        name = meta["name"]
        head = ["---"] + [f"{k}: {_yaml_value(meta[k])}" for k in AGENT_KEYS if meta.get(k)] + ["---", ""]
        agent = "\n".join(head) + body.rstrip("\n") + "\n\n" + shared
        (agents_dir / f"{name}.md").write_text(agent, encoding="utf-8", newline="\n")
        full = text.rstrip("\n") + "\n\n" + shared
        (md_dir / f"{name}.md").write_text(full, encoding="utf-8", newline="\n")
        count += 1
    return count


def main():
    root = Path(__file__).resolve().parent.parent
    n = build(root)
    print(f"已生成 {n} 个角色 -> {root / 'dist'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
