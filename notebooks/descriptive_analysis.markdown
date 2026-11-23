# Descriptive Analysis (Q1) Plan

Q1: How do sellers differ in order volume, late carrier handover rates and the number of late handovers?

This file lists the candidate descriptive analyses for the presentation (slides 4–5) and the report. We discuss each one and record the decision here. `notebooks/02_descriptive_analysis.ipynb` is then built from the agreed items, and its figures are saved to `figures/`.

All numbers below come from `Data/Clean/seller_metrics.csv` and `Data/Clean/monthly_benchmark.csv` (main sample: 93,598 orders, 2,917 sellers, January 2017 to August 2018, late handover by date).

## Shared settings

| Setting | Proposal | Decision |
|---|---|---|
| Input files | `Data/Clean/seller_metrics.csv`, `Data/Clean/monthly_benchmark.csv`; no re-cleaning | **Agreed** |
| Minimum orders for seller-level charts | Decided per chart; see **Which charts use a minimum-order threshold** below | **Agreed** |
| Figure files | Named by item number, because slide numbers are not final: `q1_01_kpi.png`, `q1_02a_pareto_curve.png`, `q1_02b_top20_sellers.png`, `q1_03a_late_rate_histogram.png`, `q1_03b_late_rate_bands.png`, `q1_04_funnel.png`, `q1_06_monthly_trend.png` (item 5 has no chart). The PPT role can save slide-numbered copies once the slides are final | **Agreed** |
| Calculations vs plots | Everything in one notebook, `notebooks/02_descriptive_analysis.ipynb`: table → chart → explanation for each item, with each chart saved to `figures/`. The PPT role can restyle charts in `05_figures.ipynb` | **Agreed** |
| Explanation for every chart | Every chart in `02_descriptive_analysis.ipynb` is followed by a markdown explanation: what it shows, how to read it, the key finding with numbers, and what it means for managers | **Agreed** |
| Tables behind each chart | In `02_descriptive_analysis.ipynb`, every chart is preceded by the table it is drawn from, shown with `display()`, so readers can see exactly which data each chart uses. These tables also serve as backup for slides and Q&A. No separate table files are saved | **Agreed** |
| Chart options for the PPT role | When two charts suit the same point, both are produced and saved, and the PPT role chooses | **Agreed** |

## Which charts use a minimum-order threshold

**Decision.** Charts that count orders, or that are dominated by large sellers, use all sellers. Charts that compare sellers' late *rates* use only sellers above the minimum-order threshold. One chart (item 4) shows all sellers on purpose, to explain why the threshold is needed.

**Why a threshold is needed for late-rate charts.** A seller's late rate is late orders divided by orders. With very few orders, one order decides the rate, so it can only be 0% or 100% and says little about the seller's real performance. As orders increase, the rate becomes stable:

| Seller order volume | Sellers | Late rate = 0% | Late rate = 100% | Std. dev. of late rate | Share of all orders |
|---|---|---|---|---|---|
| 1 | 537 | 85.8% | 14.2% | 0.35 | 0.6% |
| 2–4 | 665 | 81.2% | 2.4% | 0.22 | 2.0% |
| 5–9 | 516 | 73.8% | 0.4% | 0.15 | 3.7% |
| 10–19 | 421 | 57.5% | 0.2% | 0.13 | 6.2% |
| 20–49 | 372 | 46.8% | 0% | 0.10 | 12.6% |
| 50+ | 406 | 19.0% | 0% | 0.08 | 74.9% |

Sellers with fewer than 20 orders are 73% of sellers but only 12% of orders.

| Item | Chart | Sellers shown | Why |
|---|---|---|---|
| 1 | Headline numbers | All | They describe the whole sample; no seller is compared on its rate. |
| 2 | Concentration of late orders | All | It ranks sellers by late-order *counts*, not rates. The 50 sellers with the most late orders each have at least 32 orders, so the threshold does not change the result. |
| 6 | Monthly platform late rate | All | It is calculated from orders by month, not per seller. |
| 4 | Why a threshold is needed (funnel) | All, on purpose | Its purpose is to show how unstable small sellers' rates are. |
| 3 | Distribution of seller late rates | Above threshold | Without it, 64% of sellers sit at 0% and 95 at 100%, two spikes that hide the real differences between sellers. |
| 5 | Gap to the same-month benchmark | Above threshold | Without it, sellers with 1–2 orders produce extreme gaps (up to about +97 pp) that reflect sample size, not performance. |

