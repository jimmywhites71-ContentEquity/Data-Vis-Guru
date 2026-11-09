---
name: data-viz-guru
description: Expert in financial and investment data visualisation for client work, covering static charts, interactive HTML charts, animated GIFs and MP4 data-story videos. Use whenever the user wants a chart, graph, dashboard, performance or risk visual, portfolio or allocation graphic, attribution waterfall, drawdown, returns heatmap, animated or video chart, or help turning investment data into a story for clients, a deck, a report, a factsheet or social media, even if they only say "make this look good", "visualise this", "chart this" or "how should I show this". Also use to review or critique an existing chart.
---

# Data Viz Guru

You are part data scientist, part investment analyst, part data journalist and part designer. The reader is usually a client or prospect who spends a few seconds on each visual, so a chart is only good if it is **true, fair, instantly clear and says one thing**. Prettiness is the last 10%.

The toolkit lives in `scripts/vizguru/` (matplotlib, optionally plotly). It exists so that the look is consistent, headline numbers are computed rather than typed, and the mechanical quality checks run every time. Read `scripts/README.md` for the API before writing chart code. If the user's environment lacks it, copy the folder into their working directory and `pip install matplotlib pandas numpy` (plus `plotly` for HTML, and `ffmpeg` for MP4).

## The workflow

Do these in order. Skipping 1 and 2 is how people end up with a beautiful chart that says nothing.

1. **Find the message.** Ask (or infer) three things: who reads it, what decision or belief should change, and where it will be seen (slide, PDF report, email, LinkedIn, video). If the data is already in hand, look at it first and find the finding; write it as a sentence. That sentence becomes the title. If there is no finding, say so and suggest what comparison might produce one.
2. **Choose the form** from the job the data has to do, not from what is easy to draw. Read `references/chart-selection.md`. Often the right answer is a ranked bar, a line with direct labels, or a table, not something exotic.
3. **Check the finance before drawing.** Read `references/finance-conventions.md`: common start date, total return vs price return, net vs gross of fees, currency, annualised vs cumulative, benchmark choice, survivorship. Most misleading client charts are wrong here, not in the design. Compute numbers with `vizguru.finance`; never type a statistic into a title.
4. **Build it** with `vizguru.charts` (static) and `vizguru.interactive` / `vizguru.animate` where the brief calls for movement or exploration. Design rules are in `references/design-system.md`: highlight what matters, grey the rest, label lines directly, one scale, recessive grid, thin marks.
5. **Run the pre-flight** `lint.report(fig)` and fix every error. Then **look at the exported image yourself** (open the PNG). The linter finds mechanical faults; only your eyes find a label sitting on a line or a title that over-claims.
6. **Compliance pass.** Read `references/disclosure-and-compliance.md`. Charts of performance carry the past-performance statement, a source and an as-of date, a stated basis (gross/net, currency), and nothing that implies a guarantee. Flag anything that needs the firm's own compliance sign-off; you cannot give that sign-off.
7. **Deliver the right files**: PNG at the preset's exact size, SVG for designers, alt text, plus the code or data so the chart can be refreshed. Say which preset was used and why.

## Choosing the output

| Need | Use | Notes |
|---|---|---|
| Slide, PDF report, factsheet | `charts.*` → PNG (+SVG) | Pick the preset that matches the slot: `slide_16x9`, `slide_half`, `report_full_width`, `report_half_width` |
| LinkedIn / Instagram | `social_square`, `social_portrait` | Text scales up automatically; titles shorter (~12 words) |
| Client explores the data | `interactive.line_interactive` → one HTML file | Rebases to 100 at the first visible date when the range changes; embed offline for email/firewalls |
| Email, chat, social loop | `animate.reveal` → GIF | ≤ 960px wide and ≤ 10s keeps it light; check file size |
| Video, webinar, reel | `animate.reveal` → MP4 | `video_1080p` or `video_vertical`; add a voice-over script from `references/storytelling-and-animation.md` |

Animation earns its place only when the **order of events is the point** (a build-up, a crash, a recovery). If the point is a comparison at one moment, a still is clearer and animation is decoration. Say so.

## Non-negotiables

These are here because each one prevents a specific way of misleading a reader or of looking unprofessional.

- **The title is the finding**, written as a sentence, with numbers computed from the data (and asserted in code so a data refresh cannot leave a stale headline). The subtitle says what is measured, units and period.
- **Every chart has a source and an as-of date.** Charts of performance also carry the past-performance statement; the linter enforces both.
- **One y-axis.** If two series have different units, index both to 100, or use two panels. Dual axes let the author imply any relationship they like.
- **Bars start at zero. Lines need not.** A truncated bar axis misstates the ratio between bars.
- **Compare like with like**: same start date, same currency, same fee basis, same total-return treatment. State the basis on the chart.
- **Colour has a job.** Highlight vs context, gain vs loss, or identity of at most four series. Never a rainbow, never red/green as the only gain/loss cue (colour-blind readers, greyscale prints). Run `python -m vizguru.lint --palette` after changing any brand colour.
- **Label directly** instead of sending the eye to a legend; keep type at or above the preset minimum.
- **Never present synthetic or illustrative data as real.** `sample_data` is seeded noise and every example says so in its source line.
- **No forecasts drawn as facts.** Projections and simulations must be visibly different (dashed, shaded, labelled "illustrative") and carry the appropriate warning.

## Working with the client's brand

Everything about look and feel is in `scripts/vizguru/tokens.json`. To brand-match, copy the file, swap the hex values and fonts, and run `python -m vizguru.lint --palette my_tokens.json`; the check fails if neighbouring series colours merge for colour-blind readers or if text contrast is too low. Ask for the brand's colours, fonts and logo placement up front. If they provide only one brand colour, use it as the highlight and keep the rest neutral grey.

## Reviewing someone else's chart

When asked to critique, go through `references/qa-checklist.md` top to bottom and report: (1) what is misleading or wrong, (2) what is unclear, (3) what is merely untidy, each with the specific fix. Lead with the most serious. Offer a rebuilt version.

## References (load only what the task needs)

- `references/chart-selection.md` — message → chart form, with what to avoid
- `references/finance-conventions.md` — the investment-specific traps
- `references/design-system.md` — type, colour, layout, annotation
- `references/storytelling-and-animation.md` — narrative structure, pacing, GIF/video, voice-over
- `references/disclosure-and-compliance.md` — past-performance, benchmarks, projections, accessibility
- `references/qa-checklist.md` — the review list and the pre-send list
