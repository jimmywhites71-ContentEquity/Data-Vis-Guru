"""Zip skill/data-viz-guru into dist/data-viz-guru.skill (a zip with the folder at its root).

Leaves out caches and the evals' scratch results so the package is only what the skill needs.
"""
import sys
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[1]
src = root / "skill" / "data-viz-guru"
out = root / "dist" / "data-viz-guru.skill"
skip_dirs = {"__pycache__", ".pytest_cache", "results"}

text = (src / "SKILL.md").read_text()
assert text.startswith("---\nname: data-viz-guru\n"), "SKILL.md frontmatter missing or name changed"
assert len(text.splitlines()) < 500, "SKILL.md too long: move detail into references/"

out.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for f in sorted(src.rglob("*")):
        if f.is_file() and not (set(f.relative_to(src).parts) & skip_dirs) and f.suffix != ".pyc":
            z.write(f, Path("data-viz-guru") / f.relative_to(src))
print(f"wrote {out} ({out.stat().st_size / 1024:.0f} KB)")
