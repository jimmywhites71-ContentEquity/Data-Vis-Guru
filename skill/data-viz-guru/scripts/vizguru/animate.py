"""Animated data stories: GIF for email, chat and social; MP4 for video and slides.

The approach is 'reveal': build the finished static chart first, then draw it on over time.
That guarantees the animation ends on exactly the chart that was reviewed and linted, and
keeps the axes fixed so the eye follows the data rather than a rescaling frame.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.animation import FFMpegWriter, FuncAnimation, PillowWriter

from .charts import spread_labels


def _ease(t: np.ndarray) -> np.ndarray:
    """Ease in and out (smoothstep) so the line accelerates gently and settles at the end."""
    return t * t * (3 - 2 * t)


def reveal(fig, seconds: float = 8.0, fps: int = 24, hold: float = 2.5, lead_in: float = 0.5,
           beat_pause: float = 0.9) -> FuncAnimation:
    """Animate a figure made by `charts.line_chart`, drawing the lines on from left to right.

    seconds     time spent drawing the lines
    hold        time the finished chart stays on screen (viewers need it to read the labels,
                and a looping GIF needs a rest before it restarts)
    lead_in     time on the empty frame, so the title can be read first
    beat_pause  extra time the animation pauses each time an annotation appears

    Each annotation on the chart appears as the line reaches its date and then stays.
    """
    arts = fig._vg.get("artists")
    if not arts or fig._vg.get("kind") != "line":
        raise ValueError("reveal() needs a figure from charts.line_chart")
    ax = fig.axes[0]
    notes = fig._vg.get("annotations", [])
    index = max((a["series"].index for a in arts.values()), key=len)
    n = len(index)

    # Build the frame -> data-position schedule, pausing at each annotation.
    draw = np.clip((_ease(np.linspace(0, 1, max(2, int(seconds * fps)))) * (n - 1)).round().astype(int), 1, n - 1)
    schedule: list[int] = [1] * int(lead_in * fps)
    pending = sorted(int(index.get_indexer([b["date"]], method="nearest")[0]) for b in notes)
    for k in draw:
        schedule.append(int(k))
        while pending and k >= pending[0]:
            schedule += [int(k)] * int(beat_pause * fps)
            pending.pop(0)
    schedule += [n - 1] * int(hold * fps)

    gap_px = next(a["label"].get_fontsize() for a in arts.values()) * 1.35 * fig.dpi / 72
    fade = max(1, int(0.35 * fps))
    # First frame on which each annotation is visible. Computed up front so that any frame can
    # be rendered on its own (thinned GIFs, previews, tests) and always looks the same.
    shown_at = {j: next(i for i, k in enumerate(schedule) if index[k] >= b["date"]) for j, b in enumerate(notes)}

    def draw_frame(i: int):
        k = schedule[i]
        now = index[k]
        names, ends = [], []
        for name, a in arts.items():
            ser = a["series"].loc[:now]
            if ser.empty:
                continue
            a["line"].set_data(ser.index, ser.values)
            if "dot" in a:
                a["dot"].set_data([ser.index[-1]], [ser.values[-1]])
            names.append(name)
            ends.append(ser.values[-1])
        for name, y, v in zip(names, spread_labels(ax, ends, gap_px), ends):
            a = arts[name]
            a["label"].xy = (now, y)
            a["label"].set_text(f"{name}  {a['format'](v)}")
            # Context labels wait for the final frame: while the story is being told they only
            # compete with the callouts, and the viewer has no use for them yet.
            a["label"].set_alpha(1.0 if a["role"] == "highlight" or k == n - 1 else 0.0)
        for j, b in enumerate(notes):
            alpha = min(1.0, (i - shown_at[j] + 1) / fade) if i >= shown_at[j] else 0.0
            b["marker"].set_alpha(alpha)
            b["text"].set_alpha(alpha)
            if b["text"].arrow_patch is not None:
                b["text"].arrow_patch.set_alpha(alpha)
        return []

    anim = FuncAnimation(fig, draw_frame, frames=len(schedule), interval=1000 / fps, blit=False)
    anim._vg_fps = fps
    return anim


def save_animation(anim: FuncAnimation, path: str | Path, width_px: int | None = None,
                   gif_fps: int = 12) -> Path:
    """Write `.mp4` (H.264, plays everywhere including PowerPoint and LinkedIn) or `.gif`.

    GIFs are written at `gif_fps` and, by default, 960px wide: a GIF is ten or more times
    the size of the same MP4, so keep it small enough to embed in an email. Pass `width_px`
    to override either format's width.
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig = anim._fig
    fps = getattr(anim, "_vg_fps", 24)
    native = fig.get_figwidth() * fig.dpi
    if path.suffix == ".mp4":
        dpi = fig.dpi * (width_px / native if width_px else 1)
        writer = FFMpegWriter(fps=fps, codec="libx264",
                              extra_args=["-pix_fmt", "yuv420p", "-crf", "18", "-movflags", "+faststart"])
        anim.save(path, writer=writer, dpi=dpi)
    elif path.suffix == ".gif":
        dpi = fig.dpi * ((width_px or 960) / native)
        step = max(1, round(fps / gif_fps))
        frames = list(range(0, anim._save_count if hasattr(anim, "_save_count") else 0, step))
        thin = FuncAnimation(fig, anim._func, frames=frames, interval=1000 * step / fps, blit=False)
        thin.save(path, writer=PillowWriter(fps=fps / step), dpi=dpi)
    else:
        raise ValueError("path must end in .mp4 or .gif")
    return path
