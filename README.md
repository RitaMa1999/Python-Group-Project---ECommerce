# Python-Group-Project---ECommerce

MMGMT 722 · Group 3 · Final Project

Seller late handover on the Olist Brazilian e-commerce marketplace. We study how sellers differ in handing orders to the carrier after the `shipping_limit_date`, and which groups of sellers managers should prioritize.

## Research questions

| # | Question | Method |
|---|----------|--------|
| Q1 | How much do sellers differ in late handover? | Descriptive analysis: distributions of order volume, late orders and late rate, compared with the platform average and the same-month average |
| Q2 | Which groups of sellers exist, and how should each be prioritized? | K-means clustering on late rate and log(order volume), standardized; k chosen with elbow / silhouette |

**Late handover** = the order was handed to the carrier after `shipping_limit_date`.

## Key dates and deliverables

Everything is due **Monday, Nov 23, 2026**, the day we present. Double-check the dates on Avenue.

| Deliverable | Due | Requirements |
|-------------|-----|--------------|
| Slides sent to the instructor | Evening of Nov 22, 2026 | Send before we present |
| Final presentation | Nov 23, 2026 | 10 min + 3 min Q&A; about 10 slides, max 12; all four members speak |
| Discussant for Group 2 | Nov 23, 2026 | 1–2 specific comments or questions in class |
| Written report | Nov 23, 2026 | Max 12 pages excluding appendices; includes an AI-use appendix |
| Code | Nov 23, 2026 | Runs end to end from the raw data; numbers match the report |
| Contribution statement | Nov 23, 2026 | Signed by all four members |

Group 4 is our discussant and will ask questions about our analysis.

## Repository structure