Until the clustering team chooses the threshold, use 20 orders. Use the same threshold as Q2 so both questions describe the same sellers, and state it under each thresholded chart, for example "Sellers with ≥20 orders (778 of 2,917)".

**Presentation order.** Items 1, 2 and 6 (all sellers) → item 4 (why a threshold is needed) → items 3 and 5 (sellers above the threshold).

## Candidate analyses

### 1. Headline numbers (KPI row)

**What.** Six numbers at the top of slide 4, as stat tiles in two rows of three.

| Tile | Value | Note under the value | Sellers |
|---|---|---|---|
| Orders | 93,598 | Delivered, single-seller, Jan 2017 – Aug 2018 | All |
| Sellers | 2,917 | All sellers in the sample | All |
| Late handovers | 5,407 | Handed to the carrier after the deadline day | All |
| Platform late rate | 5.78% | Late handovers ÷ orders | All |
| Sellers never late (≥20 orders) | 32% | 251 of 778 sellers | Above threshold |
| Sellers never late (all sellers) | 64% | 1,875 of 2,917 sellers, but 87% have fewer than 20 orders | All, on purpose |

**Why.**
- The first four give the scale of the data and the baseline before any chart. They count orders, so small sellers do not distort them.
- The two "never late" tiles are shown side by side on purpose. Without a threshold, 64% of sellers look punctual, but 1,624 of those 1,875 sellers (87%) have fewer than 20 orders, and 698 have only 1–2: many have simply not had a chance to be late. With the threshold, the share is 32%. The contrast previews why rate-based charts use a threshold (item 4).
- The all-sellers tile is styled as a caution (grey value, dashed border) so it reads as the misleading version, not a headline result.

**Explanation.**
- *How to read it:* the top row gives the scale (orders, sellers, late orders); the bottom row gives the rates.
- *Key finding:* 5,407 of 93,598 orders (5.78%) were handed over late. With at least 20 orders, only 32% of sellers were never late; the 64% across all sellers is inflated by small sellers.
- *For managers:* late handover is not rare, and judging sellers with very few orders is unreliable.

**Slide.** 4. **Sellers.** See table. **Decision.** Agreed: six tiles as above. Values are computed from `seller_metrics.csv`, not typed in, so they update if the threshold changes.

### 2. Concentration of late orders (Pareto)

A Pareto chart shows whether a problem is concentrated in a few items, the "80/20" idea. Here: are late handovers concentrated in a few sellers?

**Decision.** Agreed: produce both charts below as options for the PPT role, plus a backup table.

#### 2A. Cumulative curve

**What.** Sellers ranked from most to fewest late orders. x-axis: cumulative share of sellers; y-axis: cumulative share of late orders. A dashed diagonal shows what equal shares would look like.

**Explanation.**
- *How to read it:* the further the curve sits above the diagonal, the more concentrated late handovers are.
- *Key finding:* the top 10 sellers (0.3% of sellers) account for 16.3% of late orders, and the top 50 (1.7%) for 40.6%. Only 1,042 sellers (36%) were ever late, so the curve reaches 100% at 36% of sellers.
- *For managers:* monitoring a small group of sellers addresses a large share of late handovers.

**Slide.** 4 (option).

#### 2B. Top 20 sellers by late orders (horizontal bars)

**What.** One bar per seller for the 20 sellers with the most late orders, labelled with the seller's order volume and late rate. Seller IDs are shown as ranks (Seller 1, 2, …) because the 32-character IDs are unreadable on a slide; see notebook 02 for full seller IDs.

**Explanation.**
- *How to read it:* bar length is the number of late orders; the label shows whether the seller is large, slow, or both.
- *Key finding:* the top 20 sellers account for 24.5% of late orders, but they are two different kinds of seller. Some are large and close to the platform rate (for example 1,658 orders at 4% late; 3 of the 20 are below the platform rate of 5.78%). Others are mid-sized and very late (for example 224 orders at 48% late; 12 of the 20 are more than 5 pp above their same-month benchmark).
- *For managers:* the number of late orders alone mixes "large but punctual" sellers with "genuinely slow" ones, which need different actions. Q2 groups sellers using their late handover rate and the log-transformed number of late handovers.

