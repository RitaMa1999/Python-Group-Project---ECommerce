# Cleaning Changes for `01_cleaning.ipynb`

Decisions agreed for the cleaning and merge notebook. Each item records the problem, how we found it, the decision and how to apply it. The "How we found it" code can go into the notebook's data audit section; the expected numbers come from the raw data and should match what the notebook prints. These changes are applied in `notebooks/01_cleaning.ipynb` (previously `Project_Reviewed.ipynb`).

## Agreed changes

### 1. Missing carrier handover timestamp and non-delivered orders

**Problem.** 1,783 orders (1.79%) have no carrier handover timestamp, so late handover cannot be determined for them.

| Order status | Orders missing the handover timestamp |
|---|---|
| canceled | 550 |
| unavailable | 609 |
| invoiced | 314 |
| processing | 301 |
| created / approved | 7 |
| delivered | 2 |

**How we found it.** Count the missing handover timestamps, then break them down by order status. Run this on `orders` after loading the raw CSVs.

```python
date_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
]
orders[date_columns] = orders[date_columns].apply(pd.to_datetime)

missing_handover = orders["order_delivered_carrier_date"].isna()
print(f"Orders missing a handover timestamp: {missing_handover.sum():,} "
      f"({missing_handover.mean():.2%})")
display(
    orders.loc[missing_handover, "order_status"]
    .value_counts()
    .rename("orders_missing_handover")
    .to_frame()
)
```

Expected output: 1,783 orders (1.79%), matching the status table above. The breakdown shows that almost all of them were never delivered, which is what led to the decision.

**Related problem: non-delivered orders that do have a handover timestamp.** The current notebook keeps every order status, so 1,178 non-delivered orders in the single-seller sample count toward the late rate:

| Order status | Orders with a handover timestamp (all orders) | In the notebook's late rate (single-seller sample) |
|---|---|---|
| shipped | 1,107 | 1,103 |
| canceled | 75 | 75 |

**How we found it.** Cross-tabulate order status against whether the handover timestamp is present. This also confirms the status table above.

```python
display(
    pd.crosstab(
        orders["order_status"],
        orders["order_delivered_carrier_date"].notna().rename("has_handover_timestamp"),
    )
)
```

Expected output: `shipped` has 1,107 orders with a handover timestamp and 0 without; `canceled` has 75 with and 550 without; `delivered` has 96,476 with and 2 without.

**Decision.** Drop these orders. Do not impute the timestamp. Keep only delivered orders, which also removes the shipped and canceled orders that have a handover timestamp.

**Why.**
- 1,781 of the 1,783 orders were never delivered, so they were never handed to a carrier and have no handover outcome to measure. The delivered-only status filter in the proposal removes them.
- Only 2 delivered orders are missing the timestamp. Dropping them has no material effect on a sample of about 94,000 orders.
- The handover timestamp is the variable that defines late handover. Filling it with a mean, the deadline or any other value would invent an outcome for the seller and bias the late rate.
- **Shipped orders:** these are still in transit and have no final outcome yet. The proposal's sample uses delivered orders only.
- **Canceled orders with a handover timestamp:** they were handed to the carrier and then canceled, which is a different process from a normal order. Including them would make the comparison between sellers unfair.

**How to apply.**
- Keep only orders with `order_status == "delivered"`.
- Then drop any remaining rows where `order_delivered_carrier_date` is missing.
- Print how many rows each step removes so the counts can be quoted in the report.

**Report wording (Data section).**
> 1,783 orders had no carrier handover timestamp. 1,781 of them were not delivered and were removed by the delivered-status filter; the remaining 2 delivered orders were dropped. Missing timestamps were not imputed. We also excluded shipped orders, which were still in transit, and canceled orders, so every order in the sample has a final delivered outcome.

**Limitation to mention.** Some orders may have been canceled because the seller never shipped them. Dropping them can make those sellers look better than they are. Optionally, report each seller's cancellation rate as a supplementary measure.

### 2. Timestamps in the wrong order

**Problem.** Some orders have timestamps that are out of order:

| Check | Orders |
|---|---|
| Handover before purchase (`order_delivered_carrier_date` < `order_purchase_timestamp`) | 166 |
| Handover before payment approval (`order_delivered_carrier_date` < `order_approved_at`) | 1,359 |
| Customer delivery before handover (`order_delivered_customer_date` < `order_delivered_carrier_date`) | 23 |

The current notebook does not drop the handover-before-purchase orders. It flags them (`handover_before_purchase`) and marks them ineligible (`handover.ge(purchase)` in `eligible`), so they are left out of the late rate but still counted in `order_volume` as `unknown_orders`. The other two checks are missing.

**How we found it.** Three steps: compare each pair of timestamps across all orders, repeat inside the delivered, single-seller sample to split the handover-before-approval orders into groups, then measure group B's gap. This continues from the change 1 code (`date_columns` already parsed).

Step 1: count out-of-order timestamps across all 99,441 orders.

```python
purchase, approved, handover, customer = (orders[c] for c in date_columns)

order_checks = pd.Series({
    "Handover before purchase": handover.lt(purchase).sum(),
    "Handover before payment approval": handover.lt(approved).sum(),
    "Customer delivery before handover": customer.lt(handover).sum(),
}, name="orders")
display(order_checks.to_frame())
```

Expected output: 166, 1,359 and 23 (the problem table above).

Step 2: restrict to delivered, single-seller orders and break the failures down.

```python
seller_count = order_items.groupby("order_id")["seller_id"].nunique()
single_seller_ids = seller_count.index[seller_count.eq(1)]
sample = orders.loc[
    orders["order_id"].isin(single_seller_ids)
    & orders["order_status"].eq("delivered")
].copy()
print(f"Delivered, single-seller orders: {len(sample):,}")

purchase, approved, handover, customer = (sample[c] for c in date_columns)
any_missing = sample[date_columns].isna().any(axis=1)
group_a = ~any_missing & handover.lt(purchase)
group_b = ~any_missing & handover.ge(purchase) & handover.lt(approved)
customer_before_handover = ~any_missing & customer.lt(handover)

breakdown = pd.Series({
    "Any of the four timestamps missing": any_missing.sum(),
    "Group A: handover before purchase": group_a.sum(),
    "Group B: handover after purchase, before approval": group_b.sum(),
    "Customer delivery before handover": customer_before_handover.sum(),
}, name="orders")
display(breakdown.to_frame())

failed = any_missing | group_a | group_b | customer_before_handover
print(f"Orders remaining: {(~failed).sum():,}")
```

