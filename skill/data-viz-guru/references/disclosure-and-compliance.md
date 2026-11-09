# Disclosure, compliance and accessibility

**This page is general good practice, not legal or regulatory advice.** Rules differ by country, client type (retail vs professional) and channel, and change. Always tell the user to have the firm's compliance function approve client-facing material. Never describe a chart as "compliant".

## Performance charts: the usual expectations

Regulators in the UK, EU and US all start from the same principle: communications must be **fair, clear and not misleading**. In practice, charts of performance generally need:

- **A past-performance warning**, near the chart: "Past performance is not a reliable indicator of future results." (The toolkit adds this to the footer when `performance=True`; the linter errors if it is missing.)
- **Enough history.** UK FCA rules for retail communications (COBS 4.6) look for performance over a period that is relevant and not cherry-picked, usually shown as complete 12-month periods, and at least five years where the investment has existed that long. Verify the current rule text and any local variants with compliance before relying on this.
- **A stated basis**: currency, total vs price return, gross or net of charges, and the dates. Where figures are before fees, say how fees would reduce them.
- **A named source and as-of date.**
- **Clear separation of actual, simulated and projected results.** Simulated/backtested or hypothetical performance, and any forecast, must be labelled as such, with the basis and assumptions, and drawn differently (dashed, lighter, labelled).
- **No guarantee language**: do not imply the past will repeat; avoid titles such as "Steady growth you can rely on".
- **Benchmarks** that are relevant to the strategy and fairly disclosed.
- **Risk shown alongside return** whenever outperformance is claimed.

For US advisers, performance advertising has its own detailed requirements (for example on net-of-fee presentation and time periods). Use the firm's compliance guidance, not this page.

## Wording to avoid in titles

"Guaranteed", "safe", "risk-free", "always", "never lost", "beats the market" (unless shown over a fair, stated basis), "proven", and any promise about the future. Prefer verbs about what happened: "rose", "fell", "recovered", "returned".

## Standard footer elements

```
Source: [data provider], [index/fund names], to [as-of date].
Total return, [currency], [gross/net of fees]. [Rebalancing note if blended.]
Past performance is not a reliable indicator of future results. Capital at risk.
```

Illustrative or simulated material adds: "Illustrative only. Hypothetical results do not reflect actual trading and have limitations."

## Accessibility (also good business: charts get pasted into everything)

- **Contrast**: text ≥ 4.5:1 against its background (≥ 3:1 for large text); the linter checks the text colours; `python -m vizguru.lint --palette` checks the tokens.
- **Colour is never the only cue**: direct labels, printed values, signs, and line endings carry identity; polarity colours are blue/red (not red/green) and values are printed.
- **Alt text** for every image: state the type of chart, what is measured, and the finding with its key numbers, in one or two sentences. `export.save(..., alt_text=...)` writes it beside the image. Do not write "chart showing data".
- **Data table**: for interactive or complex charts, offer the numbers in a table or CSV as well.
- **Motion**: nothing flashes more than three times per second; provide a still or transcript for GIFs and videos.
- **Reading order**: title, subtitle, content, source. Keep the SVG text as text so screen readers and translators can reach it (the toolkit does).

## Privacy and data handling

Real client positions and returns are personal data. Do not paste them into places they should not go; use the firm's approved systems; remove account identifiers from chart files, filenames and alt text; and use clearly labelled synthetic data for demos and samples.
