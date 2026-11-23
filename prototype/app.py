"""Seller late-handover monitor: a prototype of how platform managers could use the Q2 results.

The app only reads the saved outputs of notebooks/01_cleaning.ipynb and notebooks/03_q2.ipynb.
It does not refit K-means or change any tier, so every number matches the report and slides.

Run from the repository root (after `uv sync`):
    uv run streamlit run prototype/app.py
"""
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
SELLER_METRICS_PATH = ROOT / "Data" / "Clean" / "seller_metrics.csv"        # all 2,917 sellers
SELLER_TIERS_PATH = ROOT / "Data" / "Results" / "seller_tiers.csv"          # 778 sellers with >= 20 orders
FOCUS_RANKED_PATH = ROOT / "Data" / "Results" / "focus_sellers_ranked.csv"  # 159 focus sellers, ranked

MIN_ORDERS = 20  # minimum orders for a seller to be placed in a tier (03_q2)
TOP_N = 20       # the "top 20 sellers" used in the report and slides
ID_CHARS = 6     # seller IDs are shown by their first 6 characters, as on the slides

# Tier names from 03_q2; the action for each seller group follows the report (Table 6)
TIER_NAMES = {
    1: "Rarely late",
    2: "Occasionally late",
    3: "Slightly above platform, high volume",
    4: "Severely late",
}
# Same tier colours as the slide charts (05_figures): light purple (least late) to dark plum (most late)
TIER_COLORS = {1: "#c6a6e8", 2: "#9a78c8", 3: "#6c4b94", 4: "#34253f"}
TIER_ACTIONS = {
    4: "Begin with Tier 4 sellers in the top 20, then extend individual reviews to the remaining Tier 4 "
       "sellers. Investigate recurring handover delays and review customer feedback for possible issues "
       "such as product quality, since Tier 4 also received lower ratings on on-time orders. Agree on an "
       "improvement target and a follow-up date with each seller.",
    3: "Start with sellers with the largest excess late handover counts. Review their order preparation "
       "and carrier handover processes, then track performance against their same-month benchmarks. "
       "Continue routine monitoring for sellers whose late handover counts are at or below expectations.",
    2: "Monitor performance routinely and send a reminder when the seller's late handover rate exceeds "
       "its same-month benchmark.",
    1: "Continue routine monitoring.",
}
SMALL_SELLER_ACTION = ("Pilot an automated reminder based on the number of late handovers; "
                       "two and three late handovers are candidate triggers.")
LIMITS = ("Snapshot of January 2017 – August 2018: the focus list should be updated monthly with recent "
          "orders, keeping the tier boundaries fixed. Ratings are associated with late handovers; the data "
          "does not show that late handovers cause them.")


@st.cache_data
def load_data():
    """Read the saved seller tables. Nothing is recomputed from the order data."""
    sellers_all = pd.read_csv(SELLER_METRICS_PATH)
    tiers = pd.read_csv(SELLER_TIERS_PATH)
    ranked = pd.read_csv(FOCUS_RANKED_PATH)  # already sorted by excess late handovers in 03_q2
    ranked.insert(0, "rank", range(1, len(ranked) + 1))
    return sellers_all, tiers, ranked


def tier_table(tiers):
    """One row per tier, most late first, aggregated like profile_tiers() in notebooks/q2_tiers.py."""
    low_reviews = tiers["low_review_share_last"] * tiers["reviewed_orders"]
    prof = tiers.assign(low_reviews=low_reviews).groupby("tier").agg(
        sellers=("seller_id", "count"),
        orders=("order_volume", "sum"),
        late=("late_orders", "sum"),
        expected=("expected_late", "sum"),
        reviewed=("reviewed_orders", "sum"),
        low_reviews=("low_reviews", "sum"),
        focus=("focus_tier", "any"),  # focus tiers were set in 03_q2
    ).sort_index(ascending=False)
    table = pd.DataFrame({
        "Sellers": prof["sellers"],
        "Late rate": (prof["late"] / prof["orders"]).map("{:.1%}".format),
        "Gap to same-month platform": ((prof["late"] - prof["expected"]) / prof["orders"] * 100)
        .map("{:+.1f} pp".format),
        "Share of the tiered sellers' late handovers": (prof["late"] / prof["late"].sum()).map("{:.0%}".format),
        "Ratings ≤ 2 stars": (prof["low_reviews"] / prof["reviewed"]).map("{:.1%}".format),
        "Focus tier": prof["focus"].map({True: "Yes", False: "No"}),
        "Action": prof.index.map(TIER_ACTIONS),
    })
    table.index = [f"Tier {t} · {TIER_NAMES[t]}" for t in prof.index]
    return table