Expected output: 95,203 delivered, single-seller orders; 23, 161, 1,156 and 4 failures; 93,859 remaining.

Step 3: measure how far group B handovers come before approval. This is what showed that group B looks like late approval records rather than errors.

```python
gap_hours = (approved - handover)[group_b].dt.total_seconds().div(3600)
display(gap_hours.describe(percentiles=[0.5, 0.9, 0.99]).round(1))
```

Expected output: median about 20 hours, 90th percentile about 55 hours, 99th percentile about 166 hours (7 days), maximum about 225 hours (9 days).

**Decision.** Drop all orders that fail the order check: purchase ≤ approval ≤ handover ≤ customer delivery. Do this in the cleaning step, not by flagging.

**Why.**
- **The data is impossible.** An order cannot be handed to the carrier before it was placed. If one timestamp is wrong, the other timestamps for that order cannot be trusted either, so the whole order is unreliable for judging the seller.
- **The effect is small.** The 166 handover-before-purchase orders are about 0.17% of orders and will not change the conclusions.
- **It is simpler than flagging and keeping.** Keeping these orders makes `order_volume` and `eligible_orders` two different numbers that later notebooks and the report have to explain. Dropping them leaves one order count per seller.
- **It matches the proposal.** The proposal requires complete timestamps in the correct order. Applying the full order check together with the delivered filter (change 1) gives exactly 93,859 orders.

**Split the handover-before-approval orders into two groups.** In the delivered, single-seller sample, 1,317 orders were handed over before payment approval. They fall into two groups that need different treatment:

| Group | Orders | What it most likely is | Main analysis | `04_checks` |
|---|---|---|---|---|
| A. Handover also before purchase | 161 | Data error: an order cannot ship before it is placed | Drop | Drop |
| B. Handover after purchase but before approval | 1,156 | Possibly real: the seller shipped while approval was recorded late. Median gap about 20 hours; 90% within about 55 hours; 99% within 7 days | Drop | **Keep** |

Group B is dropped in the main analysis so the rule "timestamps in the correct order" stays consistent and the sample matches the proposal. Because many of these orders may be genuine approval delays, `04_checks` reruns the analysis with group B kept and compares the results.

**How to apply.**
- After the delivered filter, keep only orders where `order_purchase_timestamp <= order_approved_at <= order_delivered_carrier_date <= order_delivered_customer_date`, with all four timestamps present.
- Before dropping, identify group B (handover at or after purchase, before approval, customer delivery at or after handover). Save two order-level files, so `04_checks` can add group B back without redoing the cleaning and the main analysis cannot pick up group B by mistake:
  - `Data/Clean/orders_main.csv`: the main sample, orders that pass every check (93,598 orders after change 4). All main analysis reads this file.
  - `Data/Clean/orders_group_b.csv`: the 1,156 group B orders, with the same columns. Only `04_checks` reads this file.
- Record both files in the README and in the notebook's handoff section (see **Documentation to update** at the end of this file).
- Print how many rows each check removes so the counts can be quoted in the report.
- Remove the old `handover_before_purchase` flag and the `handover.ge(purchase)` condition from `eligible`, since these rows are already gone.
- Write the `04_checks` reminder into the notebook's **Handoff to the clustering team** section (see below).

**`04_checks` test.**
1. Main sample: 93,598 orders after change 4 (group B dropped).
2. Check sample: main sample plus the 1,156 group B orders (94,754 orders).
3. Compare the platform late rate, each seller's late rate, the chosen k, the cluster sizes and profiles, and how many sellers change cluster.
4. If the results are similar, the report can say this filter does not affect the conclusions. If they differ, report both and explain which one the recommendations rely on.

**Text to add to the notebook's handoff section.**
> **Credibility check for `04_checks`: handover before payment approval.** The main sample drops 1,156 orders that were handed over after purchase but before payment approval (saved separately as `Data/Clean/orders_group_b.csv`; the main sample is `Data/Clean/orders_main.csv`). These may be approval delays rather than data errors. In `04_checks`, combine the two files, rerun the seller metrics and K-means, then compare the platform late rate, seller late rates, k, cluster sizes and profiles, and the number of sellers that change cluster. If the results are similar, state in the report that this filter does not affect the conclusions. The 161 orders handed over before purchase stay dropped in both versions.

**Report wording (Data section).**
> We kept only orders whose timestamps were complete and in a plausible order (purchase, then payment approval, then carrier handover, then customer delivery). In the delivered, single-seller sample this removed 23 orders with a missing timestamp, 161 handed over before purchase, 1,156 handed over after purchase but before payment approval, and 4 delivered to the customer before handover, leaving 93,859 orders. Because the 1,156 orders may reflect late approval records rather than errors, we tested adding them back in the credibility checks.

Confirm these counts against what the notebook prints before using them in the report.

**Counts in the delivered, single-seller sample (95,203 orders).**

| Step | Orders removed |
|---|---|
| Any of the four timestamps missing | 23 |
| Group A: handover before purchase | 161 |
| Group B: handover after purchase, before approval | 1,156 |
| Customer delivery before handover | 4 |
| **Remaining** | **93,859** |

### 3. Shipping deadline years after purchase (`shipping_limit_date` in 2020)

**Problem.** 4 item rows have a `shipping_limit_date` in 2020, more than 1,000 days after purchase. The data ends in October 2018, and deadlines are normally 2–18 days after payment approval (median 6 days).

| Order | Status | Purchase | Deadline | Days after purchase |
|---|---|---|---|---|
| `13bdf405…` | canceled | 2017-03-16 | 2020-02-05 | 1,056 |
| `9c94a4ea…` | shipped | 2017-03-14 | 2020-02-03 | 1,056 |
| `c2bb89b5…` (2 items) | delivered | 2017-05-23 | 2020-04-09 | 1,052 |

- The 4 rows are 3 orders, all from one seller (`7a241947449cc45dbfda4f9d0798d9d0`). That seller's other 68 item rows have normal deadlines of 3–12 days (median 6).
- The canceled and shipped orders are already removed by the delivered filter (change 1). Only `c2bb89b5…` is in the main sample.
- That order was handed over 5 days after approval, so it would be on time under the seller's usual 6-day deadline as well. Dropping it does not change any late count.

A separate group is **not** a problem: 235 item rows (185 orders in the main sample) have a deadline 30–148 days after purchase, mostly 30–50 days (median 36). The values form a continuous range and look like real long lead times, such as pre-orders or made-to-order products. 16 of the 185 orders were late.

**How we found it.** Merge the item deadlines with the order purchase time, look at the deadline years and the number of days from purchase to deadline, then compare the affected seller with its other orders. This continues from the change 1 code (`date_columns` already parsed).

