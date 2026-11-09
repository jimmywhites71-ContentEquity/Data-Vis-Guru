# Finance conventions that decide whether a chart is honest

Check these before choosing colours. Each is a way real investment charts mislead without anyone intending it.

## Basis of the numbers

- **Total return vs price return.** Dividends and coupons are most of long-run bond and equity returns. State which, and compare like with like. Default to total return for performance.
- **Gross vs net of fees.** A chart for clients should say whether fund charges (and platform/advice fees, if relevant) are deducted. Never put a gross-of-fees portfolio next to a net-of-fees fund without saying so.
- **Currency.** Say which currency the returns are in. A global equity index in USD and in GBP can tell opposite stories in a year when sterling moved.
- **Real vs nominal.** If inflation is the point, show both or state it. Say so in the subtitle.
- **Annualised vs cumulative.** Never place the two side by side unlabelled. Annualise only periods of a year or more; do not annualise a three-month return.
- **Arithmetic vs geometric.** CAGR is geometric. An average of annual returns is arithmetic and is always higher when returns vary. Prefer CAGR for "what did I earn per year".

## Comparisons

- **Common start date.** Rebase every series on the first date all of them have data (`finance.rebase`). Different start dates make the comparison meaningless.
- **Start-date sensitivity.** Check that the story survives moving the start or end by a year. If a 2020 start makes the story and a 2019 start kills it, the chart is cherry-picking; either change it or say what the period was chosen for. Use rolling-return charts for robustness.
- **Benchmark choice.** A benchmark should be one a reasonable investor could have held instead, in the same currency and risk class. Do not choose a benchmark because it flatters the subject.
- **Risk next to return.** A higher return with higher volatility is not a better result by itself. When claiming outperformance, show a risk measure (volatility, max drawdown) somewhere on the page.
- **Survivorship.** Funds that closed or merged are missing from any "top funds over 10 years" list. If the universe is today's survivors, say so.
- **Backtests and model portfolios.** Label as hypothetical or simulated, state the method and fees assumed, and keep them visually distinct from actual results (dashed lines, a different label).
- **Smoothed or rebalanced series.** State the rebalancing frequency in the note for any blended portfolio.

## Calculations (all in `vizguru.finance`)

| Measure | Convention used |
|---|---|
| `rebase` | First date with data for every series = 100 |
| `total_return` | Last / first − 1 |
| `cagr` | (Last / first)^(1 / years) − 1, years = calendar days / 365.25 |
| `annualised_vol` | Sample std of daily simple returns × √252 |
| `drawdown` | Price / running peak − 1 |
| `calendar_returns` | Last price in each calendar month; first month measured from the first price (partial) |
| `discrete_periods` | Returns for the last n complete 12-month periods ending on the final date |

If a client's own methodology differs (for example time-weighted returns from a custody system, or money-weighted returns), use their numbers and say so. Do not recompute official performance from prices.

## Data hygiene

- Sort oldest to newest; check for gaps, stale prices, splits, and currency mismatches before charting.
- Use the as-of date from the data, not the date you made the chart.
- Keep the source file and the code alongside the output so that the chart can be reproduced and refreshed.
- Round for display only; never round before computing.
- Say "n/a" rather than plotting an invented value where data is missing.
