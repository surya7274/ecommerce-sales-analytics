# feature_engineering.py – create analytical columns
"""
Purpose
-------
* Load the cleaned CSVs from ``data/processed/``.
* Derive useful features required for the business analysis:
  - order_month, order_year
  - delivery_days, delivery_delay_flag
  - order_value (sum of item price * qty + freight)
  - customer_lifetime_value (cumulative order_value per customer)
  - R‑F‑M scores & segment labels
  - customer_type (new vs repeat)
  - price_bucket (low/medium/high based on order_value)
* Save the enriched tables back to ``data/processed/`` with ``_feat`` suffixes.
"""

import os
from pathlib import Path
import pandas as pd
import numpy as np

RAW_PROCESSED = Path(__file__).resolve().parents[1] / "data" / "processed"

def load_cleaned(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW_PROCESSED / f"{name}_clean.csv")

def save_feat(df: pd.DataFrame, name: str) -> None:
    df.to_csv(RAW_PROCESSED / f"{name}_feat.csv", index=False)

def main():
    # Load tables
    orders = load_cleaned("orders")
    order_items = load_cleaned("order_items")
    customers = load_cleaned("customers")
    payments = load_cleaned("payments")
    reviews = load_cleaned("reviews")

    # ---------- 1. Temporal features ----------
    orders["order_date"] = pd.to_datetime(orders["order_date"], errors="coerce")
    orders["delivery_date"] = pd.to_datetime(orders["delivery_date"], errors="coerce")
    orders["order_month"] = orders["order_date"].dt.month
    orders["order_year"] = orders["order_date"].dt.year

    # ---------- 2. Delivery metrics ----------
    orders["delivery_days"] = (orders["delivery_date"] - orders["order_date"]).dt.days
    orders["delivery_delay_flag"] = (orders["delivery_days"] > 7).astype(int)

    # ---------- 3. Order value ----------
    # merge order_items to compute line totals
    order_items["line_total"] = order_items["price"] * order_items["quantity"]
    order_value = order_items.groupby("order_id")["line_total"].sum().reset_index()
    orders = orders.merge(order_value, on="order_id", how="left")
    orders["order_value"] = orders["line_total"] + orders.get("order_freight_value", 0)

    # ---------- 4. Customer lifetime value ----------
    cust_ltv = orders.groupby("customer_id")["order_value"].sum().reset_index()
    cust_ltv.rename(columns={"order_value": "customer_lifetime_value"}, inplace=True)
    customers = customers.merge(cust_ltv, on="customer_id", how="left").fillna(0)

    # ---------- 5. RFM scores ----------
    # Recency – days since last order
    reference_date = orders["order_date"].max()
    recency = orders.groupby("customer_id")["order_date"].max().reset_index()
    recency["recency_days"] = (reference_date - recency["order_date"]).dt.days
    # Frequency – number of orders
    frequency = orders.groupby("customer_id").size().reset_index(name="frequency")
    # Monetary – total spend
    monetary = cust_ltv.copy()
    rfm = recency.merge(frequency, on="customer_id").merge(monetary, on="customer_id")
    # Simple quantile‑based scoring (1‑5)
    rfm["R_score"] = pd.qcut(rfm["recency_days"], 5, labels=[5,4,3,2,1]).astype(int)
    rfm["F_score"] = pd.qcut(rfm["frequency"].replace(0, np.nan), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["M_score"] = pd.qcut(rfm["customer_lifetime_value"].replace(0, np.nan), 5, labels=[1,2,3,4,5]).astype(int)
    rfm["RFM_score"] = rfm["R_score"]*100 + rfm["F_score"]*10 + rfm["M_score"]
    # Segment mapping (example)
    def segment(row):
        if row["R_score"] >= 4 and row["F_score"] >= 4 and row["M_score"] >= 4:
            return "Champions"
        if row["R_score"] >= 3 and row["F_score"] >= 3:
            return "Loyal"
        if row["R_score"] <= 2:
            return "At Risk"
        return "Other"
    rfm["rfm_segment"] = rfm.apply(segment, axis=1)
    customers = customers.merge(rfm[["customer_id", "R_score", "F_score", "M_score", "RFM_score", "rfm_segment"]], on="customer_id", how="left")

    # ---------- 6. Customer type ----------
    customers["customer_type"] = np.where(customers["frequency"] > 1, "repeat", "new")

    # ---------- 7. Price bucket ----------
    bins = [-np.inf, 50, 200, np.inf]
    labels = ["low", "medium", "high"]
    orders["price_bucket"] = pd.cut(orders["order_value"], bins=bins, labels=labels)

    # Save enriched tables
    save_feat(orders, "orders")
    save_feat(customers, "customers")
    save_feat(order_items, "order_items")
    save_feat(payments, "payments")
    save_feat(reviews, "reviews")
    print("✅ Feature‑engineered tables saved to data/processed")

if __name__ == "__main__":
    main()