```python
order_items["shipping_limit_date"] = pd.to_datetime(order_items["shipping_limit_date"])

item_deadlines = order_items.merge(
    orders[["order_id", "order_status", "order_purchase_timestamp"]],
    on="order_id",
    how="left",
    validate="many_to_one",
)
item_deadlines["days_to_deadline"] = (
    item_deadlines["shipping_limit_date"]
    .sub(item_deadlines["order_purchase_timestamp"])
    .dt.total_seconds()
    .div(86400)
)

# Deadline years and days from purchase to deadline.
display(item_deadlines["shipping_limit_date"].dt.year.value_counts().sort_index())
display(item_deadlines["days_to_deadline"].describe(percentiles=[0.5, 0.99]).round(1))

# Deadlines more than a year after purchase.
far_deadline = item_deadlines["days_to_deadline"].gt(365)
display(
    item_deadlines.loc[
        far_deadline,
        ["order_id", "seller_id", "order_status", "order_purchase_timestamp",
         "shipping_limit_date", "days_to_deadline"],
    ]
)

# The same seller's other deadlines.
affected_sellers = item_deadlines.loc[far_deadline, "seller_id"].unique()
display(
    item_deadlines.loc[
        item_deadlines["seller_id"].isin(affected_sellers) & ~far_deadline,
        "days_to_deadline",
    ].describe().round(1)
)

# Long but plausible deadlines, kept.
long_deadline = item_deadlines["days_to_deadline"].between(30, 365)
print(f"Item rows with a deadline 30-365 days after purchase: {long_deadline.sum():,}")
display(item_deadlines.loc[long_deadline, "days_to_deadline"].describe(percentiles=[0.5, 0.9]).round(1))
```

Expected output:
- Deadline years: 2016 = 370, 2017 = 49,765, 2018 = 62,511, 2020 = 4.
- Days to deadline: median 6.0, 99th percentile 19.0, maximum 1,056.
- 4 rows more than a year after purchase, all from seller `7a241947…`.
- That seller's other 68 rows: 3–12 days, median 6.
- 235 rows with a deadline 30–365 days after purchase: median 36 days, maximum 148.

**Decision.**
- **Drop** orders with a deadline more than 365 days after purchase. In the main sample this is 1 order (`c2bb89b5…`).
- **Keep** orders with a deadline 30–365 days after purchase.

**Why.**
- **Drop the 2020 deadlines.** A deadline more than 1,000 days after purchase, and after the data ends, is clearly an entry error such as a wrong year. The deadline is the other variable that defines late handover. Replacing it, for example with approval plus 6 days, would invent a deadline for the seller, the same reason we do not impute handover timestamps (change 1).
- **The effect is negligible.** One order out of about 94,000 is dropped, and the seller keeps 55 orders in the main sample. The order would be on time under a normal deadline, so no late count changes.
- **Keep the 30–148 day deadlines.** They are a continuous range, not isolated extreme values, and match real long lead times. There is no evidence-based cutoff; removing them at an arbitrary threshold would be harder to justify than keeping them.
- **Why 365 days.** No deadline falls between 148 and 1,052 days, so any cutoff in that gap gives the same result. One year is easy to explain and does not depend on the year 2020 specifically.

**How to apply.**
- When building the seller-order table from `order_items`, compute days from purchase to `shipping_limit_date` and drop orders where any item's deadline is more than 365 days after purchase. Drop the whole order, not just the item row, so the order is not left with only some of its items.
- Print how many orders this removes, overall and in the main sample.
- After this change the main sample (`Data/Clean/orders_main.csv`) is 93,858 orders; `Data/Clean/orders_group_b.csv` stays at 1,156. Update any expected counts in the notebook.

**Report wording (Data section).**
> Three orders from one seller had a shipping deadline more than 1,000 days after purchase, which we treated as an entry error. One of them was in our delivered, single-seller sample and was dropped, leaving 93,858 orders. We did not replace the deadline, because doing so would assign the seller a deadline that was never recorded. 185 orders with long but plausible deadlines (30–148 days after purchase) were kept.

**Limitation to mention.** 185 orders have deadlines of 30 days or more, which makes late handover less likely for them. Sellers with many such orders may look more punctual than sellers with short deadlines.

### 4. Study period: 2016 orders and September–October 2018

**Problem.** The first and last months of the data are very thin. The proposal's coverage is September 2016 to October 2018.

| Month | All orders | Delivered | Main sample after changes 1–3 | Late rate in main sample |
|---|---|---|---|---|
| 2016-09 | 4 | 1 | 1 | 100% |
| 2016-10 | 324 | 265 | 258 | 48.1% |
| 2016-11 | 0 | 0 | 0 | — |
| 2016-12 | 1 | 1 | 1 | 0% |
| 2018-09 | 16 | 0 | 0 | — |
| 2018-10 | 4 | 0 | 0 | — |

For comparison, the platform late rate from 2017 onward is about 9%.

- **September–October 2018:** all 20 orders are canceled (19) or shipped (1). None is delivered, so the delivered filter in change 1 already removes them. The old notebook kept every status, which is why 2018-09 appeared in its monthly benchmark. The last order in the main sample was placed on 2018-08-29.
- **2016:** 260 orders from 126 sellers, with a 48% late rate. 23 of these sellers have no orders after 2016.
- The high 2016 late rate comes from the platform's launch period rather than individual sellers. In 2016 the median deadline was 4 days after approval (6 days later), but the median handover took 8.9 days after approval (1.8 days later).

**How we found it.** Cross-tabulate the edge months by order status, then rebuild the main sample from changes 1–3 and compare months, processing times and late rates. This continues from the change 2 code (`sample`, `failed`) and the change 3 code (`item_deadlines`, `far_deadline`).

