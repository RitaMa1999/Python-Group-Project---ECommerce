"""Shared functions for the Q2 seller tiers, used by 03_q2.ipynb and 04_checks.ipynb."""
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42


def seller_metrics_from_orders(orders, late_col="late_handover"):
    """Build one row per seller from order-level data.

    `orders` needs `seller_id`, `order_purchase_month` and a boolean late column. The benchmark is
    the late rate the seller would have if each of its orders were late at the platform rate for
    that order's month (the same definition as 01_cleaning).
    """
    monthly_rate = orders.groupby("order_purchase_month")[late_col].mean()
    df = orders.assign(month_rate=orders["order_purchase_month"].map(monthly_rate))
    sellers = df.groupby("seller_id").agg(
        order_volume=(late_col, "size"),
        late_orders=(late_col, "sum"),
        benchmark_late_rate=("month_rate", "mean"),
    ).reset_index()
    sellers["late_rate"] = sellers["late_orders"] / sellers["order_volume"]
    return sellers


def make_features(sellers, scale="late_orders"):
    """Standardized features: late rate plus a log scale measure.

    scale="late_orders" uses log(1 + late orders), the main analysis.
    scale="order_volume" uses log(order volume), the earlier version kept for comparison.
    """
    if scale == "late_orders":
        scale_values = np.log1p(sellers["late_orders"])
    else:
        scale_values = np.log(sellers["order_volume"])
    raw = pd.DataFrame({"late_rate": sellers["late_rate"], "scale": scale_values})
    return StandardScaler().fit_transform(raw)


def fit_kmeans(X, k, random_state=RANDOM_STATE):
    """Fit K-means with k clusters and return the fitted model."""
    return KMeans(n_clusters=k, n_init=10, random_state=random_state).fit(X)


def order_tiers(sellers, labels):
    """Renumber cluster labels 1..k from the lowest to the highest mean late rate."""
    mean_rate = sellers.groupby(labels)["late_rate"].mean().sort_values()
    mapping = {old: new for new, old in enumerate(mean_rate.index, start=1)}
    return pd.Series(labels).map(mapping).to_numpy()


def assign_tiers(sellers, k, min_orders, scale="late_orders", random_state=RANDOM_STATE):
    """Keep sellers with at least `min_orders` orders and add a `tier` column (1 = least late)."""
    eligible = sellers[sellers["order_volume"] >= min_orders].reset_index(drop=True).copy()
    X = make_features(eligible, scale)
    labels = fit_kmeans(X, k, random_state).labels_
    eligible["tier"] = order_tiers(eligible, labels)
    return eligible


def add_excess(sellers):
    """Add expected and excess late handovers versus the same-month platform benchmark."""
    sellers = sellers.copy()
    sellers["expected_late"] = sellers["benchmark_late_rate"] * sellers["order_volume"]
    sellers["excess_late"] = sellers["late_orders"] - sellers["expected_late"]
    return sellers


def profile_tiers(sellers):
    """Summary table with one row per tier."""
    sellers = add_excess(sellers)
    prof = sellers.groupby("tier").agg(
        sellers=("seller_id", "count"),
        median_orders=("order_volume", "median"),
        median_late_orders=("late_orders", "median"),
        total_orders=("order_volume", "sum"),
        late_orders=("late_orders", "sum"),
        expected_late=("expected_late", "sum"),
    )
    prof["late_rate"] = prof["late_orders"] / prof["total_orders"]  # weighted by orders
    prof["gap_vs_same_month_pp"] = (prof["late_orders"] - prof["expected_late"]) / prof["total_orders"] * 100
    prof["share_of_sellers"] = prof["sellers"] / prof["sellers"].sum()
    prof["share_of_orders"] = prof["total_orders"] / prof["total_orders"].sum()
    prof["share_of_late_orders"] = prof["late_orders"] / prof["late_orders"].sum()
    return prof.drop(columns="expected_late")


def focus_tiers(profile):
    """Tiers whose late rate is above the same-month platform benchmark, most severe first."""
    focus = profile[profile["gap_vs_same_month_pp"] > 0].sort_values("late_rate", ascending=False)
    return list(focus.index)
