# AI-Use Appendix

**Read this before writing Appendix A of the report.** It collects the AI-use records from the project notebooks in one place, so the report writer can merge them with everyone else's records.

| Part | Notebook | Tools |
| --- | --- | --- |
| 1 | `notebooks/01_cleaning.ipynb` (data cleaning and merge) | ChatGPT, Claude |
| 2 | `notebooks/02_descriptive_analysis.ipynb` (Q1 descriptive analysis) | Claude |
| 3 | `read-me-first/pass-over-to-clustering.md` (review ratings for the Q2 clusters) | Claude |
| 4 | `notebooks/03_q2.ipynb`, `notebooks/04_checks.ipynb`, `notebooks/q2_tiers.py` (Q2 seller tiers and credibility checks) | Claude |

Contributor: [name]. The text for Parts 1 and 2 also appears at the end of each notebook; if you change one, change both. Parts 3 and 4 appear only here.

## Part 1. Data cleaning and merge (`01_cleaning.ipynb`)

I used ChatGPT to draft and revise pandas code for the first version of this notebook (A.1–A.4), and Claude (Anthropic) to review that version against the raw data and rebuild it (A.5). The prompts below document how the notebook developed in stages.

### A.1 Order data validation and cleaning

> Please write a python code to check the values in `order_id` column in the `orders` dataset are unique and complete, so the existing records can be retained.

> write a python code to standardize the time format. Convert the order placement time (`order_purchase_timestamp`) and the actual delivery time (`order_delivered_carrier_date`) to a date-time format. Both them in the order dataset. The order placement time will later be used for month-to-month comparisons.

> please write a code to check the Missing and Abnormal Values for three columns: **order_purchase_timestamp**, **order_delivered_carrier_date**, **order_purchase_month**

> Write the code to clean the `order_status` column in my existing `orders` DataFrame using pandas. The previous already check order IDs, parse purchase and carrier handover timestamps, and flag timestamp issues. Continue from the current `orders` DataFrame.

> Then Convert `order_status` to pandas’ nullable string type, strip leading and trailing whitespace, convert values to lowercase, and treat empty strings as missing. Display a summary table with the order count and percentage for each status, including missing values. Use all rows in `orders` as the denominator, and keep every order for later analysis.

In the final analysis, I used `order_delivered_carrier_date` as the **carrier handover timestamp**.

### A.2 Order–seller table and merge

> Firstly, copy `order_id`, `seller_id`, and `shipping_limit_date` from `order_items`. Preserve the original DataFrame. Then treat both ID columns as strings, trim whitespace, and check for missing or blank IDs. Report any affected rows before grouping. Finally, convert `shipping_limit_date` to a datetime column and report how many values were originally missing and how many failed to parse.

> Please write code to check whether any `order_id` and `seller_id` pair has conflicting shipping deadlines. If any conflicts exist, display the affected pairs and stop so I can review them. Otherwise, collapse repeated item rows to one row per `order_id`and `seller_id`, preserving the available deadline.

> Add `seller_count` for the number of distinct sellers per order and `is_multi_seller_order` to flag orders with more than one seller. Keep those orders available for later analysis.

> Save the result as `seller_orders`, verify that `order_id` and `seller_id` are unique as a pair, and print the original item row count, final seller-order row count, and number of distinct multi-seller orders.

> Write the code using pandas. I already have `orders`, with parsed purchase and carrier handover timestamps, and `seller_orders`, with one row per `order_id` and `seller_id`, a parsed `shipping_limit_date`, and an `is_multi_seller_order` flag. Please left join `seller_orders` to `orders` on `order_id`. Validate the merge as many-to-one. Report the row count before and after the merge and the number of unmatched rows. Verify that each `order_id` and `seller_id` pair remains unique.

> could u rename the merge dataset as `merged_orders`

### A.3 Late handover eligibility and seller summary

> write a code to add flags for missing handover timestamps and for handover timestamps earlier than the purchase timestamp. Preserve the original timestamps. Then Create `analysis_orders` from single-seller orders and add an `eligible_for_late_rate` flag that requires a valid purchase timestamp, carrier handover timestamp, and shipping deadline, with handover at or after purchase. Create `late_handover` as a nullable Boolean. Finally, set it to `True` when an eligible order was handed over after its shipping deadline, `False` when it was handed over on or before the deadline, and `pd.NA` when eligibility requirements are not met.

