from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "SKILL.md"
EXPECTED_NAME = "guitar-pick-compositor"


def fail(message: str) -> None:
    raise SystemExit(message)


def main() -> None:
    text = SKILL.read_text(encoding="utf-8")
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        fail("SKILL.md must start with YAML frontmatter")
    frontmatter = text.split("\n---\n", 1)[0][4:]
    name_match = re.search(r"(?m)^name:\s*([^\s]+)\s*$", frontmatter)
    description_match = re.search(r"(?m)^description:\s*(.+?)\s*$", frontmatter)
    if not name_match or name_match.group(1) != EXPECTED_NAME:
        fail(f"SKILL.md name must be {EXPECTED_NAME}")
    if not description_match or len(description_match.group(1)) < 40:
        fail("SKILL.md needs a discriminating description")
    if re.search(r"(?i)\bTODO\b|\[TODO", text):
        fail("SKILL.md contains an unfinished placeholder")

    links = re.findall(r"\[[^\]]+\]\(([^)]+)\)", text)
    missing = []
    for link in links:
        if "://" in link or link.startswith("#"):
            continue
        target = (ROOT / link).resolve()
        try:
            target.relative_to(ROOT.resolve())
        except ValueError:
            fail(f"SKILL.md link escapes repository: {link}")
        if not target.exists():
            missing.append(link)
    if missing:
        fail("Missing SKILL.md resources: " + ", ".join(missing))

    required = [
        ROOT / "agents" / "openai.yaml",
        ROOT / "references" / "prompt-template.md",
        ROOT / "references" / "quality-checklist.md",
        ROOT / "scripts" / "build_layouts.py",
    ]
    absent = [str(path.relative_to(ROOT)) for path in required if not path.is_file()]
    if absent:
        fail("Missing required files: " + ", ".join(absent))

    metadata = (ROOT / "agents" / "openai.yaml").read_text(encoding="utf-8")
    if f"${EXPECTED_NAME}" not in metadata:
        fail("agents/openai.yaml default_prompt must name the skill explicitly")
    print(f"Repository validation passed for {EXPECTED_NAME}.")


if __name__ == "__main__":
    main()
