# Pass-over to the Clustering Team

**Read this before starting Q2 (`03_q2`) or the credibility checks (`04_checks`).** It collects the handoff notes from `notebooks/01_cleaning.ipynb` and `notebooks/02_descriptive_analysis.ipynb` in one place.

## Before you start

- Run `git pull` to get the latest notebooks, cleaned data and figures.
- Do not re-clean the data. Every notebook reads the files in `Data/Clean/`, so the numbers in the report, slides and code stay consistent.
- Run notebooks from the `notebooks/` folder; paths such as `../Data/Clean/` assume it.
- Why each cleaning step was taken: `notebooks/change.markdown`. Why each Q1 chart was chosen: `notebooks/descriptive_analysis.markdown`.

## Data files (`Data/Clean/`)

Created by `notebooks/01_cleaning.ipynb`, which loads the raw CSVs from this repository (`Data/Raw`).

| File | What to use it for |
| --- | --- |
| `seller_metrics.csv` | One row per seller (2,917): `order_volume`, `late_orders`, `late_rate`, `benchmark_late_rate`, `late_rate_gap_pp`, plus review summaries (see **Review ratings**). Input for Q1, the Q2 clustering and figures. No minimum-order threshold applied. |
| `monthly_benchmark.csv` | Platform late rate by purchase month, 2017-01 to 2018-08. Same-month baseline for Q1 and the monthly trend figure. |
| `orders_main.csv` | Main sample, one row per order (93,598), including `review_score_first` and `review_score_last`. Use it to rebuild seller metrics under other settings, such as the 2017 training and 2018 validation split. |
| `orders_group_b.csv` | 1,156 orders handed over after purchase but before payment approval. Use only in `04_checks`: combine with `orders_main.csv` and compare results. |

All main analysis (Q1, Q2, figures, report and slide numbers) reads `seller_metrics.csv` and `monthly_benchmark.csv`. Do not add `orders_group_b.csv` to the main analysis.

## Key definitions

- **Main sample:** delivered, single-seller orders with complete, correctly ordered timestamps, placed from January 2017 to August 2018.
- **Late handover:** an order handed to the carrier on a calendar day after its `shipping_limit_date` day.
- **`late_rate`:** a proportion from 0 to 1. The platform late rate in the main sample is 5.78% (5,407 of 93,598 orders).
- **`benchmark_late_rate`:** the late rate a seller would have if each of its orders were late at the platform rate for that order's month. **`late_rate_gap_pp`** is `late_rate` minus this benchmark, in percentage points.

## Minimum orders per seller (clustering team decides)

Many sellers have very few orders, so their late rates are unreliable. In the main sample, 79% of sellers with fewer than 5 orders have a 0% late rate and 10% have 100%. The funnel chart in `figures/q1_04_funnel.png` shows this.

| Minimum orders | Sellers kept | Share of sellers | Share of orders |
| --- | --- | --- | --- |
| None | 2,917 | 100% | 100% |
| 5 | 1,715 | 58.8% | 97.4% |
| 10 | 1,199 | 41.1% | 93.7% |
| 20 | 778 | 26.7% | 87.5% |
| 30 | 604 | 20.7% | 83.0% |

- The group plan suggests 20 orders for the main analysis, with 10 and 30 as checks in `04_checks`.
- Apply the threshold to sellers in the clustering step only. The platform late rate, the monthly benchmark and the Q1 distributions use all orders.
- Explain the chosen threshold in the report and show how results change under the alternatives.
- **Tell the group which threshold you choose.** Q1 uses the same threshold so both questions describe the same sellers (see **If you change the threshold** below).

## 2017 → 2018 holdout

Few sellers are active enough in both years. Rebuild yearly seller metrics from `orders_main.csv` and check this count early.

| Minimum orders in each year | Sellers in 2017 | Sellers in 2018 | Sellers in both years |
| --- | --- | --- | --- |
| 10 | 640 | 876 | 429 |
| 20 | 420 | 527 | 264 |
| 30 | 309 | 368 | 171 |

## Credibility checks for `04_checks`

**Handover before payment approval.** The main sample drops 1,156 orders that were handed over after purchase but before payment approval (saved separately as `Data/Clean/orders_group_b.csv`). These may be approval delays rather than data errors. In `04_checks`, combine the two files, rerun the seller metrics and K-means, then compare the platform late rate, seller late rates, k, cluster sizes and profiles, and the number of sellers that change cluster. If the results are similar, state in the report that this filter does not affect the conclusions. The 161 orders handed over before purchase stay dropped in both versions.