```python
purchase_month = orders["order_purchase_timestamp"].dt.to_period("M")
edge_months = (
    purchase_month.dt.year.eq(2016)
    | purchase_month.isin(pd.PeriodIndex(["2018-09", "2018-10"], freq="M"))
)
display(pd.crosstab(purchase_month[edge_months], orders.loc[edge_months, "order_status"]))

far_order_ids = item_deadlines.loc[far_deadline, "order_id"].unique()
order_seller_deadlines = (
    order_items.groupby("order_id", as_index=False)
    .agg(seller_id=("seller_id", "first"), shipping_limit_date=("shipping_limit_date", "first"))
)
main_sample = (
    sample.loc[~failed & ~sample["order_id"].isin(far_order_ids)]
    .merge(order_seller_deadlines, on="order_id", how="left", validate="one_to_one")
)
main_sample["order_purchase_month"] = main_sample["order_purchase_timestamp"].dt.to_period("M")
main_sample["late_handover"] = (
    main_sample["order_delivered_carrier_date"].gt(main_sample["shipping_limit_date"])
)
print(f"Main sample after changes 1-3: {len(main_sample):,}")

monthly = main_sample.groupby("order_purchase_month").agg(
    orders=("order_id", "size"),
    sellers=("seller_id", "nunique"),
    late_rate=("late_handover", "mean"),
)
display(monthly.round(3))

is_2016 = main_sample["order_purchase_month"].dt.year.eq(2016)
days = lambda later, earlier: (
    main_sample[later].sub(main_sample[earlier]).dt.total_seconds().div(86400)
)
process = pd.DataFrame({
    "approval_to_deadline_days": days("shipping_limit_date", "order_approved_at"),
    "approval_to_handover_days": days("order_delivered_carrier_date", "order_approved_at"),
}).groupby(is_2016.map({True: "2016", False: "2017-2018"})).median()
display(process.round(1))

sellers_2016 = set(main_sample.loc[is_2016, "seller_id"])
sellers_later = set(main_sample.loc[~is_2016, "seller_id"])
print(f"Sellers with 2016 orders: {len(sellers_2016)}; only in 2016: {len(sellers_2016 - sellers_later)}")
print(f"Platform late rate with 2016: {main_sample['late_handover'].mean():.2%}; "
      f"without 2016: {main_sample.loc[~is_2016, 'late_handover'].mean():.2%}")
print(f"Orders without 2016: {(~is_2016).sum():,}")
```

Expected output:
- Edge months by status: 2018-09 has 15 canceled and 1 shipped; 2018-10 has 4 canceled; no delivered orders in either month.
- Main sample after changes 1–3: 93,858 orders. 2016-09: 1 order, 2016-10: 258 orders from 125 sellers (48.1% late), 2016-12: 1 order; no 2016-11, 2018-09 or 2018-10.
- Median days after approval: 2016 deadline 4.0, handover 8.9; 2017–2018 deadline 6.0, handover 1.8.
- 126 sellers with 2016 orders, 23 only in 2016.
- Platform late rate 9.21% with 2016, 9.10% without; 93,598 orders without 2016.

**Decision.**
- **Drop all 2016 orders** from the main analysis. The study period becomes **January 2017 to August 2018** (20 months).
- **September–October 2018:** no extra step. Change 1 already removes these orders.
- **Keep January–February 2017**, although their late rates are high (22.0% and 17.3%).

**Why.**
- **2016 is the platform's launch period, not normal seller behavior.** Deadlines were shorter and handovers much slower across the platform, which is a platform-wide process issue. Including it would make sellers active in 2016 look worse for reasons outside their control.
- **The 2016 data has gaps.** November 2016 has no orders, and September and December have 1 order each. A same-month benchmark based on 1 order is meaningless.
- **It matches the 2017 → 2018 holdout.** The credibility check already uses only 2017 and 2018. Starting the main analysis in January 2017 puts both on the same period.
- **The effect matters for some sellers, so it has to be decided.** Among sellers with at least 20 orders, 14 sellers' late rates change by more than 2 percentage points (maximum 6.9), and 23 sellers drop out entirely.
- **Why keep January–February 2017.** They still have 744 and 1,628 orders, enough for a reliable monthly benchmark, and the same-month comparison adjusts for their higher platform-wide rate.

**How to apply.**
- After changes 1–3, drop orders whose `order_purchase_timestamp` is in 2016. Apply it to both `Data/Clean/orders_main.csv` and `Data/Clean/orders_group_b.csv`, so `04_checks` uses the same period.
- Print how many orders and sellers this removes.
- After this change `Data/Clean/orders_main.csv` has **93,598 orders** and `Data/Clean/orders_group_b.csv` has **1,156 orders** (group B has no 2016 orders). Together they make the 94,754-order check sample.
- The monthly benchmark table should run from 2017-01 to 2018-08 with no empty or 1-order months.

**Report wording (Data section).**
> The data covers September 2016 to October 2018, but we restricted the analysis to orders placed from January 2017 to August 2018. 2016 was the platform's launch period: it had only 260 delivered orders in our sample, no orders in November, and a late handover rate of 48% compared with about 9% afterwards, driven by platform-wide slower handovers and shorter deadlines. September and October 2018 contained no delivered orders. The final sample has 93,598 orders.

**Limitations to mention.**
- The data ends in October 2018. Orders placed in late August 2018 that were still in transit (47 shipped orders) are not in the sample. If those were slower, the August 2018 late rate may be slightly understated.
- January–February 2017 are still early months with higher platform-wide late rates. The same-month benchmark accounts for this, but raw seller late rates from those months are less comparable.

### 5. Orders with no items and orders with more than one seller

These two problems are already handled correctly by the current notebook. This change records them so the handling is documented and explained in the report.

**Problem.**
- **Orders with no item rows: 775.** They have no seller and no `shipping_limit_date`, so they cannot be assigned to a seller or judged late. None of them is delivered: unavailable 603, canceled 164, created 5, invoiced 2, shipped 1.
- **Orders with more than one seller: 1,278.** 1,219 have 2 sellers, 54 have 3, 3 have 4 and 2 have 5. Almost all are delivered (1,275), so excluding them removes real orders. The problem is that `orders` records one `order_delivered_carrier_date` per order, and `order_items` has no handover timestamp. When several sellers ship one order, we cannot tell which seller handed over late.

**How we found it.** Check which orders have item rows, count distinct sellers per order, and confirm that the handover timestamp exists only at the order level. Run this on `orders` and `order_items` after loading the raw CSVs.

```python
# Orders with no item rows.
has_items = orders["order_id"].isin(order_items["order_id"])
print(f"Orders with no item rows: {(~has_items).sum():,}")
display(orders.loc[~has_items, "order_status"].value_counts().rename("orders").to_frame())

# Orders with more than one seller.
sellers_per_order = order_items.groupby("order_id")["seller_id"].nunique()
multi_seller_ids = sellers_per_order.index[sellers_per_order.gt(1)]
print(f"Orders with more than one seller: {len(multi_seller_ids):,}")
display(
    orders.loc[orders["order_id"].isin(multi_seller_ids), "order_status"]
    .value_counts()
    .rename("orders")
    .to_frame()
)
display(sellers_per_order.value_counts().sort_index().rename("orders").to_frame())

# One handover timestamp per order, even when several sellers ship.
handover_columns = orders.columns[orders.columns.str.contains("carrier")]
print(f"Handover timestamp columns in orders: {list(handover_columns)}")
print(f"Handover timestamp columns in order_items: "
      f"{list(order_items.columns[order_items.columns.str.contains('carrier')])}")
```