> It has bug. I write a code to add before your code. timestamp_columns = [
>     "order_purchase_timestamp",
>     "order_delivered_carrier_date",
>     "shipping_limit_date",
> ]
>
> for column in timestamp_columns:
>     merged_orders[column] = pd.to_datetime(
>         merged_orders[column], errors="raise"
>     )

> Write the next Jupyter Notebook cell using pandas. I already have `analysis_orders`, with one row per single-seller order and the columns `seller_id`, `order_id`, `eligible_for_late_rate`, and `late_handover`. The nullable Boolean column `late_handover` is `True` for late, `False` for on time, and `pd.NA` for unknown.

> Group by `seller_id` and save the result as `seller_summary`, with one row per seller. Calculate `order_volume` from all rows, `eligible_orders` from rows eligible for the late rate, `late_orders` from rows marked `True`, and `late_rate` as `late_orders / eligible_orders`. Leave `late_rate` missing when `eligible_orders` is zero.

> Verify that the totals across sellers and Display the top 10 sellers by late order count

### A.4 Monthly benchmarks and seller comparisons

> I already have `analysis_orders`, with one row per single-seller order and the columns `seller_id`, `order_purchase_month`, `eligible_for_late_rate`, and `late_handover`. please calculate the overall and monthly late handover rates across the single-seller analysis sample. For each month, divide the total number of late orders by the total number of eligible orders in that month. Then calculate the same counts and rates by seller and month, and merge the monthly benchmark onto the seller-month table. Save the result as `seller_monthly_summary`.

In my next message, I shared the revised notebook cell and asked ChatGPT to use it going forward. The excerpt below shows the change I made before grouping by month.

> It has bug. so I rewrite the code. Now it becomes
>
> ```python
> analysis_orders["order_purchase_month"] = pd.to_datetime(
>     analysis_orders["order_purchase_timestamp"],
>     errors="raise",
> ).dt.to_period("M")
> ```
>
> […] please remember it

> Then add a column for the seller's late rate minus the monthly benchmark, expressed in percentage points. Leave rates missing when the eligible order count is zero. Keep the eligible order count visible so I can interpret results based on small samples. Display the monthly benchmark table and a preview of `seller_monthly_summary`.

### A.5 Data review and rebuild with Claude

- **Review:** I had Claude review our project proposal slides and all of our CSV files, and based on those, check the data cleaning and merging code I had written earlier. Claude pointed out several issues: missing handover timestamps; undelivered orders being included in the late handover rate; out-of-order timestamps; shipping deadlines in 2020; too little data for 2016 and for September–October 2018; and a total sample size that did not match the 93,859 orders in the proposal.
- **Decision-making:** For each issue, Claude provided recommendations, but I made the final decision. I decided to exclude undelivered orders and orders with out-of-order timestamps (without filling in missing values); keep the group B orders for a credibility check; exclude orders with deadlines in 2020; exclude 2016 data; define late handover by date; and leave the minimum-order threshold to the clustering team. Every decision, its rationale and the code used to identify each issue are documented in `notebooks/change.markdown`.
- **Rebuild:** I used Claude to rewrite the cleaning notebook based on `change.markdown`. I also used Claude to change how the data is loaded, so the raw data now loads from our GitHub repository and the cleaned files are saved to the `Data/Clean/` directory.

## Part 2. Q1 descriptive analysis (`02_descriptive_analysis.ipynb`)

I used Claude (Anthropic) to plan and build this notebook.