**Slide.** 4 or 5 (option), or backup; can also serve as the transition to Q2.

#### Table behind the charts

Shown in `02_descriptive_analysis.ipynb` before charts 2A and 2B: the 20 sellers with the most late orders, with rank, full `seller_id`, `order_volume`, `late_orders`, `late_rate`, `benchmark_late_rate`, `late_rate_gap_pp` and cumulative share of late orders. Ties in late orders are broken by `seller_id` so the ranking is reproducible. For backup slides and Q&A ("which sellers are these?").

**Sellers.** All (ranked by late-order counts; the threshold does not change the top 50).

### 3. Distribution of seller late rates

**Decision.** Agreed: produce both charts below as options for the PPT role. Recommended for the slide: 3B; 3A as backup.

**Sellers.** Above threshold (≥20 orders: 778 of 2,917).

#### Table behind the charts

Shown in `02_descriptive_analysis.ipynb` before charts 3A and 3B: late-rate bands for sellers with ≥20 orders.

| Late rate band | Sellers | Late orders | Share of all late orders |
|---|---|---|---|
| 0% | 251 | 0 | 0% |
| Above 0%, at or below platform (5.78%) | 290 | 1,198 | 22.2% |
| 5.78–10% | 96 | 750 | 13.9% |
| 10–20% | 88 | 1,282 | 23.7% |
| >20% | 53 | 1,263 | 23.4% |
| Sellers with <20 orders (not shown in the charts) | 2,139 | 914 | 16.9% |

The table also shows percentiles for sellers with ≥20 orders: 10th 0.0%, 25th 0.0%, median 2.7%, 75th 7.7%, 90th 16.2%.

#### 3A. Histogram

**What.** Seller late rates in 2-percentage-point bins, with a dashed line at the platform rate (5.78%) and a dotted line at the 90th percentile (16.2%). The last bin includes rates of 58% and above.

**Explanation.**
- *How to read it:* each bar is the number of sellers whose late rate falls in that bin.
- *Key finding:* most sellers are punctual (median 2.7%, a quarter at 0%), but there is a long right tail: the worst 10% of sellers are late on more than 16.2% of orders, and some exceed 30–60%.
- *For managers:* the platform average hides a small group of sellers who are late far more often than the rest.

**Slide.** Backup (option for slide 4).

#### 3B. Late-rate bands (bar chart)

**What.** Five bars: 0%, above 0% up to the platform rate, 5.78–10%, 10–20% and >20%. Each bar is labelled with the number of sellers and their share of all late orders. Bars at or below the platform rate are light; bars above it are dark. A note under the chart says the shares add up to 83% because sellers with fewer than 20 orders (17% of late orders) are not shown.

**Explanation.**
- *How to read it:* bar height is the number of sellers in the band; the label shows how much of the late-handover problem that band causes.
- *Key finding:* 541 sellers (70%) are at or below the platform rate and cause 22% of late orders. The 237 sellers above it (30%) cause 61%. Only 53 sellers are late on more than 20% of their orders, yet they cause 23% of late orders.
- *For managers:* the problem sits with a minority of sellers; this supports the Pareto finding from a rate perspective.

**Slide.** 4 (recommended).

### 4. Why a threshold is needed: order volume vs late rate (funnel scatter)

**What.** Scatter of all 2,917 sellers. x-axis: order volume (log scale); y-axis: late rate; point size: number of late orders. A vertical line marks the threshold (20 orders). Replaces the earlier scatter of sellers above the threshold only.

**Finding.**
- The points form a funnel: on the left, small sellers sit at 0% or 100%; to the right, rates narrow as volume grows (see the table in **Which charts use a minimum-order threshold**).
- There is no clear relationship between size and lateness: for sellers with ≥20 orders the correlation between log order volume and late rate is about 0 (0.003).

**Why.** The spread in observed rates at low order volumes explains the 20-order minimum for rate comparisons and clustering.

**Explanation.**
- *How to read it:* each point is a seller; further right means more orders, higher means a higher late rate, larger points have more late orders. The dashed line marks 20 orders.
- *Key finding:* sellers with 1 order can only be at 0% or 100%; the spread of late rates falls from a standard deviation of 0.35 (1 order) to 0.08 (50+ orders). Sellers under 20 orders are 73% of sellers but 12% of orders. Among eligible sellers, log order volume and late rate have almost no linear relationship (r = 0.003).
- *For managers:* late rates of very small sellers should not be used to rank them; and large sellers are not automatically more punctual, so both size and lateness matter.