Expected output:
- 775 orders with no item rows: unavailable 603, canceled 164, created 5, invoiced 2, shipped 1.
- 1,278 orders with more than one seller: delivered 1,275, shipped 2, unavailable 1.
- Sellers per order: 1 seller 97,388; 2 sellers 1,219; 3 sellers 54; 4 sellers 3; 5 sellers 2.
- `order_delivered_carrier_date` is the only handover column and is in `orders`; `order_items` has none.

**Decision.**
- **Orders with no items:** exclude. No extra step is needed.
- **Orders with more than one seller:** exclude from the main analysis. No sensitivity check with these orders.

**Why.**
- **Orders with no items** have no seller to attribute the order to. They are also all non-delivered, so change 1 would remove them anyway.
- **Multi-seller orders** cannot be attributed. With one handover timestamp per order, the same time would be credited to every seller in the order, and a late seller would make the punctual sellers in the same order look late.
- **The loss is small.** 1,278 orders are 1.3% of all orders.
- **No sensitivity check.** Including multi-seller orders would mean assigning a handover time to sellers who may not have shipped at that time, so the check would not test a credible alternative. The proposal does not require it, and the time is limited. The old notebook's optional `merged_orders` sensitivity analysis is dropped; `merged_orders` is no longer handed over.

**How to apply.**
- Keep the notebook's current approach: build the seller-order table from `order_items` and left join `orders` onto it, so orders with no items never enter. Keep only orders where `seller_count == 1`.
- Print the number of orders with no items and the number of multi-seller orders, so the counts can be quoted in the report.
- Remove the `merged_orders` row from the notebook's handoff table.

**Report wording (Data section).**
> Each order in the analysis must be attributable to one seller. 775 orders had no item records, and therefore no seller or shipping deadline; none of them had been delivered, and they were excluded. A further 1,278 orders (1.3%) contained items from more than one seller. Because the dataset records a single carrier handover time per order, a late handover in these orders cannot be attributed to a specific seller, so we excluded them and analysed single-seller orders only.

**Limitation to mention.** Excluding multi-seller orders removes 1,275 delivered orders. Sellers who often sell in multi-seller orders are represented by fewer orders, and their handover performance in those orders is unknown.

### 6. Late handover definition: by date, not by timestamp

**Problem.** The current notebook marks an order late when the handover timestamp is after the deadline timestamp, so handing over one minute late counts. Comparing dates instead gives a very different late rate.

| | By timestamp (current notebook) | By date (new) |
|---|---|---|
| Late when | Handover time is after the deadline time | Handover date is after the deadline date; handing over on the deadline day is on time |
| Platform late rate (main sample, 93,598 orders) | 9.10% | 5.78% |
| Late orders | 8,522 | 5,407 |

The 3,115 orders in between were all handed over on the deadline day, but after the deadline's clock time. They are 37% of the orders that are late by timestamp.

**How we found it.** Compute both definitions, count the orders late only by timestamp, then check where the deadline's clock time comes from and compare deadline hours with handover hours. This continues from the change 4 code (`main_sample` before the 2016 filter).

```python
main_sample = main_sample.loc[~main_sample["order_purchase_month"].dt.year.eq(2016)].copy()
handover = main_sample["order_delivered_carrier_date"]
deadline = main_sample["shipping_limit_date"]
approved = main_sample["order_approved_at"]

late_by_timestamp = handover.gt(deadline)
late_by_date = handover.dt.normalize().gt(deadline.dt.normalize())
same_day_only = late_by_timestamp & ~late_by_date

print(f"Orders: {len(main_sample):,}")
print(f"Late by timestamp: {late_by_timestamp.sum():,} ({late_by_timestamp.mean():.2%})")
print(f"Late by date: {late_by_date.sum():,} ({late_by_date.mean():.2%})")
print(f"Late by timestamp only, handed over on the deadline day: {same_day_only.sum():,} "
      f"({same_day_only.sum() / late_by_timestamp.sum():.0%} of timestamp-late orders)")

# Is the deadline's clock time just the approval time?
whole_days_after_approval = deadline.sub(approved).dt.total_seconds().mod(86400).eq(0)
same_clock_time = deadline.dt.strftime("%H:%M").eq(approved.dt.strftime("%H:%M"))
print(f"Deadline = approval + whole days: {whole_days_after_approval.mean():.0%}")
print(f"Deadline clock time = approval clock time (to the minute): {same_clock_time.mean():.0%}")

# When deadlines fall versus when handovers happen.
display(
    pd.DataFrame({
        "deadline_share": deadline.dt.hour.value_counts(normalize=True),
        "handover_share": handover.dt.hour.value_counts(normalize=True),
    })
    .sort_index()
    .round(3)
)
```

Expected output:
- 93,598 orders; 8,522 late by timestamp (9.10%); 5,407 late by date (5.78%); 3,115 late by timestamp only (37%).
- 80% of deadlines are exactly whole days after approval; 82% have the same clock time as approval, to the minute.
- Deadlines most often fall at 02:00 (7.3%) and 03:00 (5.7%), when almost no handovers happen (0.6% and 0.3%). Handovers peak at 14:00 (10.7%) and 15:00 (9.0%).

**Decision.** Define late handover by date: an order is late when it is handed to the carrier on a calendar day after the `shipping_limit_date` day.

**Why.**
- **The deadline's clock time is mechanical and has no business meaning.** 80% of deadlines are the payment approval time plus a whole number of days, and 82% have exactly the same clock time as approval. The time of day in the deadline is the moment the buyer's payment was approved, not a dispatch cut-off set by the platform.
- **That clock time is unfair to sellers.** The most common deadline hours are 2 a.m. and 3 a.m., because many payments are approved overnight, while handovers peak at 2–3 p.m., when carriers collect. By timestamp, an order with a 02:35 deadline is late if the seller hands it over that afternoon. That depends on when the buyer paid, not on how the seller performed.

**How to apply.**
- Compute `late_handover` as `order_delivered_carrier_date.dt.normalize() > shipping_limit_date.dt.normalize()`.
- Use this definition for the main sample, `seller_metrics.csv`, the monthly benchmark and all report and slide numbers.
- In `04_checks`, rerun with the timestamp definition (`order_delivered_carrier_date > shipping_limit_date`) as the alternative-definition check from the group plan. Compare the platform late rate, seller late rates, cluster profiles and which sellers end up in the high-priority group.
- Add this check to the notebook's handoff section (see **Documentation to update**).

