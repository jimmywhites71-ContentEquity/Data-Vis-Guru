# QA checklist

Use it two ways: as a **pre-send** list on your own chart, and as the structure of a **critique** of someone else's. Report problems in the order below: truth first, polish last.

## A. Is it true? (errors here are serious)

- [ ] Numbers in the title and annotations match the data (computed, not typed).
- [ ] Same start date, currency, fee basis and total-return treatment across series.
- [ ] Start and end dates are stated, and the story survives moving them by a year.
- [ ] Benchmark is relevant and fairly chosen.
- [ ] Bars start at zero; axes are not cropped to exaggerate.
- [ ] One y-scale (no dual axis). Log scale, if used, is labelled.
- [ ] Simulated, hypothetical and projected data are labelled and visibly distinct.
- [ ] Nothing important is left out (the bad year, the fees, the risk).
- [ ] Survivorship and selection are disclosed where relevant.

## B. Is it fair and compliant?

- [ ] Source and as-of date present.
- [ ] Past-performance statement present on performance charts.
- [ ] Basis stated: gross/net, currency, annualised/cumulative.
- [ ] No guarantee or promise language in title, labels, narration or alt text.
- [ ] Risk shown next to any claim of outperformance.
- [ ] Marked for the firm's compliance approval before client use.

## C. Is it clear in five seconds?

- [ ] The title states the finding in a sentence.
- [ ] One message; the eye lands on it first.
- [ ] Highlight vs context is obvious (colour for the story, grey for the rest).
- [ ] Lines are labelled directly; a legend is not needed.
- [ ] 2–3 annotations at most, at the turning points the title mentions.
- [ ] No chart junk: 3-D, gradients, heavy grid, decorative icons.
- [ ] Numbers formatted consistently (separators, decimals, true minus, units).

## D. Is it accessible?

- [ ] Text contrast ≥ 4.5:1; type at or above the medium's minimum.
- [ ] Meaning survives greyscale and colour-blindness (labels, printed values, signs).
- [ ] Alt text states the finding with numbers.
- [ ] Animation: pausing at annotations, no flashing, a still or transcript exists.

## E. Is it made right?

- [ ] Correct preset for where it will be used; exact pixel size exported.
- [ ] `lint.report(fig)` returns no errors; warnings considered.
- [ ] **Looked at the exported image** at full size: no label on a line, no clipping, no orphan words in the title.
- [ ] Dark/light version checked if both are needed.
- [ ] SVG text is live text; fonts embedded or available.
- [ ] Code and data saved next to the outputs so it can be refreshed.

## Critique template

```
Verdict: one sentence (ship / fix first / rethink).

Misleading or wrong
1. [issue] -> [specific fix]

Unclear
1. …

Untidy
1. …

What works (keep this): …
```

Lead with what could mislead a client; do not bury it under style notes.
