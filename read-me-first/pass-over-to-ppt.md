# Pass-over to the PPT Role

**Read this before building the Q1 slides or `05_figures`.** It explains which figures exist, which to use, and what still needs to be done to fit them to the slide template.

## Before you start

- Run `git pull` to get the latest figures and notebooks.
- Figures come from `notebooks/02_descriptive_analysis.ipynb`. Each figure there is preceded by the table it is drawn from and followed by an explanation (what it shows, how to read it, key finding, meaning for managers). Use those explanations for speaker notes.
- Why each chart was chosen: `notebooks/descriptive_analysis.markdown`.

## Figures (`figures/`)

Figures are named by item number, not slide number, because the slides are not final. Save slide-numbered copies once the deck is fixed.

| Item | File | Suggested use | Note to add on the slide |
| --- | --- | --- | --- |
| 1. Headline numbers | `q1_01_kpi.png` | Slide 4, top | The grey dashed tile (64%) is the misleading version, shown on purpose next to 32% |
| 2A. Pareto curve | `q1_02a_pareto_curve.png` | Slide 4 (recommended for item 2) | — |
| 2B. Top 20 sellers | `q1_02b_top20_sellers.png` | Slide 4 or 5, or backup; works as the transition to Q2 | Seller names are ranks; full IDs are in the notebook's top-20 table |
| 3A. Late-rate histogram | `q1_03a_late_rate_histogram.png` | Backup | "Sellers with ≥20 orders (778 of 2,917)" |
| 3B. Late-rate bands | `q1_03b_late_rate_bands.png` | Slide 4 (recommended for item 3) | "Shares add up to 83%; sellers with fewer than 20 orders cause the rest" (already in the chart footnote) |
| 4. Funnel scatter | `q1_04_funnel.png` | Slide 5: why a minimum-order threshold is needed | All sellers, on purpose |
| 5. Same-month benchmark | No chart | One sentence under 3B or spoken | "Comparing each seller with the platform in the same months changes the classification of only 18 of 778 sellers." |
| 6. Monthly trend | `q1_06_monthly_trend.png` | Slide 3 (data) or backup; Q&A backup for item 5 | "Black Friday" is our interpretation of the November peak, not recorded in the data |

Items 2 and 3 each have two versions so you can choose. Suggested Q1 order: items 1, 2 and 6 → item 4 → items 3 and 5.

## Chart style is not yet matched to the slide template

The charts use a neutral default style (system sans-serif font, blue palette, light background). To match the slide template:

- **Option 1: change the style in `02_descriptive_analysis.ipynb`.** In the setup cell, edit the colour constants (`INK`, `INK_2`, `MUTED`, `SURFACE`, `GRID`, `BLUE`, `LIGHT_BLUE`) and the `plt.rcParams.update({...})` block (add `"font.family"` for the template font), then rerun the notebook. All seven figures are redrawn in the new style.
- **Option 2: redraw in `05_figures.ipynb`.** Read `Data/Clean/seller_metrics.csv` and `Data/Clean/monthly_benchmark.csv` and copy the chart code you need.

Either way, change only the appearance. Do not change the data, filters or the `MIN_ORDERS` threshold, so the slide numbers match the report. Also check that labels still fit after changing the font or figure size.

## Numbers to use on the Q1 slides

| Number | Value |
| --- | --- |
| Orders / sellers in the main sample | 93,598 / 2,917 (January 2017 – August 2018) |
| Late handovers / platform late rate | 5,407 / 5.78% |
| Top 10 / top 50 sellers' share of late orders | 16.3% / 40.6% |
| Sellers above the platform rate (≥20 orders) | 237 of 778 (30%), causing 61% of late orders |
| Sellers never late | 32% of sellers with ≥20 orders (64% of all sellers, inflated by small sellers) |
| Monthly platform late rate | 3.5% (April 2018) to 18.5% (January 2017) |

**Correction.** The January 2017 platform late rate is **18.5%** (138 of 744 orders). An earlier draft said 18.6%; use 18.5%.

**If the threshold changes.** These numbers use a 20-order threshold. If the clustering team chooses another threshold, the notebook is rerun and the numbers that depend on it (rows 4 and 5) change. Check the notebook output before finalising the slides.