**Report wording (Data section).**
> We define a late handover as an order handed to the carrier on a calendar day after its shipping limit date. We compare dates rather than exact times because the time of day in the shipping limit is mechanical: 80% of deadlines are exactly a whole number of days after payment approval, and 82% share the approval's clock time to the minute. Many deadlines therefore fall in the early morning (2–3 a.m. are the most common hours), while handovers peak in the afternoon. Under an exact-time rule, a seller who hands over an order during the afternoon of its deadline day would be counted late because of when the buyer's payment was approved. With this definition the platform late rate is 5.78%; with exact times it is 9.10%, which we test in the credibility checks.

**Text to add to the notebook's handoff section.**
> **Credibility check for `04_checks`: late handover definition.** The main analysis defines late handover by date (handed over on a day after the deadline day). In `04_checks`, rerun the seller metrics and K-means with the timestamp definition (handed over after the exact deadline time), then compare the platform late rate, seller late rates, cluster profiles and the sellers in the high-priority group.

### 7. Save the seller metrics and monthly benchmark as files

**Problem.** The notebook builds `seller_summary` (one row per seller) and `monthly_benchmark` (one row per month) but only keeps them in memory. Nothing is saved, so they disappear when the notebook closes. The group plan requires the data role to deliver `seller_metrics.csv` (orders, late orders and late rate per seller) and a monthly platform late-rate table by Tuesday evening, and every later notebook reads the same `seller_metrics.csv` instead of cleaning the data again. Without saved files, each person has to rerun the cleaning notebook, and small differences in steps or versions can make the numbers in the report, slides and code disagree.

The notebook also compares sellers with the same-month benchmark only at the seller-month level (`seller_monthly_summary`), so there is no seller-level benchmark for Q1 or clustering.

**How we found it.** Reading the notebook: no cell calls `to_csv`, and `late_rate_gap_pp` exists only in `seller_monthly_summary`, one row per seller and month.

**Decision.** Save two files from the main sample (`Data/Clean/orders_main.csv`, date definition from change 6), and add two same-month benchmark columns to the seller file.

| File | One row per | Columns | Rows |
|---|---|---|---|
| `Data/Clean/seller_metrics.csv` | Seller | `seller_id`, `order_volume`, `late_orders`, `late_rate`, `benchmark_late_rate`, `late_rate_gap_pp` | 2,917 |
| `Data/Clean/monthly_benchmark.csv` | Purchase month | `order_purchase_month`, `orders`, `late_orders`, `late_rate` | 20 (2017-01 to 2018-08) |

New columns:
- `benchmark_late_rate`: the late rate the seller would have if each of its orders were late at the platform rate for that order's month. It is the platform monthly rate averaged over the seller's orders, so months with more orders count more.
- `late_rate_gap_pp`: `late_rate` minus `benchmark_late_rate`, in percentage points. Positive means later than the platform in the same months.

**Why.**
- **One source for every number.** Q1, Q2, the figures, the report and the slides all read the same files, so their numbers agree.
- **It matches the group plan.** The plan names `seller_metrics.csv` and a monthly platform late-rate table as the data role's Tuesday deliverables.
- **A fair comparison for each seller.** Platform late rates range from 3.5% to 18.5% by month. A seller who sells mostly in high-rate months such as November or January would look worse on raw late rate alone. `late_rate_gap_pp` compares each seller with the platform in the months it actually sold, which is the same-month baseline in the analysis plan.

**Choices built into the files.**
- **No minimum-order threshold.** All 2,917 sellers are kept; the clustering team chooses the threshold (see **Left to the clustering team**).
- **Months saved as text** (`"2017-01"`). A pandas `Period` does not survive a round trip through CSV, so text keeps the format the same when the file is read back.
- **Rates saved as plain decimals from 0 to 1**, not nullable types, so scikit-learn can read them directly. Every seller has at least one order, so no rate is missing.
- **Late handover by date** (change 6).

**Who uses which file.**

| File | Used by | For |
|---|---|---|
| `seller_metrics.csv` | Analysis: Q1 (`02_q1`) | Distributions of order volume, late orders and late rate; comparison with the platform and same-month benchmark |
| | Analysis: Q2 (`03_q2`) | K-means input (late rate and log order volume) |
| | PPT (`05_figures`) | Q1 and Q2 figures |
| `monthly_benchmark.csv` | Analysis: Q1 | Same-month baseline |
| | PPT and report | Monthly platform trend figure and the overall numbers in the Data section |
| `orders_main.csv` | `04_checks`, 2017 → 2018 holdout | Rebuild seller metrics under other settings: timestamp definition, group B added back, separate years |
| `orders_group_b.csv` | `04_checks` only | Added to `orders_main.csv` for the group B check |

The two summary files are the agreed numbers for the main analysis. `orders_main.csv` is the order-level input for anything that needs different seller metrics.

**How to apply.** Add this at the end of the cleaning notebook, after `orders_main` is built and saved (changes 1–6). It replaces `seller_summary`, `monthly_benchmark`, `seller_monthly_summary` and the `eligible_*` and `unknown_orders` columns.

```python
orders_main["late_handover"] = (
    orders_main["order_delivered_carrier_date"].dt.normalize()
    .gt(orders_main["shipping_limit_date"].dt.normalize())
)
orders_main["order_purchase_month"] = (
    orders_main["order_purchase_timestamp"].dt.to_period("M").astype(str)
)

# Platform late rate by purchase month.
monthly_benchmark = (
    orders_main.groupby("order_purchase_month", as_index=False)
    .agg(orders=("order_id", "size"), late_orders=("late_handover", "sum"))
)
monthly_benchmark["late_rate"] = monthly_benchmark["late_orders"] / monthly_benchmark["orders"]

# Attach each order's monthly benchmark, then aggregate to one row per seller.
orders_with_benchmark = orders_main.merge(
    monthly_benchmark[["order_purchase_month", "late_rate"]].rename(
        columns={"late_rate": "month_late_rate"}
    ),
    on="order_purchase_month",
    how="left",
    validate="many_to_one",
)
seller_metrics = (
    orders_with_benchmark.groupby("seller_id", as_index=False)
    .agg(
        order_volume=("order_id", "size"),
        late_orders=("late_handover", "sum"),
        benchmark_late_rate=("month_late_rate", "mean"),
    )
)
seller_metrics["late_rate"] = seller_metrics["late_orders"] / seller_metrics["order_volume"]
seller_metrics["late_rate_gap_pp"] = (
    seller_metrics["late_rate"].sub(seller_metrics["benchmark_late_rate"]).mul(100)
)
seller_metrics = seller_metrics[
    ["seller_id", "order_volume", "late_orders", "late_rate",
     "benchmark_late_rate", "late_rate_gap_pp"]
]

output_dir = Path("../Data/Clean")  # Relative to notebooks/01_cleaning.ipynb.
output_dir.mkdir(parents=True, exist_ok=True)
monthly_benchmark.to_csv(output_dir / "monthly_benchmark.csv", index=False)
seller_metrics.to_csv(output_dir / "seller_metrics.csv", index=False)

print(f"seller_metrics: {len(seller_metrics):,} sellers, "
      f"{seller_metrics['order_volume'].sum():,} orders, "
      f"{seller_metrics['late_orders'].sum():,} late")
print(f"monthly_benchmark: {len(monthly_benchmark)} months, "
      f"{monthly_benchmark['order_purchase_month'].min()} to "
      f"{monthly_benchmark['order_purchase_month'].max()}")
display(monthly_benchmark.round(4))
display(seller_metrics.describe().round(3))
```