def top_share(ranked, tiers, n):
    """Share of the tiered sellers' positive excess late handovers covered by the first n ranked sellers."""
    selected_excess = ranked["excess_late"].head(n).clip(lower=0).sum()
    return selected_excess / tiers["excess_late"].clip(lower=0).sum()


def show_overview(sellers_all, tiers, ranked):
    st.subheader("Where late handovers come from")
    total_orders = sellers_all["order_volume"].sum()
    total_late = sellers_all["late_orders"].sum()
    kpis = [
        ("Platform late-handover rate", f"{total_late / total_orders:.2%}",
         f"{total_late:,} of {total_orders:,} orders"),
        ("Sellers in the tiers", f"{len(tiers):,}",
         f"of {len(sellers_all):,} sellers: those with at least {MIN_ORDERS} orders"),
        ("Focus sellers (Tiers 4 and 3)", f"{len(ranked)}",
         f"{ranked['late_orders'].sum() / tiers['late_orders'].sum():.0%} of the late handovers "
         f"of the {len(tiers)} tiered sellers"),
        (f"Top {TOP_N} sellers", f"{top_share(ranked, tiers, TOP_N):.0%}",
         f"of all positive excess late handovers across the {len(tiers)} tiered sellers"),
    ]
    for col, (label, value, note) in zip(st.columns(len(kpis)), kpis):
        col.metric(label, value)
        col.caption(note)

    st.table(tier_table(tiers))
    small = sellers_all[sellers_all["order_volume"] < MIN_ORDERS]
    st.caption(f"{len(small):,} sellers with fewer than {MIN_ORDERS} orders "
               f"({small['order_volume'].sum() / total_orders:.1%} of orders) are outside the tiers. "
               f"{SMALL_SELLER_ACTION} {(small['late_orders'] >= 2).sum()} of them have at least two "
               f"late handovers and {(small['late_orders'] >= 3).sum()} at least three.")


def show_priority_list(tiers, ranked):
    st.subheader("Whom to act on first")
    st.markdown("Focus-tier sellers ranked by **excess late handovers**: actual late handovers minus the "
                "number the same-month platform rate predicts.")
    n = st.slider("Number of sellers to show", min_value=5, max_value=len(ranked), value=TOP_N)
    top = ranked.head(n)
    st.markdown(f"These **{n}** sellers account for **{top_share(ranked, tiers, n):.0%}** of all positive "
                f"excess late handovers across the {len(tiers)} tiered sellers.")

    table = pd.DataFrame({
        "Rank": top["rank"],
        "Seller": top["seller_id"].str[:ID_CHARS],
        "Tier": top["tier"],
        "Orders": top["order_volume"],
        "Late handovers": top["late_orders"],
        "Late rate (%)": top["late_rate"] * 100,
        "Same-month platform rate (%)": top["benchmark_late_rate"] * 100,
        "Excess late handovers": top["excess_late"].round().astype(int),  # whole orders; avoids "-0"
    })
    # Height fits every selected row (35 px each plus the header), so the list needs no inner scrolling
    st.dataframe(table, hide_index=True, width="stretch", height=(n + 1) * 35 + 3, column_config={
        "Late rate (%)": st.column_config.NumberColumn(format="%.1f"),
        "Same-month platform rate (%)": st.column_config.NumberColumn(format="%.1f"),
    })
    # The download keeps the full seller IDs so the list can be handed to the seller team
    st.download_button("Download this list (CSV)", table.assign(Seller=top["seller_id"]).to_csv(index=False),
                       file_name=f"top_{n}_focus_sellers.csv", mime="text/csv")

    no_excess = ranked[ranked["excess_late"] <= 0]
    no_excess_tiers = " and ".join(str(t) for t in sorted(no_excess["tier"].unique()))
    st.caption(f"{len(no_excess)} focus sellers (Tier {no_excess_tiers}, median "
               f"{no_excess['order_volume'].median():.0f} orders) have no excess late handovers. "
               "They sit at the bottom of the list and stay on routine monitoring.")


