# Choosing the form

Start from the **question the reader will ask**, not from the chart catalogue. Each row says what to use, what the title should claim, and what not to do.

| The reader asks… | Use | Avoid |
|---|---|---|
| How did this grow, compared with alternatives? | `line_chart` on index levels rebased to 100 (or £10,000), highlight 1–3 series, grey the rest, label ends | More than ~4 coloured lines; different start dates |
| How much did I lose at the worst point, and how long to recover? | `drawdown_chart` | Reporting only the point-to-point return, which hides the path |
| How consistent is it, year by year / month by month? | `calendar_heatmap` (numbers printed in cells) or a bar per discrete year | Heatmap colour with no numbers |
| Which is best / worst? | `bar_chart` ranked, one colour, highlight the subject | Unsorted bars, 3-D, pies with more than three slices |
| Which of them gained or lost? | `bar_chart` with signed colours (blue gain, red loss) | Green/red as the only cue |
| What did I get for the risk I took? | `risk_return_scatter` | Dual-axis return-and-risk lines |
| Where did the return come from? | `waterfall` (attribution) | Stacked areas that bury the contributions |
| What am I holding / what is changing? | `allocation_bars` (100% stacked, compare rows) | Pies for comparing two portfolios, 3-D donuts |
| How do many series behave individually? | `small_multiples` on a shared axis | Spaghetti line chart with eight colours |
| Where do the numbers sit exactly? | A well-set table | A chart nobody can read values off |
| One number matters | A large number with a one-line caption | A chart for a single value |

## Rules of thumb

- **If you cannot write the title as a sentence with a verb and a number, you do not have a chart yet.** "Performance" is a label; "The portfolio fell half as far as equities" is a finding.
- **Show the path, not only the endpoints**, when risk is part of the story. Two portfolios that end at the same value can have very different journeys.
- **Cumulative growth charts flatter the long run; annual bars show variability.** Choose according to what the client needs to understand, and consider showing both.
- **Log scale** only for long horizons where equal percentage moves should look equal (multi-decade equity charts); label it clearly, because most clients read a straight line as constant growth in pounds.
- **Few categories, big marks; many data points, thin marks.**
- **Pie/donut**: acceptable only for two or three parts that sum to a whole and where the rough share is the message. Otherwise a ranked bar is easier to read.
- **Maps** only when geography explains the data (exposure by country with real regional patterns); otherwise a ranked bar.
- **Interactive vs static**: interactive for exploring many series or periods; static for the single message. Interactive charts must still make sense in their first, un-hovered state.

## Number of things on screen

- Lines: highlight ≤ 4, grey the rest.
- Categories on a bar: ≤ 12 before ranking and cutting ("top 10 and Other").
- Annotations: 2–3. More than that is a different chart.
- Words in a slide title: ≤ 20.
