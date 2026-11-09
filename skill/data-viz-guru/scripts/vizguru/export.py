"""Write a figure in the formats a client deliverable needs."""
from __future__ import annotations

from pathlib import Path

from .theme import load_tokens, preset as get_preset


def save(fig, path: str | Path, formats=("png", "svg"), alt_text: str | None = None) -> list[Path]:
    """Save `fig` at its preset's exact pixel size. `path` is given without an extension.

    PNG for slides and social, SVG (text kept as text) for designers, PDF for print.
    `alt_text` is written beside the image as `<name>.alt.txt` so it travels with the file
    into the CMS, the deck notes or the social post.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    ps = get_preset(fig._vg["preset"]) if hasattr(fig, "_vg") else None
    out = []
    for ext in formats:
        target = path.with_suffix(f".{ext}")
        fig.savefig(target, dpi=ps.dpi if ps else fig.dpi)
        out.append(target)
    if alt_text:
        target = path.with_suffix(".alt.txt")
        target.write_text(alt_text.strip() + "\n")
        out.append(target)
    return out


def presets() -> dict:
    """Name -> pixel size and intended use, for choosing an output format."""
    return {k: {"px": tuple(v["px"]), "use": v["use"]} for k, v in load_tokens()["presets"].items()}