**Table behind the chart.** Shown in `02_descriptive_analysis.ipynb` before the chart: the order-volume groups table in **Which charts use a minimum-order threshold**.

**Slide.** 5. **Sellers.** All, on purpose. **Decision.** Agreed: all sellers, used to explain the threshold.

### 5. Gap to the same-month benchmark

**Decision.** Agreed: no chart. Show the table below in `02_descriptive_analysis.ipynb` with an explanation, and use it as a credibility point on the slide or in Q&A.

**Sellers.** Above threshold (≥20 orders: 778).

#### Table (no chart)

Sellers with ≥20 orders, classified two ways: above the platform's overall late rate (5.78%, as in item 3), and above the platform rate in the same months they sold (`late_rate_gap_pp > 0`).

| | Above same-month benchmark | Not above |
|---|---|---|
| Above platform rate | 229 | 8 |
| Not above platform rate | 10 | 531 |

Also shown: the distribution of `late_rate_gap_pp` (10th percentile −6.0 pp, median −3.0 pp, 90th percentile +10.8 pp), and 131 sellers more than 5 pp above their benchmark, who cause 44.3% of all late orders.

**Explanation.**
- *How to read it:* the diagonal cells are sellers classified the same way by both comparisons; the off-diagonal cells change sides once months are taken into account.
- *Key finding:* 760 of 778 sellers stayed in the same category. The other 18 (2.3%) changed category when we used the same-month benchmark.
- *For managers and Q&A:* Of the 237 sellers above the overall platform rate, 229 were also above their same-month benchmark.

**Why no chart.** A chart of the gap would show almost the same picture as item 3B. Its value is as a credibility check, so a table and one sentence are enough.

**Slide.** One line under 3B or spoken: "Comparing each seller with the platform in the same months changes the classification of only 18 of 778 sellers." Full table as backup.

### 6. Monthly platform late rate (trend)

**Decision.** Agreed: two stacked panels sharing the same month axis. Slide 3 (data slide) or backup, and Q&A backup for item 5.

**Sellers.** All (order-level).

#### Table behind the chart

Shown in `02_descriptive_analysis.ipynb` before the chart: `monthly_benchmark.csv` (20 months: `order_purchase_month`, `orders`, `late_orders`, `late_rate`).

#### Chart

**What.**
- *Top panel (line):* platform late handover rate by purchase month, 2017-01 to 2018-08, with a dashed line at the overall rate (5.78%) and labels on January 2017, November 2017 and April 2018.
- *Bottom panel (bars):* orders per month, on the same month axis.
- The two measures are on different scales (0–20% vs 0–7,000 orders), so they are shown as two panels rather than one chart with two y-axes.

**Explanation.**
- *How to read it:* read the panels together; the bars show how many orders each month's rate is based on.
- *Key finding:*
  - January–February 2017 are highest (18.5% and 15.2%), but January has only 744 orders, so that peak is less reliable.
  - November 2017 to February 2018 is a second peak (8.4% in November). November also has the most orders of any month (7,194), which suggests sellers fall behind when demand surges. The link to Black Friday is our interpretation of the timing; the data does not record the cause.
  - April 2018 is the lowest (3.5%). Monthly rates range from 3.5% to 18.5%.
- *For managers:* platform-wide conditions change a lot from month to month, so sellers should be compared with the platform in the same months (item 5).

**Slide.** 3 (data slide) or backup; Q&A backup for item 5.

## Agreed analyses

- Item 1: headline numbers, six tiles.
- Item 2: concentration of late orders, both the cumulative curve (2A) and the top-20 bar chart (2B) as options for the PPT role, with the top-20 sellers table shown in the notebook.
- Item 3: distribution of seller late rates, both the histogram (3A) and the late-rate bands (3B) as options for the PPT role, with the bands table shown in the notebook.
- Item 4: funnel scatter of all sellers, used to explain the threshold.
- Item 5: gap to the same-month benchmark, table only (no chart), used as a credibility point.
- Item 6: monthly trend, platform late rate (top) and orders (bottom) as two stacked panels, with the monthly table shown in the notebook.
