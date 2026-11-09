"""Design tokens -> matplotlib. Every chart in the toolkit draws its look from here."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl
from matplotlib import font_manager

TOKENS_PATH = Path(__file__).with_name("tokens.json")


@dataclass(frozen=True)
class Preset:
    name: str
    px: tuple[int, int]
    dpi: int
    use: str
    text_scale: float = 1.0
    min_pt: float = 9.0

    @property
    def inches(self) -> tuple[float, float]:
        return self.px[0] / self.dpi, self.px[1] / self.dpi


@dataclass(frozen=True)
class Theme:
    mode: str
    surface: str
    text_primary: str
    text_secondary: str
    text_muted: str
    grid: str
    axis: str
    context: str  # the grey used for "everything else" when one series is the story
    categorical: tuple[str, ...]
    sequential: tuple[str, ...]
    diverging: dict
    status: dict
    font_family: tuple[str, ...]
    title_weight: str
    sizes: dict

    def color(self, i: int) -> str:
        """Categorical slot i. Slots are fixed and never cycled: a 9th series is a design
        problem (fold into 'Other', facet, or grey out the context), not a colour problem."""
        if i >= len(self.categorical):
            raise ValueError(
                f"Asked for series colour {i + 1} but the palette has {len(self.categorical)}. "
                "Highlight the few series that carry the story and pass the rest as context."
            )
        return self.categorical[i]


def load_tokens(path: str | Path | None = None) -> dict:
    return json.loads(Path(path or TOKENS_PATH).read_text())


def preset(name: str, tokens: dict | None = None) -> Preset:
    presets = (tokens or load_tokens())["presets"]
    if name not in presets:
        raise KeyError(f"Unknown preset {name!r}. Choose from: {', '.join(presets)}")
    p = presets[name]
    return Preset(name, tuple(p["px"]), p["dpi"], p["use"], p.get("text_scale", 1.0), p.get("min_pt", 9.0))


def _first_installed(families) -> str:
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for fam in families:
        if fam in installed:
            return fam
    return "DejaVu Sans"


def get_theme(mode: str = "light", tokens_path: str | Path | None = None) -> Theme:
    """Return the theme for `mode` and set matplotlib's defaults to match it."""
    tokens = load_tokens(tokens_path)
    if mode not in tokens["modes"]:
        raise KeyError(f"mode must be one of {list(tokens['modes'])}")
    m = tokens["modes"][mode]
    f = tokens["font"]
    family = _first_installed(f["family"])
    theme = Theme(
        mode=mode,
        surface=m["surface"], text_primary=m["text_primary"], text_secondary=m["text_secondary"],
        text_muted=m["text_muted"], grid=m["grid"], axis=m["axis"], context=m["context"],
        categorical=tuple(m["categorical"]), sequential=tuple(m["sequential"]),
        diverging=m["diverging"], status=m["status"],
        font_family=(family,), title_weight=f["title_weight"], sizes=f["sizes_pt"],
    )
    mpl.rcParams.update({
        "font.family": family,
        "font.size": theme.sizes["label"],
        "figure.facecolor": theme.surface, "axes.facecolor": theme.surface,
        "savefig.facecolor": theme.surface,
        "text.color": theme.text_primary,
        "axes.edgecolor": theme.axis, "axes.labelcolor": theme.text_secondary,
        "axes.linewidth": 0.8,
        "axes.spines.top": False, "axes.spines.right": False, "axes.spines.left": False,
        "axes.grid": True, "axes.grid.axis": "y", "axes.axisbelow": True,
        "grid.color": theme.grid, "grid.linewidth": 0.8,
        "xtick.color": theme.text_secondary, "ytick.color": theme.text_secondary,
        "xtick.labelsize": theme.sizes["tick"], "ytick.labelsize": theme.sizes["tick"],
        "xtick.major.size": 3, "ytick.major.size": 0,
        "lines.linewidth": 2.0, "lines.solid_capstyle": "round",
        "legend.frameon": False,
        "svg.fonttype": "none",  # keep text editable when a designer opens the SVG
        "axes.unicode_minus": True,
    })
    return theme