Expected output:
- `seller_metrics`: 2,917 sellers, 93,598 orders, 5,407 late orders.
- `monthly_benchmark`: 20 months, 2017-01 to 2018-08. Lowest late rate 2018-04 (3.49%), highest 2017-01 (18.55%).
- `benchmark_late_rate` ranges from 0.035 to 0.185 across sellers.
- Checks: `order_volume` sums to 93,598 and `late_orders` to 5,407; weighting `benchmark_late_rate` by `order_volume` gives the platform rate (5.78%).

**Limitation to mention.** The monthly benchmark includes the seller being compared. A large seller pulls the platform rate for its months toward its own rate, which slightly shrinks its gap. The largest seller has at most 5.9% of any month's orders, so the effect is small.

**Report wording (Data section).**
> For each seller we computed order volume, the number of late handovers and the late rate. To compare sellers fairly across months with different platform late rates (3.5% to 18.5%), we also computed a same-month benchmark: the late rate the seller would have if each of its orders were late at the platform rate for its month. The gap between a seller's late rate and this benchmark, in percentage points, shows whether the seller is later or more punctual than the platform in the months it sold.

## Resolved issues

Problems from the notebook review and the change that resolves each one.

- [x] Missing carrier handover timestamp (1,783 orders): change 1.
- [x] Shipped orders counted in the late rate (1,103 in the single-seller sample): change 1.
- [x] Canceled orders with a handover timestamp (75): change 1.
- [x] Handover before purchase (161 in the sample): change 2, group A.
- [x] Handover after purchase but before payment approval (1,156 in the sample): change 2, group B; tested in `04_checks`.
- [x] Customer delivery before handover (4 in the sample): change 2.
- [x] Shipping deadline more than 365 days after purchase (1 order in the sample): change 3.
- [x] 2016 orders (260 in the sample, 48% late rate): change 4.
- [x] Near-empty months of September–October 2018 (20 orders, none delivered): change 1; recorded in change 4.
- [x] Orders with no item rows (775): change 5.
- [x] Orders with more than one seller (1,278): change 5.
- [x] Late handover definition: by date (5.78%), with the timestamp version (9.10%) in `04_checks`: change 6.
- [x] Seller metrics and monthly benchmark only in memory: change 7, with same-month benchmark columns added.
- [x] `order_volume` vs eligible orders: resolved by changes 1–4. Every order in the main sample has a known handover outcome, so `order_volume` equals the number of eligible orders.
- [x] Orders with several reviews, and reviews shared by several orders: change 8, with the earliest and latest rating both kept.
- [x] Code clean-up, done in the rebuild of `01_cleaning.ipynb`: removed the purchase-month mismatch check, duplicate imports, reused variable names and the `eligible_*` / `unknown_orders` columns; `late_rate` is saved as a plain float; only `orders` and `order_items` are loaded.

### 8. Review ratings: orders with several reviews

**Problem.** The reviews table (`olist_order_reviews_dataset.csv`, 99,224 rows) does not have exactly one review per order, so it cannot be merged onto orders as it is.

| Case | Count | Most likely reason |
|---|---|---|
| One order, several reviews | 547 orders (1,098 rows): 543 with 2 reviews, 4 with 3 | The customer answered the review survey more than once. Reviews are usually a few days apart (median 3, up to 106), and 202 of these orders have different scores |
| One review, several orders | 789 reviews (1,603 rows) | One purchase split into several orders: in every case it is the same customer, and 95% of the orders were placed on the same day |

In the main sample (93,598 orders), 622 orders (0.7%) have no review, and 508 have more than one. The dataset documentation does not explain either case; the reasons above are inferred from the data.

**How we found it.** Count reviews per order and orders per review, then check whether the orders sharing a review belong to the same customer and were placed on the same day. This continues from the change 1 code (`orders` with parsed timestamps), with `reviews` loaded with `parse_dates=["review_creation_date", "review_answer_timestamp"]`.

```python
customers = pd.read_csv(f"{data_url}/olist_customers_dataset.csv")

# One order, several reviews.
reviews_per_order = reviews.groupby("order_id")["review_id"].size()
multi_review_orders = reviews_per_order.index[reviews_per_order.gt(1)]
multi_reviews = reviews.loc[reviews["order_id"].isin(multi_review_orders)].groupby("order_id")
days_apart = (
    multi_reviews["review_creation_date"].max() - multi_reviews["review_creation_date"].min()
).dt.days
print(f"Orders with more than one review: {len(multi_review_orders):,} "
      f"({reviews['order_id'].isin(multi_review_orders).sum():,} rows)")
print(f"  with different scores: {multi_reviews['review_score'].nunique().gt(1).sum()}")
print(f"  days between first and last review: median {days_apart.median():.0f}, max {days_apart.max()}")

# One review, several orders.
orders_per_review = reviews.groupby("review_id")["order_id"].size()
shared_ids = orders_per_review.index[orders_per_review.gt(1)]
shared = (
    reviews.loc[reviews["review_id"].isin(shared_ids), ["review_id", "order_id"]]
    .merge(orders[["order_id", "customer_id", "order_purchase_timestamp"]], on="order_id")
    .merge(customers[["customer_id", "customer_unique_id"]], on="customer_id")
    .groupby("review_id")
)
same_day = (
    shared["order_purchase_timestamp"].max().dt.normalize()
    .eq(shared["order_purchase_timestamp"].min().dt.normalize())
)
print(f"Reviews attached to more than one order: {len(shared_ids):,} "
      f"({reviews['review_id'].isin(shared_ids).sum():,} rows)")
print(f"  same customer: {shared['customer_unique_id'].nunique().eq(1).mean():.0%}; "
      f"orders placed on the same day: {same_day.mean():.0%}")
```

