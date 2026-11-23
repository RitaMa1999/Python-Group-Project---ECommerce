# Python-Group-Project---ECommerce

MMGMT 722 · Group 3 · Final Project

Seller late handover on the Olist Brazilian e-commerce marketplace. We study how sellers differ in handing orders to the carrier after the `shipping_limit_date`, and which groups of sellers managers should prioritize.

## Research questions

| # | Question | Method |
|---|----------|--------|
| Q1 | How much do sellers differ in late handover? | Descriptive analysis: distributions of order volume, late orders and late rate, compared with the platform average and the same-month average |
| Q2 | Which groups of sellers exist, and how should each be prioritized? | K-means on late rate and log(1 + late orders), standardized, for sellers with ≥20 orders; k = 4 chosen with elbow / silhouette against a no-groups baseline; sellers in the focus tiers ranked by excess late handovers |

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

> **Read `read-me-first/` before starting your part.** The clustering team starts with `read-me-first/pass-over-to-clustering.md`, the PPT role with `read-me-first/pass-over-to-ppt.md`, and the report writer with `read-me-first/pass-over-to-report.md` (Q2 chapters) and `read-me-first/ai-use-appendix.md` (Appendix A).

```
Data/
├── Raw/                      # Original Olist CSVs (do not edit)
├── Clean/                    # Outputs of notebooks/01_cleaning.ipynb (do not edit by hand)
│   ├── orders_main.csv       # Main sample: 93,598 cleaned orders, Jan 2017 – Aug 2018
│   ├── orders_group_b.csv    # 1,156 orders handed over before payment approval; 04_checks only
│   ├── seller_metrics.csv    # One row per seller (2,917), built from orders_main.csv
│   └── monthly_benchmark.csv # Platform late rate by month (2017-01 to 2018-08)
└── Results/                  # Outputs of notebooks/03_q2.ipynb (do not edit by hand)
    ├── seller_tiers.csv      # 778 sellers with ≥20 orders: tier, excess late handovers, focus flag
    └── focus_sellers_ranked.csv  # 159 focus-tier sellers ranked by excess late handovers
notebooks/
├── 01_cleaning.ipynb         # Cleaning and merge; writes everything in Data/Clean/
├── change.markdown           # Cleaning decisions: problem, how we found it, decision, reasons
├── 02_descriptive_analysis.ipynb  # Q1 descriptive analysis; writes figures/q1_*.png
├── descriptive_analysis.markdown  # Q1 plan: each chart, why, and the decisions behind it
├── q2_tiers.py               # Shared Q2 functions (features, K-means, tiers, profiles), used by 03 and 04
├── 03_q2.ipynb               # Q2 tiers, profiles, ratings, focus tiers and seller ranking; writes Data/Results/ and figures/q2_*.png
├── 04_checks.ipynb           # 10 credibility checks for Q2, with an English summary at the top
└── 05_figures.ipynb          # Slide versions of the figures in the presentation's style (same data); writes figures/slide*.png
figures/                      # All figures, named by notebook and item (e.g. q1_02a_pareto_curve.png); slide versions start with slideNN_
prototype/
└── app.py                    # Streamlit prototype for managers: a read-only view of Data/Results/ (see How to run)
.streamlit/config.toml        # Prototype theme: the presentation's colours and font
read-me-first/                # Read before starting your part
├── pass-over-to-clustering.md  # Handoff for Q2 and 04_checks: files, definitions, threshold, checks
├── pass-over-to-ppt.md         # Handoff for the slides: figures, which to use, styling, key numbers (Q1 and Q2)
├── pass-over-to-report.md      # Handoff for the report's Q2 chapters: method, results, limitations, recommendations
└── ai-use-appendix.md          # AI-use records from the notebooks, for the report's Appendix A
pyproject.toml, uv.lock       # Python version and packages for uv (see How to run)
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
| `seller_metrics.csv` | Seller (2,917) | `order_volume`, `late_orders`, `late_rate`, `benchmark_late_rate`, `late_rate_gap_pp`; review summaries `reviewed_orders`, `avg_review_first`, `avg_review_last`, `low_review_share_first`, `low_review_share_last`; no minimum-order threshold | Q1, Q2 clustering, figures |
| `monthly_benchmark.csv` | Month (20) | `orders`, `late_orders`, `late_rate` | Q1 same-month baseline, monthly trend figure, report |
| `orders_main.csv` | Order (93,598) | Order IDs, seller, timestamps, deadline, `late_handover`, `review_score_first`, `review_score_last` | Rebuilding seller metrics under other settings, e.g. the 2017 → 2018 holdout |
| `orders_group_b.csv` | Order (1,156) | Same columns; handed over after purchase but before payment approval | `04_checks` only |

> **Which file to use.** All main analysis (Q1, Q2, figures, report and slide numbers) reads `Data/Clean/seller_metrics.csv` and `Data/Clean/monthly_benchmark.csv`. Use `Data/Clean/orders_main.csv` only when you need seller metrics under different settings, such as the 2017 → 2018 holdout. `Data/Clean/orders_group_b.csv` is only for the credibility check in `04_checks`, where it is combined with `orders_main.csv`. Do not add it to the main analysis.

**Key definitions.** The main sample is delivered, single-seller orders with complete, correctly ordered timestamps, placed from January 2017 to August 2018. An order is a late handover when it is handed to the carrier on a calendar day after its `shipping_limit_date` day. The platform late rate is 5.78%.

## How to run

The project uses [uv](https://docs.astral.sh/uv/). `pyproject.toml` lists the Python version and packages, and `uv.lock` fixes their exact versions, so everyone gets the same results.

1. Install the environment once, from the repository folder:

   ```
   uv sync
   ```

2. Run the notebooks in order, 01 → 05. Each one reads the outputs of the notebooks before it, so together they rebuild `Data/Clean/`, `Data/Results/` and `figures/` from the raw data. Either open them with `uv run jupyter lab` and run all cells, or run them from the terminal:

   ```
   uv run jupyter nbconvert --to notebook --execute --inplace notebooks/01_cleaning.ipynb
   uv run jupyter nbconvert --to notebook --execute --inplace notebooks/02_descriptive_analysis.ipynb
   uv run jupyter nbconvert --to notebook --execute --inplace notebooks/03_q2.ipynb
   uv run jupyter nbconvert --to notebook --execute --inplace notebooks/04_checks.ipynb
   uv run jupyter nbconvert --to notebook --execute --inplace notebooks/05_figures.ipynb
   ```

   `01_cleaning` reads the raw CSVs from this repository on GitHub, so it needs an internet connection.

3. Start the prototype (it reads `Data/Results/`, so run `03_q2` first):

   ```
   uv run streamlit run prototype/app.py
   ```

## Shared conventions

- Every notebook reads from the same `Data/Clean/seller_metrics.csv`. Don't re-clean the data in your own notebook, so the numbers in the report, slides and code stay consistent.
- Write code comments and variable names in English, and remove unused code.
- Name figures in `figures/` by notebook and item number (for example `q1_02a_pareto_curve.png`), because slide numbers are not final. Slide versions are drawn in `05_figures.ipynb` and named by slide (for example `slide07_tiers.png`); they change only the appearance, not the data.

## Decisions before cleaning

- [x] **Minimum orders per seller:** 20 for the main analysis (778 sellers, 87.5% of orders), with 10 and 30 as checks in `04_checks`
- [x] **Drop 2016?** Yes. The study period is January 2017 to August 2018
- [x] **How to measure lateness:** by date. The platform late rate is 5.78% by date and 9.10% by timestamp (tested in `04_checks`)

## Roles

| Role | Responsible for | Presents | Owner |
|------|-----------------|----------|-------|
| Data | Cleaning, seller-level and monthly tables, Q1 descriptive analysis, final end-to-end run; discussant on the day | Data and Q1 (~2:45) | Yanxin (Rita) Ma |
| Analysis | Q2 K-means tiers and seller ranking, credibility checks (`04_checks`), tier recommendations | Q2 method, findings and credibility checks (~3:05) | Rui Chen |
| Report | Writing and editing the full report, AI-use appendix, contribution statement | Problem, research questions, recommendations (~2:20) | Lingli (Helen) Li |
| PPT & prototype | Slide deck, slide figures (`05_figures`), prototype (`prototype/app.py`) and its demo video, timed rehearsal | Prototype video, conclusion (~1:35) | Jingshu (Daisy) Fu |

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

### PPT & prototype
- [ ] Mon (Nov 16): set up a 10-slide skeleton from the proposal template and share it with the group
- [ ] Tue–Thu (Nov 17–19): problem, research question and data slides; Q1 plotting code from `seller_metrics.csv`
- [ ] Fri (Nov 20): Q2 and credibility-check figures; fill every slide
- [ ] Sat (Nov 21): finalize the slides; remind everyone to write their script
- [ ] Sun (Nov 22): `05_figures`, slide versions of the figures in the presentation's style (`figures/slide*.png`)
- [ ] Sun (Nov 22): prototype (`prototype/app.py`), a read-only view of `Data/Results/` for managers; record the demo video for slide 10
- [ ] Sun (Nov 22): run a timed rehearsal; send the slides to the instructor

### Everyone
- [ ] Keep notes on what you used AI for and what you checked (needed for the AI-use appendix)
- [ ] Read the full report before Sunday. The instructor may ask anyone about any part

## Presentation plan (12 slides, 10 minutes)

| # | Content | Speaker | Time |
|---|---------|---------|------|
| 1 | Title page | Report | 0:10 |
| 2 | Problem, audience and the two research questions | Report | 1:20 |
| 3 | Data and the definition of late handover (one slide, no cleaning details) | Data | 0:45 |
| 4 | Q1: late handovers are concentrated in a few sellers | Data | 1:00 |
| 5 | Q1 for managers: judge rates only with enough orders, then focus | Data | 1:00 |
| 6 | Q2 method: features, choice of k, focus tiers and ranking | Analysis | 0:55 |
| 7 | Q2 findings: four tiers along one lateness scale | Analysis | 1:10 |
| 8 | Credibility checks: why the results hold | Analysis | 1:00 |
| 9 | Q2 recommendations: whom to contact first, and how | Report | 0:50 |
| 10 | Prototype video (recorded voice-over) | PPT & prototype | 0:40 |
| 11 | Conclusion, limitations and challenges | PPT & prototype | 0:55 |
| 12 | Thank you; questions | PPT & prototype | — |

Totals: Report 2:20, Data 2:45, Analysis 3:05, PPT & prototype 1:35 (0:40 of it the recorded video); 9:45 in all. Slides 4–9 cover the analysis and findings (6 slides, in line with the instructor's suggested 6–7). The order follows the report: findings, then the credibility checks, then recommendations. Each person presents the part they built, and in Q&A answers first for those slides.

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
