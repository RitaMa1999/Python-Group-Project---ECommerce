# Pass-over to the Report Role (Q2)

**Read this before writing the Q2 parts of the report (chapters 4–6).** It lists what each chapter needs, the limitations to state, and the draft recommendations. The slides use the same wording and numbers: see the "Wording" table in `read-me-first/pass-over-to-ppt.md`.

## Sources

| What | Where |
| --- | --- |
| Method, tier profiles, ratings, focus tiers, ranking | `notebooks/03_q2.ipynb` (each section starts with an explanation) |
| Credibility checks | `notebooks/04_checks.ipynb`; the English summary at the top can be used almost as it is |
| Seller lists | `Data/Results/seller_tiers.csv` (778 sellers), `Data/Results/focus_sellers_ranked.csv` (159 focus-tier sellers) |
| Figures | `figures/q2_01_choose_k.png`, `figures/q2_02_tiers.png`, `figures/q2_03_tier_ratings.png` |

## Chapter 4: Q2 seller tiers and priorities

Write it in the order method → results → what it means.

**Method.** State these points:

- Only sellers with at least 20 orders are placed in tiers (778 sellers, 87.5% of orders). The threshold applies to the tiers only; the platform late rate uses all 93,598 orders.
- Two features, both standardized: **late rate** (severity) and **log(1 + late orders)** (scale of late handovers). Q2 asks about the scale of late handovers, not the size of the seller, so late orders replace order volume. With order volume, the seller with the most late handovers was grouped with large, mostly punctual sellers.
- K-means was run for k = 2 to 8. The silhouette score of the real data is no higher than for data built to have no groups, and the elbow has no sharp bend. The two features are linked (late orders = late rate × order volume), so K-means cuts sellers into ordered tiers along one lateness scale. k = 4 is a judgement: four tiers can each be given a management action. The tier assignments were very similar across 10 random seeds (minimum adjusted Rand index 0.980).
- **Focus tiers** are the tiers whose late rate is above the same-month platform rate (Tiers 4 and 3). Inside them, sellers are ranked by **excess late handovers**: actual late handovers minus the number the same-month platform rate predicts.
- The ranking answers "whom to act on first"; the tiers answer "which kind of action fits each group".

**Results.** Use the tier table in Section 4 of `03_q2` and these numbers:

| Tier | Sellers | Late rate | Gap to same-month platform | Share of late handovers (778 sellers) | Ratings ≤ 2 stars |
| --- | --- | --- | --- | --- | --- |
| 1 Rarely late | 383 | 0.6% | −5.1 pp | 3% | 9.6% |
| 2 Occasionally late | 236 | 3.2% | −2.6 pp | 20% | 11.8% |
| 3 Slightly above platform, high volume | 132 | 8.6% | +2.8 pp | 58% | 14.1% |
| 4 Severely late | 27 | 36.1% | +29.9 pp | 18% | 26.0% |

**Sentences you can use:**

- "We use K-means to cut sellers into four tiers along a single lateness scale. The tiers are not natural groups: the silhouette score is no higher than for data with no groups, partly because late orders equal late rate times order volume."
- "The 159 sellers in the two focus tiers account for 77% of late handovers among the 778 sellers with at least 20 orders (64% of all late handovers in the main sample)."
- "The top 20 sellers account for 46% of the total positive excess late handovers across all 778 tiered sellers."
- "The ranking by excess late handovers tells managers whom to act on first; the tiers tell them which kind of action fits each group of sellers."
- "Late handovers are associated with lower ratings. After adjusting for product category, only Tier 4 is rated lower on orders that were on time."

**Two ratings tables.** Section 5 of `03_q2` shows ratings two ways. The table above weights every order equally (Tier 4: 3.63 stars on average). The Kruskal-Wallis test uses one average per seller (Tier 4: 3.64), because orders of the same seller are not independent. Quote the first in the text and the second only with the test.

**Q1 and Q2 numbers.** Q1 reports 237 sellers above the platform rate; Q2 focuses on 159 sellers. They answer different questions: Q1 counts every seller whose own late rate is above the platform, while the Q2 tiers group sellers by both late rate and number of late handovers. 97 of the 237 are in Tier 2 with only a few late handovers.

## Chapter 5: credibility checks and limitations

**Checks.** Use the English summary at the top of `04_checks`.

**Limitations.** State at least 1–6.

1. **The tiers are not natural groups.** They are cut from one lateness scale, partly because the two features are linked. One side effect: about 20 large sellers in Tier 3 have a late rate at or below the platform and are there only because of their number of late handovers. Their excess late handovers are zero or negative, so they come last in the ranking.
2. **k = 4 is a judgement.** The edge of the focus group depends on k: with k = 3 only the 58 most severe sellers are in focus. With three tiers, 18 of the original top 20 sellers stayed in focus.
3. **Some choices were made after seeing results.** The second feature (late orders instead of order volume) and the focus-tier rule were set after looking at the results. The reason is the wording of Q2, and the earlier version is shown in `04_checks` (check 5).
4. **The effect on customers is small.** Only about 20% of late deliveries followed a late handover. Fixing the top 20 sellers' excess late handovers might avoid about 3% of late deliveries and about 1% of low ratings (an association-based estimate, not causal).
5. **Ratings show association, not cause.** Ratings also depend on carrier delivery and product quality. After adjusting for product category, only Tier 4 is rated lower, and Tier 4 has only 27 sellers.
6. **Only sellers with at least 20 orders.** The 2,139 smaller sellers (73% of sellers, 12.5% of orders, 17% of late handovers) are outside the tiers.
7. **The holdout is small and shows persistence only, and tiers are a snapshot.** Only 264 sellers are active in both 2017 and 2018. 2017 focus sellers are still worse in 2018, but only 51% of sellers stay in the same tier, and the 2017 Tier 4 sellers fall from 33% to 9.5% late (partly regression to the mean). It does not show that acting on the list would help.
8. **Limits from cleaning.** Measuring lateness by date is lenient; cancelled orders are removed, so sellers that never shipped may look better than they are (see `notebooks/change.markdown`).

## Chapter 6: recommendations (draft, to agree with Rui on Friday 20 November)

| Tier | Priority | Draft action |
| --- | --- | --- |
| 4 Severely late (27 sellers) | First | Contact each seller and find the cause (capacity, process, stock); check product and service too, since its on-time orders are also rated lower; set a deadline and review |
| 3 Slightly above platform, high volume (132 sellers) | Second | Start with the Tier 3 sellers in the top 20; find the cause, then monitor monthly. Sellers with no excess late handovers need no action |
| 2 Occasionally late (236 sellers) | Routine | Automatic reminder when the late rate is above the same-month platform rate |
| 1 Rarely late (383 sellers) | None | — |
| Fewer than 20 orders (2,139 sellers) | Simple rule | Reminder after a set number of late handovers (97 small sellers have at least 3, 175 have at least 2; threshold to decide) |

- **Keep the tiers current.** Re-score sellers each period (for example the last 6 months) with the tier boundaries from this analysis, and take stronger action only after a seller stays in a high tier for two periods in a row.
- **How to state the value.** Seller-controlled late handovers are concentrated in few sellers, so the platform can cover most of them at low management cost. Do not claim large gains in customer satisfaction.
