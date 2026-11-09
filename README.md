# Data Viz Guru

A Claude skill plus the charting toolkit behind it, for **financial and investment data visualisation used with clients**: static charts, interactive HTML charts, animated GIFs and MP4 data-story videos.

The skill is the judgement (what to say, which chart, what makes an investment chart misleading, what disclosures it needs). The toolkit is the craft (one consistent look, finance maths, export sizes, animation, and an automatic quality linter). Together they make the good version the easy version.

```
skill/data-viz-guru/        the skill: install this in Claude
  SKILL.md                  workflow, rules, when to use what
  references/               chart selection, finance conventions, design, storytelling,
                            disclosure & accessibility, QA checklist
  scripts/vizguru/          the Python toolkit (charts, finance, animate, interactive, lint, tokens.json)
  evals/                    test prompts and graders for the skill
examples/build_gallery.py   builds 12 example outputs from synthetic data (also the CI smoke test)
tests/                      pytest suite for finance maths, charts, linter, animation, HTML
tools/package_skill.py      builds dist/data-viz-guru.skill
```

## Try it

```bash
pip install -e ".[dev]"            # plus ffmpeg on the PATH for MP4
python examples/build_gallery.py   # writes examples/gallery/ and lints every chart
pytest -q
python tools/package_skill.py      # -> dist/data-viz-guru.skill, upload in Claude > Skills
```

## What it makes

| Output | How |
|---|---|
| Indexed performance, drawdown, returns heatmap, ranked/signed bars, risk-return, attribution waterfall, allocation, small multiples | `vizguru.charts` |
| Slide, report, LinkedIn square/portrait, 16:9 and 9:16 video sizes, light and dark | presets in `tokens.json` |
| Self-contained interactive HTML with 1Y/3Y/5Y/Max that re-index to 100 | `vizguru.interactive` |
| Line "reveal" animation with annotation beats to GIF or MP4 | `vizguru.animate` |
| Pre-flight checks: source, past-performance line, text size/contrast, clipping, overlaps, bar baseline, dual axes, pies; colour-blind palette check | `vizguru.lint` |

## Principles baked in

- Title is a computed finding; numbers are never typed by hand.
- Common start date, stated basis (total return, currency, net/gross), source and as-of date on every chart.
- One y-axis. Bars start at zero. Highlight the story, grey the rest. Label lines directly.
- Colour carries meaning, never red/green alone; palettes are checked for colour-blind separation.
- Animation only when the order of events is the point.

## Brand-matching a client

Edit `skill/data-viz-guru/scripts/vizguru/tokens.json` (colours, fonts, preset sizes), then:

```bash
PYTHONPATH=skill/data-viz-guru/scripts python -m vizguru.lint --palette
```

## Limits to know about

- Sample data is synthetic. Do not present it as market history.
- The linter finds mechanical faults only; it cannot judge whether a chart is true or fair.
- The compliance reference is general good practice, not legal advice. Client-facing material needs the firm's own compliance approval.
- Data connectors (Bloomberg, FactSet, Morningstar, custody files) are not included: bring a DataFrame of prices or returns.