def show_late_rate_chart(seller):
    labels = ["Seller", "Same-month platform"]
    rates = pd.DataFrame({
        "group": labels,
        "rate": [seller["late_rate"], seller["benchmark_late_rate"]],
    })
    st.vega_lite_chart(
        rates,
        {
            "title": {"text": "Late handover rate", "anchor": "start", "fontSize": 15},
            "height": 116,
            "encoding": {
                "y": {"field": "group", "type": "nominal", "sort": labels,
                      "axis": {"title": None, "labelLimit": 220, "labelFontSize": 13}},
                "x": {"field": "rate", "type": "quantitative",
                      "scale": {"zero": True, "rangeMax": {"expr": "width - 52"}},
                      "axis": {"title": None, "format": ".0%", "tickCount": 4, "labelFontSize": 11}},
            },
            "layer": [
                {
                    "mark": {"type": "bar", "height": 18},
                    "encoding": {"color": {"field": "group", "type": "nominal", "legend": None,
                                           "scale": {"domain": labels, "range": ["#6c4b94", "#b0a5b6"]}}},
                },
                {
                    "mark": {"type": "text", "align": "left", "dx": 6, "fontSize": 14,
                             "fontWeight": "bold", "color": "#34253f"},
                    "encoding": {"text": {"field": "rate", "type": "quantitative", "format": ".1%"}},
                },
            ],
        },
        width=680,
        alt=(f"Late handover rate for this seller: {seller['late_rate']:.1%}. "
             f"Same-month platform benchmark: {seller['benchmark_late_rate']:.1%}."),
    )


def show_tiered_seller(seller, ranked):
    tier = int(seller["tier"])
    in_focus = ranked[ranked["seller_id"] == seller["seller_id"]]
    focus_note = "focus tier" if not in_focus.empty else "not a focus tier"
    st.markdown(f"<h3><span style='color: {TIER_COLORS[tier]}'>●</span> Tier {tier} · {TIER_NAMES[tier]} "
                f"— {focus_note}</h3>", unsafe_allow_html=True)
    cols = st.columns(4)
    cols[0].metric("Orders", f"{seller['order_volume']:,}")
    cols[1].metric("Late handovers", f"{seller['late_orders']:,}")
    cols[2].metric("Late rate", f"{seller['late_rate']:.1%}",
                   f"{seller['late_rate_gap_pp']:+.1f} pp vs same-month platform "
                   f"({seller['benchmark_late_rate']:.1%})", delta_color="inverse")
    cols[3].metric("Excess late handovers", f"{int(round(seller['excess_late']))}")  # int() avoids "-0"
    show_late_rate_chart(seller)

    if not in_focus.empty:
        rank = int(in_focus["rank"].iloc[0])
        top_note = f", in the top {TOP_N}" if rank <= TOP_N else ""
        st.markdown(f"Rank **{rank}** of {len(ranked)} focus sellers{top_note}.")
        if seller["excess_late"] <= 0:
            st.markdown("This seller has no excess late handovers, so routine monitoring is enough.")
    st.info(f"**Action for Tier {tier}:** {TIER_ACTIONS[tier]}")
    if pd.notna(seller["avg_review_last"]):
        st.caption(f"Average rating: {seller['avg_review_last']:.2f} stars "
                   f"over {seller['reviewed_orders']:,} reviewed orders (last review per order).")


def show_small_seller(seller):
    st.markdown(f"### Outside the tiers (fewer than {MIN_ORDERS} orders)")
    cols = st.columns(4)
    cols[0].metric("Orders", f"{seller['order_volume']:,}")
    cols[1].metric("Late handovers", f"{seller['late_orders']:,}")
    st.info(SMALL_SELLER_ACTION)
    st.caption("No late rate is shown: with so few orders it is unreliable "
               "(one late order out of two is already 50%).")


def show_lookup(sellers_all, tiers, ranked):
    st.subheader("Which action fits a seller")
    query = st.text_input("Seller ID (the first 6 characters are enough)").strip().lower()
    if not query:
        return
    matches = sellers_all[sellers_all["seller_id"].str.startswith(query)]
    if matches.empty:
        st.warning("No seller in the main sample has this ID.")
        return
    seller_id = matches["seller_id"].iloc[0]
    if len(matches) > 1:
        seller_id = st.selectbox(f"{len(matches)} sellers match; choose one", matches["seller_id"])

    tiered = tiers[tiers["seller_id"] == seller_id]
    if tiered.empty:
        show_small_seller(sellers_all[sellers_all["seller_id"] == seller_id].iloc[0])
    else:
        show_tiered_seller(tiered.iloc[0], ranked)


st.set_page_config(page_title="Seller late-handover monitor", layout="wide")
sellers_all, tiers, ranked = load_data()

st.title("Seller late-handover monitor")
st.caption("Prototype · Olist marketplace · delivered single-seller orders, January 2017 – August 2018 · "
           "read-only view of the Q2 results in notebooks/03_q2.ipynb")

overview_tab, priority_tab, lookup_tab = st.tabs(["Overview", "Priority list", "Seller lookup"])
with overview_tab:
    show_overview(sellers_all, tiers, ranked)
with priority_tab:
    show_priority_list(tiers, ranked)
with lookup_tab:
    show_lookup(sellers_all, tiers, ranked)

st.divider()
st.caption(LIMITS)
