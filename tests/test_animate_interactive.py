import matplotlib.pyplot as plt
import pytest

from vizguru import animate, charts, finance, sample_data

P = sample_data.prices("2018-01-01", "2024-12-31")
IDX = finance.thin(finance.rebase(P))[["Global equities", "Government bonds"]]


def make():
    return charts.line_chart(IDX, "Equities outgrew bonds over the seven years", "x", "Synthetic",
                             highlight=["Global equities"], performance=True, preset="slide_half",
                             annotations=[dict(date="2020-03-23", text="March 2020 sell-off")])


def test_reveal_ends_on_the_static_chart():
    fig = make()
    anim = animate.reveal(fig, seconds=1, hold=0.5, fps=10)
    anim._func(len(list(anim.new_frame_seq())) - 1)
    line = fig._vg["artists"]["Global equities"]["line"]
    assert len(line.get_xdata()) == len(IDX)
    assert fig._vg["annotations"][0]["text"].get_alpha() == 1.0
    plt.close(fig)


def test_reveal_starts_empty_with_annotations_hidden():
    fig = make()
    anim = animate.reveal(fig, seconds=1, hold=0.5, fps=10)
    anim._func(0)
    assert len(fig._vg["artists"]["Global equities"]["line"].get_xdata()) <= 2
    assert fig._vg["annotations"][0]["text"].get_alpha() == 0.0
    plt.close(fig)


def test_reveal_rejects_non_line_figures():
    fig = charts.bar_chart(IDX.iloc[-1], "Equities beat bonds by a wide margin", "x", "Synthetic")
    with pytest.raises(ValueError):
        animate.reveal(fig)
    plt.close(fig)


def test_mp4_and_gif_are_written(tmp_path):
    fig = make()
    anim = animate.reveal(fig, seconds=1, hold=0.4, fps=12, lead_in=0.2)
    mp4 = animate.save_animation(anim, tmp_path / "a.mp4")
    gif = animate.save_animation(anim, tmp_path / "a.gif", width_px=480)
    assert mp4.stat().st_size > 5_000 and gif.stat().st_size > 5_000
    from PIL import Image
    assert Image.open(gif).width == 480
    plt.close(fig)


def test_interactive_html_embeds_rebase_data(tmp_path):
    pytest.importorskip("plotly")
    from vizguru import interactive
    fig = interactive.line_interactive(P, "Equities outgrew bonds over the seven years", "x", "Synthetic",
                                       highlight=["Global equities"], performance=True)
    out = interactive.write_html(fig, tmp_path / "i.html", offline=False)
    html = out.read_text()
    assert "Past performance is not a reliable indicator" in html
    assert "plotly_relayout" in html and "__RAW__" not in html and "__X__" not in html