**Late handover definition.** The main analysis defines late handover by date (handed over on a day after the deadline day). In `04_checks`, rerun the seller metrics and K-means with the timestamp definition (`order_delivered_carrier_date > shipping_limit_date`), then compare the platform late rate (9.10% by timestamp), seller late rates, cluster profiles and the sellers in the high-priority group.

**Minimum-order threshold.** Rerun the clustering with the alternative thresholds (suggested 10 and 30) and compare the results.

## Review ratings (optional, for cluster profiles)

Review ratings are in `Data/Clean/` (change 8 in `notebooks/change.markdown`). Use them to describe the clusters; the clustering team decides which rating to use and reports the comparison.

| File | Columns |
| --- | --- |
| `orders_main.csv`, `orders_group_b.csv` | `review_score_first` (earliest review), `review_score_last` (latest review) |
| `seller_metrics.csv` | `reviewed_orders` (orders with a review), `avg_review_first`, `avg_review_last`, `low_review_share_first`, `low_review_share_last` (share of ratings of 2 stars or less) |

- **Why two ratings:** 547 orders have more than one review (most likely the customer answered the survey more than once; 202 have different scores). The earliest review is closest to the delivery experience; the latest is the customer's final view. For orders with one review, both columns are the same.
- **Shared reviews:** 789 reviews are attached to several orders bought together by the same customer; each of those orders keeps that score.
- **Missing ratings:** 622 of 93,598 main-sample orders (0.7%) have no review and keep missing ratings. 3 sellers have no reviewed orders, so their review columns in `seller_metrics.csv` are missing.
- Only 179 main-sample orders (0.2%) have different first and last scores.

### What we found so far

Using the current K-means result (late rate and log order volume, k = 3, sellers with ≥20 orders), the two ratings give practically the same results:

| Cluster | Avg. rating (last / first) | Share of reviews ≤ 2 stars (last / first) |
| --- | --- | --- |
| 1: small, mostly punctual (477 sellers) | 4.265 / 4.266 | 10.4% / 10.4% |
| 2: large (222 sellers) | 4.163 / 4.164 | 12.3% / 12.3% |
| 3: high late rate (79 sellers) | 3.811 / 3.813 | 21.3% / 21.2% |

- The difference between clusters is significant under both ratings (Kruskal-Wallis on seller averages: H = 95.4 and 95.7, p < 0.001).
- In every cluster, late orders score about 0.5–0.7 stars lower than on-time orders (orders of the 778 clustered sellers: 3.57 vs 4.20 under both ratings; across the whole main sample, 3.55 vs 4.21).
- The 18 sellers in cluster 2 with more than twice the platform late rate average 3.91 stars (17.9% low reviews), closer to cluster 3 than to the rest of cluster 2 (4.18).

### What to do

1. Choose which rating to use for the cluster profiles, and use it consistently in the notebook, report and slides.
2. Show the comparison with the other rating as a robustness check, for example: "Using the earliest instead of the latest review changes the score of 179 orders (0.2%) and does not change the results."
3. Use ratings to **describe** clusters, not as a clustering feature. Adding the average rating lowered the silhouette score in our tests, and it would change the question from late handover to overall seller quality.
4. Write the link as an association, not a cause: ratings also depend on carrier delivery and product quality ("late handovers are associated with lower review scores").

## Notes on the Q1 descriptive analysis

**If you change the threshold.** `02_descriptive_analysis.ipynb` uses 20 orders for the charts that compare sellers' late rates. If the clustering team chooses a different threshold, change `MIN_ORDERS` in its setup cell and rerun. The tables and charts update automatically, but the numbers quoted in the explanation text are for 20 orders and must be edited by hand.

**Seller ranking.** Two sellers in the top-20 list are tied on 54 late orders. The notebook orders ties by `seller_id`, so the ranking is reproducible. Use the notebook's ranking and the full seller IDs in its top-20 table as the final version.

**Figures for the slides.** Charts are in `figures/`, named by item number (for example `q1_02a_pareto_curve.png`), because slide numbers are not final. Items 2 and 3 each have two versions for the PPT role to choose from. Item 5 has no chart: its table is a credibility point to use in one sentence on the slide or in Q&A.

**Findings that lead into Q2.**
- Late handovers are concentrated: the top 50 sellers (1.7%) cause 40.6% of late orders.
- Sellers with many late orders are of two kinds: large sellers close to the platform rate, and mid-sized sellers with very high late rates. They need different actions.
- Order volume and late rate are unrelated (correlation about 0 for sellers with at least 20 orders), which is why clustering on both is informative.
- Comparing each seller with the platform in the same months changes the classification of only 18 of 778 sellers.

**Correction.** The January 2017 platform late rate is 18.5% (138 of 744 orders). An earlier draft said 18.6%; use 18.5%.
