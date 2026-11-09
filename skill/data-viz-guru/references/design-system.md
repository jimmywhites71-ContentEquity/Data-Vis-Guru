# Design system

All values live in `scripts/vizguru/tokens.json`. This page explains the reasoning so you can make good decisions where the toolkit does not decide for you.

## Anatomy (top to bottom)

1. **Title**: the finding, a sentence, sentence case, up to two lines. Colour: primary ink.
2. **Subtitle**: what is measured, units, currency, period. One line.
3. **Plot**: direct labels, no legend box where labels fit.
4. **Footer**: `Source: …`, as-of date, basis (gross/net), then the past-performance line when the chart shows performance.

Left-align everything to one edge. Whitespace is part of the design; do not fill it.

## Colour: four jobs, never mixed

| Job | Use | Rule |
|---|---|---|
| Emphasis | One accent against neutral grey | Grey the context; the story gets the colour |
| Identity | Up to four categorical colours in fixed order | The colour belongs to the entity (a fund keeps its colour across every chart in a deck), never to its rank |
| Polarity | Diverging pair, neutral midpoint | Blue for gain, red for loss by default; never red/green alone |
| Magnitude | One hue, light to dark | Heatmaps and maps; the lightest step is "near zero" |

- **Brand colours**: swap into `tokens.json`; run `python -m vizguru.lint --palette <file>`. The check fails when neighbouring series merge for protan/deutan readers or text contrast is too low.
- **Red/green**: if a client insists, keep the cell values printed and add a shape or sign cue; verify with the palette check.
- **Dark mode**: use the dark token set (its own steps, not an inversion). Prefer it for video and social; use light for print and documents.
- **Status colours** (good/warning/serious/critical) are reserved for status and always come with an icon or word.

## Typography

- One family (Inter by default, then Helvetica Neue, Arial). Title semibold, everything else regular; medium weight only to pick out the highlighted label.
- Sizes are set per medium by the preset (`text_scale`, `min_pt`). Smaller than the minimum fails the linter, because a chart that needs zooming has failed.
- Numbers: thousands separators, a true minus sign (−), consistent decimals within a chart, `+` on signed changes, units in the subtitle rather than on every label.
- Dates: `2014`, `Mar 2020`, or `31 Dec 2024`, not `12/31/24`. Be unambiguous for an international audience.

## Marks

- Lines 2 pt for highlighted, 1.2 pt for context; end-of-line dot with a surface-coloured ring.
- Bars: wide enough to hold the label, 4 px gap or a surface-coloured border between stacked segments; bars start at zero.
- Grid: horizontal only, pale, behind the data. Drop axes and ticks you do not need.
- Never use shadows, gradients, 3-D, textured fills or decorative icons inside a plot.

## Annotation

- Annotate the turning points the title talks about, two or three at most. Put the words on the chart next to the event, in primary ink with a background-coloured halo so they stay readable over a line.
- A callout should add what the axis cannot: the cause, the size of the move, the duration.
- Direct-label the last point of each line (name and value). Spread labels apart so they never overlap (`spread_labels` does this).

## Sizes by medium

| Preset | Pixels | Where it goes |
|---|---|---|
| `slide_16x9` | 1920×1080 | Full-slide chart |
| `slide_half` | 1200×1050 | Chart beside a text column |
| `report_full_width` | 1950×1100 @300 dpi | Report text width |
| `report_half_width` | 960×840 @300 dpi | Two charts across |
| `social_square` | 1080×1080 | LinkedIn/Instagram feed |
| `social_portrait` | 1080×1350 | Taller feed post |
| `video_1080p` | 1920×1080 | Landscape video |
| `video_vertical` | 1080×1920 | Reels, Shorts, Stories |

For social, cut the title to about 12 words and remove anything the thumbnail cannot show. For print, check greyscale.

## Layout for dashboards (when asked)

- Put the one number or chart that answers the main question top-left; supporting detail below.
- Same chart type, same colour and same scale for the same measure everywhere.
- One filter row at the top; no more than six panels.
- Every panel has its own title (a finding or a measure), its own source, and works at a glance.