> **Read `notation/` before starting your part.** The clustering team starts with `notation/pass-over-to-clustering.md`.

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
├── change.markdown           # Cleaning decisions: problem, how we found it, decision, reasons
├── 02_descriptive_analysis.ipynb  # Q1 descriptive analysis; writes figures/q1_*.png
├── descriptive_analysis.markdown  # Q1 plan: each chart, why, and the decisions behind it
├── 03_q2.ipynb
├── 04_checks.ipynb
└── 05_figures.ipynb
figures/                      # All figures, named by notebook and item (e.g. q1_02a_pareto_curve.png)
notation/                     # Read before starting your part
└── pass-over-to-clustering.md  # Handoff for Q2 and 04_checks: files, definitions, threshold, checks
```

### Raw data (`Data/Raw/`)

| File | Contents |
|------|----------|
| `olist_orders_dataset.csv` | Orders, status and timestamps |
| `olist_order_items_dataset.csv` | Order items, seller and `shipping_limit_date` |
| `olist_sellers_dataset.csv` | Sellers |
| `olist_customers_dataset.csv` | Customers |
| `olist_products_dataset.csv` | Products |
| `product_category_name_translation.csv` | Category names, Portuguese to English |
| `olist_order_payments_dataset.csv` | Payments |
| `olist_order_reviews_dataset.csv` | Reviews |
| `olist_geolocation_dataset.csv` | Zip-code coordinates (about 58 MB, too large for GitHub's preview) |

### Cleaned data (`Data/Clean/`)

Created by `notebooks/01_cleaning.ipynb`. The reasons for each cleaning step are in `notebooks/change.markdown`.

| File | One row per | Contents | Used by |
|------|-------------|----------|---------|
| `seller_metrics.csv` | Seller (2,917) | `order_volume`, `late_orders`, `late_rate`, `benchmark_late_rate`, `late_rate_gap_pp`; no minimum-order threshold | Q1, Q2 clustering, figures |
| `monthly_benchmark.csv` | Month (20) | `orders`, `late_orders`, `late_rate` | Q1 same-month baseline, monthly trend figure, report |
| `orders_main.csv` | Order (93,598) | Order IDs, seller, timestamps, deadline, `late_handover` | Rebuilding seller metrics under other settings, e.g. the 2017 → 2018 holdout |
| `orders_group_b.csv` | Order (1,156) | Same columns; handed over after purchase but before payment approval | `04_checks` only |

> **Which file to use.** All main analysis (Q1, Q2, figures, report and slide numbers) reads `Data/Clean/seller_metrics.csv` and `Data/Clean/monthly_benchmark.csv`. Use `Data/Clean/orders_main.csv` only when you need seller metrics under different settings, such as the 2017 → 2018 holdout. `Data/Clean/orders_group_b.csv` is only for the credibility check in `04_checks`, where it is combined with `orders_main.csv`. Do not add it to the main analysis.

**Key definitions.** The main sample is delivered, single-seller orders with complete, correctly ordered timestamps, placed from January 2017 to August 2018. An order is a late handover when it is handed to the carrier on a calendar day after its `shipping_limit_date` day. The platform late rate is 5.78%.

## Shared conventions

- Every notebook reads from the same `Data/Clean/seller_metrics.csv`. Don't re-clean the data in your own notebook, so the numbers in the report, slides and code stay consistent.
- Write code comments and variable names in English, and remove unused code.
- Name figures in `figures/` by notebook and item number (for example `q1_02a_pareto_curve.png`), because slide numbers are not final. The PPT role can save slide-numbered copies once the slides are fixed.

## Decisions before cleaning

- [ ] **Minimum orders per seller:** left to the clustering team; suggested 20 for the main analysis, with 10 and 30 as checks. See the handoff section of `notebooks/01_cleaning.ipynb`
- [x] **Drop 2016?** Yes. The study period is January 2017 to August 2018
- [x] **How to measure lateness:** by date. The platform late rate is 5.78% by date and 9.10% by timestamp (tested in `04_checks`)

## Roles

| Role | Responsible for | Presents | Owner |
|------|-----------------|----------|-------|
| Data | Cleaning, seller-level table, credibility checks, final end-to-end run; discussant on the day | Data and credibility checks (~2:00) | TBD |
| Analysis | Q1 descriptive analysis, Q2 K-means, cluster profiles and priorities | Q2 method, findings and recommendations (~3:00) | TBD |
| Report | Writing and editing the full report, AI-use appendix, contribution statement | Problem, research questions, conclusion (~2:30) | TBD |
| PPT | Full slide deck, plotting code, timed rehearsal | Q1 method and findings (~2:30) | TBD |

Daisy presented the data at the proposal stage, so she could keep the Data role. The other three roles go to whoever is strongest at each.

## Tasks by role

The critical step is **`seller_metrics.csv` on Tuesday evening**. All later analysis starts from this table.

### Data
- [ ] Mon–Tue (Nov 16–17): `01_cleaning`, using the proposal's filters (delivered, single seller, complete and correctly ordered timestamps; 93,859 orders); add a `late_handover` column
- [ ] Tue evening (Nov 17): deliver `seller_metrics.csv` (one row per seller: orders, late orders, late rate) plus a monthly platform late-rate table
- [ ] Wed–Thu (Nov 18–19): `04_checks` (different minimum-order thresholds, different lateness definitions, 2017 clusters tested on 2018); write data-section notes for the report
- [ ] Fri (Nov 20): run the checks with the analysis clustering function; send result tables to Report and PPT
- [ ] Sat (Nov 21): rerun every notebook from the raw data and confirm the numbers match the report
- [ ] Mon (Nov 23): listen to Group 2 and ask 1–2 specific questions (others help take notes)

### Analysis
- [ ] Mon–Tue (Nov 16–17): build the Q1 and Q2 code skeletons using the preliminary proposal data
- [ ] Wed (Nov 18): `02_descriptive_analysis`, distributions of seller order volume, late orders and late rate, compared with the platform and same-month averages
- [ ] Thu (Nov 19): `03_q2`, K-means on late rate and log(order volume), standardized; choose k with elbow / silhouette
- [ ] Thu evening (Nov 19): deliver key Q1 numbers and the cluster profile table (sellers, average orders, average late rate); wrap clustering in a function for the Data role
- [ ] Fri (Nov 20): set priorities and management actions for each cluster with the Report role
- [ ] Sat (Nov 21): check that the report describes the analysis and findings correctly

### Report
- [ ] Mon–Tue (Nov 16–17): Introduction (problem, audience, why it matters, the two research questions)
- [ ] Wed–Thu (Nov 18–19): Data section and the Method parts for both questions, following the proposal's analysis plan
- [ ] Fri (Nov 20): Findings once results arrive; agree on recommendations with the Analysis role
- [ ] Sat (Nov 21): Recommendations, Conclusion, Limitations; edit down to 12 pages
- [ ] Sun (Nov 22): collect everyone's AI-use notes for the appendix; prepare the contribution statement

### PPT
- [ ] Mon (Nov 16): set up a 10-slide skeleton from the proposal template and share it with the group
- [ ] Tue–Thu (Nov 17–19): problem, research question and data slides; Q1 plotting code from `seller_metrics.csv`
- [ ] Fri (Nov 20): Q2 and credibility-check figures; fill every slide
- [ ] Sat (Nov 21): finalize the slides; remind everyone to write their script
- [ ] Sun (Nov 22): run a timed rehearsal; send the slides to the instructor

### Everyone
- [ ] Keep notes on what you used AI for and what you checked (needed for the AI-use appendix)
- [ ] Read the full report before Sunday. The instructor may ask anyone about any part

## Presentation plan (10 slides, 10 minutes)

| # | Content | Speaker | Time |
|---|---------|---------|------|
| 1 | Title + problem: why seller late handover is worth managing | Report | 0:45 |
| 2 | Audience and the two research questions | Report | 0:45 |
| 3 | Data and the definition of late handover (one slide, no cleaning details) | Data | 0:45 |
| 4 | Q1 method + main finding: how much sellers differ | PPT | 1:15 |
| 5 | What the Q1 findings mean for managers | PPT | 1:15 |
| 6 | Q2 method: features used and how k was chosen | Analysis | 1:00 |
| 7 | Q2 findings: seller cluster profiles | Analysis | 1:15 |
| 8 | Q2 recommendations: priority and management action for each cluster | Analysis | 0:45 |
| 9 | Credibility checks: thresholds, definitions, 2017 → 2018 | Data | 1:15 |
| 10 | Conclusion, limitations, challenges | Report | 1:00 |

Totals: Report 2:30, Data 2:00, PPT 2:30, Analysis 3:00. Slides 4–9 cover the analysis and findings (6 slides, in line with the instructor's suggested 6–7). PPT presents Q1, so they should go through the results with Analysis on Thursday. In Q&A, each person answers first for the part they presented.

## Report plan (about 11 pages, 1 page spare)

| Section | Writer | Input / review | Rubric (out of 100) | Pages |
|---------|--------|----------------|---------------------|-------|
| 1 Introduction: problem, audience, research questions | Report | — | Problem framing 20 | 1.5 |
| 2 Data & preparation: source, cleaning, exclusions, constructed variables | Report | Data | Data 15 | 2 |
| 3 Q1 Seller differences | Report | Analysis | Analysis 20 + Findings 20 | 2 |
| 4 Q2 Seller clusters & priorities | Report | Analysis | Same as above | 2.5 |
| 5 Credibility checks & limitations | Report | Data | Evaluation 15 | 1.5 |
| 6 Recommendations & conclusion | Report | Analysis | Findings 20 | 1.5 |
| Appendix A: AI use | Report (compiles) | Everyone submits their own notes | Required | — |
| Appendix B: Contribution statement | Report | Signed by all four | Required | — |

Code is worth 10 points; the Data role reruns it end to end on Saturday. After sections 3–5 are written, the Analysis or Data role must review them so no numbers or methods are wrong.