- **Planning:** Based on the two files, `seller_metrics.csv` and `monthly_benchmark.csv`, Claude offered me some suggestions. I then worked with Claude to confirm, one by one, that these charts met our requirements and aligned with our ideas. Finally, I documented these proposals in the `notebooks/descriptive_analysis.markdown` file.
- **Decision-making:** Claude provided recommendations, but I made the final decisions, and in several places I changed its suggestions:
  - Claude suggested applying a minimum-order threshold to all seller-level charts. I proposed instead to show sellers without a threshold and use a chart to explain why a threshold may be needed, and asked that the notebook explain why some charts use the threshold and others do not.
  - For the headline numbers, Claude suggested choosing between the share of sellers never late across all sellers (64%) and the share among sellers with at least 20 orders (32%). I decided to show both side by side, so the contrast itself explains the threshold.
  - Where two charts suited the same point, such as the Pareto chart, I decided to produce both and let the PPT role choose.
  - Claude first planned to save the tables behind the charts as separate CSV files. I asked instead for each table to be shown inside the notebook before its chart, so readers can see exactly which data each chart is drawn from.
- **Build:** I used Claude to write this notebook based on `descriptive_analysis.markdown`, and to save the charts to the `figures/` directory.

## Part 3. Review ratings for the clusters (Q2)

- **Planning:** I wanted to add customer review ratings to our analysis, to see whether the clusters differ in customer satisfaction. I discussed this with Claude, and we compared our existing three clusters with review ratings. The high-late cluster had clearly lower ratings, and late orders scored lower than on-time orders in every cluster.
- **Decision-making:** While preparing the ratings, Claude found that some orders have more than one review, so we discussed which rating to keep. Claude suggested keeping only the latest review. I asked Claude to rerun the analysis with the earliest review as well, and the results were practically the same. I then decided to keep two ratings, the earliest and the latest review, and to let the clustering team compare them and choose which one to use.
- **Documentation:** I used Claude to write the "Review ratings" section of `read-me-first/pass-over-to-clustering.md`, including the code that builds both ratings and a summary of the findings so far.

## Part 4. Q2 seller tiers and credibility checks (`03_q2.ipynb`, `04_checks.ipynb`, `q2_tiers.py`)

Contributor: Rui. I used Claude (Anthropic) to plan, build and check the Q2 analysis, and to write the Q2 hand-over notes (`pass-over-to-ppt.md`, Q2 section; `pass-over-to-report.md`).

- **Planning:** Claude first checked the cleaned data and the date-based definition of late handover against the raw data, then drafted a pipeline: put sellers into tiers with K-means, describe each tier with review ratings, choose the tiers managers should focus on, and rank the sellers inside them.
- **Decision-making:** Claude offered options, but I made the final decisions:
  - I kept K-means and used it to set the tier boundaries, rather than switching to a more complex method.
  - After the pass-over suggested replacing log(order volume) with log(1 + late orders), I had Claude explain the change and rebuild the analysis with it, because Q2 asks about the scale of late handovers.
  - I asked Claude to test product category and other features; none of them gave clearer groups, so the features stayed as they were.
  - I asked for the tiers to be compared with review ratings, and decided to use ratings only to describe the tiers.
  - I asked whether a seller's tier is fixed; Claude added the tier-movement table (check 6b), and we describe the tiers as a snapshot of one period.
  - About 20 large Tier 3 sellers are not worse than the platform. I decided to keep them in the focus tiers with a note, because the ranking already puts them last.
- **What the tool got wrong and how it was caught:**
  - When I looked at the first scatter plot, I saw that K-means was cutting one continuous cloud of sellers into groups, although Claude had presented the groups as real. Claude then compared the silhouette score with a baseline that has no groups. The review below showed that its first baselines were not a fair comparison and made the groups look real; with a fair baseline, the real data scores no higher, so we describe the result as tiers on one lateness scale.
  - I asked Claude to review the whole analysis from start to finish three times. This found further errors: the significance test did not allow for late handovers bunching in some months (allowing for it reduced the sellers worse than chance from 85 to 74); a correlation was reported as 0.90, which is the Spearman value (the Pearson value is 0.68); and the claim that higher tiers get lower ratings even on on-time orders holds only for Tier 4 once product category is held fixed.
  - I asked Claude to apply five review points to the write-up: the Tier 3 name, the denominators of percentages, wording that implied cause, sellers with fewer than 20 orders, and the role of K-means.
- **Build:** Claude wrote the notebooks, the shared functions in `q2_tiers.py`, the figures and the hand-over notes. I went through each part with Claude until I understood it, and checked the results before they were shared with the group.