Expected output:
- 547 orders with more than one review (1,098 rows); 202 with different scores; median 3 days and maximum 106 days between first and last review.
- 789 reviews attached to more than one order (1,603 rows); 100% the same customer; 95% placed on the same day.

**Decision.**
- **Keep two ratings per order:** `review_score_first` (earliest review) and `review_score_last` (latest review), ordered by `review_creation_date` and then `review_answer_timestamp`. For orders with one review, both are the same.
- **A review attached to several orders** gives its score to each of them.
- **Orders without a review** keep missing ratings. Do not impute.
- **The clustering team chooses** which rating to use and reports the other as a robustness check.

**Why.**
- **Neither review is clearly the right one.** The earliest is closest to the delivery experience; the latest is the customer's final view. Keeping both avoids making that choice in cleaning.
- **The choice barely matters, and keeping both shows it.** Only 179 main-sample orders (0.2%) have different first and last scores. Average ratings are 4.21 for on-time and 3.55 for late orders under both.
- **A shared review is a real answer for each order.** The customer rated the whole purchase, so each of its orders gets that score.
- **No imputation,** for the same reason as changes 1 and 3: filling in a rating would invent a customer's opinion.

**How to apply.** Applied in `01_cleaning.ipynb` (audit step "Orders with several reviews" and cleaning step "Attach review ratings").
- Load `olist_order_reviews_dataset.csv` with the review dates parsed.
- Sort reviews by `review_creation_date` and `review_answer_timestamp`; keep the first row per order as `review_score_first` and the last as `review_score_last`.
- Left join both onto the main sample and group B, so no order is dropped.
- Add to `orders_main.csv` and `orders_group_b.csv`: `review_score_first`, `review_score_last`.
- Add to `seller_metrics.csv`: `reviewed_orders` (orders with a review), `avg_review_first`, `avg_review_last`, `low_review_share_first`, `low_review_share_last` (share of ratings of 2 stars or less). 3 sellers have no reviewed orders, so their review columns are missing.
- The reconcile step checks that reviewed orders across sellers equal reviewed orders in `orders_main.csv` (92,976).

Expected output: 622 main-sample orders without a review (0.7%); 179 whose first and last score differ (0.2%); 6 group B orders without a review. All earlier counts are unchanged (93,598 orders, 5,407 late, 2,917 sellers).

**Report wording (Data section).**
> Customer ratings come from the reviews table. 547 orders had more than one review, most likely because the customer answered the survey more than once, and 789 reviews applied to several orders bought together by the same customer. For each order we kept both the earliest and the latest review; they differ for only 179 orders (0.2%) and give the same results. Orders without a review (0.7%) were left without a rating.

**Limitation to mention.** Ratings reflect the customer's whole experience, including carrier delivery and product quality, not only the seller's handover. Differences in ratings between seller groups are associations, not effects of late handover.

## Left to the clustering team

These are not cleaning decisions; the cleaning notebook passes them to the clustering team. The minimum-order threshold, the 2017 → 2018 holdout counts and the `04_checks` credibility checks are in **[`read-me-first/pass-over-to-clustering.md`](../read-me-first/pass-over-to-clustering.md)**.

## Issues still to decide

None. Every issue from the notebook review has been resolved (see **Resolved issues**).

Expected result after changes 1–4: 93,598 orders in the main sample, January 2017 to August 2018 (the proposal's 93,859, minus 1 order in change 3 and 260 orders from 2016 in change 4), 1,156 orders in `Data/Clean/orders_group_b.csv`; together 94,754 orders for the `04_checks` check sample. With the date definition from change 6, the platform late rate in the main sample is 5.78%. After change 8, 92,976 main-sample orders have a review rating.

## Documentation to update

Done: both the README and the handoff section of `01_cleaning.ipynb` were updated when the notebook was rebuilt. The text below is kept for reference.

**1. `README.md` (GitHub repo).** Add both files to the repository structure and explain them:

```
Data/
├── Raw/                      # Original Olist CSVs (do not edit)
└── Clean/                    # Outputs of notebooks/01_cleaning.ipynb (do not edit by hand)
    ├── orders_main.csv       # Main sample: 93,598 cleaned orders, Jan 2017 – Aug 2018
    ├── orders_group_b.csv    # 1,156 orders handed over before payment approval; 04_checks only
    ├── seller_metrics.csv    # One row per seller (2,917), built from orders_main.csv
    └── monthly_benchmark.csv # Platform late rate by month (2017-01 to 2018-08)
notebooks/
├── 01_cleaning.ipynb         # Cleaning and merge; writes everything in Data/Clean/
├── 02_q1.ipynb
├── 03_q2.ipynb
├── 04_checks.ipynb
└── 05_figures.ipynb
```

> **Which file to use.** All main analysis (Q1, Q2, figures, report and slide numbers) reads `Data/Clean/seller_metrics.csv` and `Data/Clean/monthly_benchmark.csv`. Use `Data/Clean/orders_main.csv` only when you need seller metrics under different settings, such as the 2017 → 2018 holdout. `Data/Clean/orders_group_b.csv` is only for the credibility check in `04_checks`, where it is combined with `orders_main.csv`. Do not add it to the main analysis.

**2. The notebook's "Handoff to the clustering team" section.** Replace the `merged_orders` / `analysis_orders` rows in the handoff table with the saved files, and add the group B reminder:

| File | What to use it for |
| --- | --- |
| `Data/Clean/orders_main.csv` | Main sample, one row per order (93,598). Input for the 2017 training and 2018 validation split. |
| `Data/Clean/orders_group_b.csv` | 1,156 orders handed over after purchase but before payment approval. Use only in `04_checks`: combine with `orders_main.csv` and compare results. |
| `Data/Clean/seller_metrics.csv` | One row per seller (2,917), built from `orders_main.csv`: `order_volume`, `late_orders`, `late_rate`, `benchmark_late_rate`, `late_rate_gap_pp`. Input for Q1, Q2 clustering and figures. No minimum-order threshold applied. |
| `Data/Clean/monthly_benchmark.csv` | Platform late rate by purchase month, 2017-01 to 2018-08. Same-month baseline for Q1 and the monthly trend figure. |

Then paste the **Credibility check for `04_checks`** texts from changes 2 and 6, and the **Minimum orders per seller** table and points from **Left to the clustering team**.

