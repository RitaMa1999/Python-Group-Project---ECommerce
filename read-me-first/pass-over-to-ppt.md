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

## Q2 and credibility-check slides (6–9)

Q2 figures come from `notebooks/03_q2.ipynb`; check results come from `notebooks/04_checks.ipynb` (English summary at the top). The report uses the same wording and numbers (`read-me-first/pass-over-to-report.md`).

### Wording

| Item | Use | Avoid |
| --- | --- | --- |
| Groups | tier | cluster, "natural groups", "types of sellers" |
| Tier names | Tier 1 Rarely late · Tier 2 Occasionally late · Tier 3 Slightly above platform, high volume · Tier 4 Severely late | "often late" for Tier 3 |
| Ratings | "associated with" | "caused by", "leads to" |
| Shares | Name the denominator: "of the 778 sellers with ≥20 orders" or "of all late handovers" | A bare "77%" |
| Who to act on | The top 20 sellers | "All of Tier 3" |

### Figures

| Slide | File | Note to add on the slide |
| --- | --- | --- |
| 6 Q2 method | `q2_01_choose_k.png` (optional; text alone is fine if time is short) | "No k stands out, and the data scores no higher than data with no groups, so k = 4 is a judgement" |
| 7 Q2 findings | `q2_02_tiers.png` | "The tiers lie along one lateness scale" |
| 7 Q2 findings | `q2_03_tier_ratings.png` | "After adjusting for product category, only Tier 4 is still rated lower" |
| 8 Q2 recommendations | No chart: the top 5 sellers (below) and the action for each tier (agreed on Friday, see `pass-over-to-report.md`) | Use the first 6 characters of each seller ID |
| 9 Credibility checks | No chart: the check table below | — |

### Numbers for the Q2 slides

| Number | Value |
| --- | --- |
| Sellers in the tiers | 778 with ≥20 orders (87.5% of orders) |
| Tiers (sellers, late rate) | Tier 1: 383, 0.6% · Tier 2: 236, 3.2% · Tier 3: 132, 8.6% · Tier 4: 27, 36.1% |
| Focus tiers (4 and 3) | 159 sellers (20% of the 778) with 77% of these sellers' late handovers (64% of all late handovers) |
| Top 20 sellers | 46% of the positive excess late handovers across all 778 tiered sellers. All 20 had significantly more late handovers than expected under the main test. |
| Low ratings (≤2 stars) | Tier 4: 26.0% · Tier 1: 9.6% |
| Effect on customers | Only about 20% of late deliveries followed a late handover |

Top 5 sellers by excess late handovers (late handovers above what the same-month platform rate predicts):

| Rank | Seller | Tier | Orders | Late handovers | Late rate | Excess late handovers |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 7c67e1 | 3 | 963 | 189 | 19.6% | 134 |
| 2 | 88460e | 4 | 224 | 107 | 47.8% | 94 |
| 3 | 06a2c3 | 4 | 369 | 102 | 27.6% | 84 |
| 4 | 1025f0 | 3 | 869 | 115 | 13.2% | 69 |
| 5 | 816025 | 3 | 352 | 80 | 22.7% | 58 |

### Slide 9: credibility checks

| Check | Result |
| --- | --- |
| Minimum orders 10 or 30 instead of 20 | At least 99% of eligible original focus sellers and all of the original top 20 stay in focus. |
| Late by timestamp instead of by date | 99% of the original focus sellers and all of the original top 20 stay in focus. |
| Orders handed over before payment approval added | All original focus sellers stay in focus, including the top 20. |
| Three or five tiers instead of four | With five tiers, 97% of the original focus sellers stay in focus. With three tiers, 58 sellers are in focus, including 18 of the original top 20. |
| Earlier feature set using order volume | 14 of the original top 20 stay in focus. |
| Tiers built on 2017, checked in 2018 | 2017 focus sellers are still worse in 2018 (7.3% vs 2.6% late). Individual sellers move between tiers, so tiers are a snapshot |
| Chance | Allowing for late handovers that bunch in some months, all top 20 sellers are worse than the platform |

One sentence for the slide: "Most of our top 20 sellers stayed in the focus group across the checks. With three tiers, 18 stayed in focus. With the earlier feature set, 14 did."

### Questions to prepare for

1. **Why use K-means if the ranking already finds the top 20?** The ranking says whom to act on first; the tiers say which kind of action fits each group.
2. **What about sellers with fewer than 20 orders?** They are outside the tiers; use a simple rule, such as a reminder after a set number of late handovers.
3. **Do late handovers cause low ratings?** They are associated with lower ratings. After adjusting for product category, only Tier 4 is rated lower on orders that were on time.
4. **Is a seller's tier fixed?** No. The tiers describe one period, so sellers are re-scored each period with the same boundaries.
5. **Q1 says 237 sellers are above the platform rate; why does Q2 focus on 159?** Q1 counts every seller whose own late rate is above the platform. Q2 groups sellers by both late rate and number of late handovers: 97 of the 237 are in Tier 2 with only a few late handovers, and Tier 3 also includes about 20 large sellers whose late rate is at or below the platform.

