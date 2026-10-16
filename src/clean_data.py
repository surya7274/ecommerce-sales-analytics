# clean_data.py
"""Data cleaning module.
Loads raw CSV files, performs type conversion, handles missing values, removes duplicates, and standardizes text.
Outputs cleaned CSVs to `data/processed/`.
"""

import os
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def load_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(RAW_DIR / f"{name}.csv")

def save_csv(df: pd.DataFrame, name: str):
    df.to_csv(PROCESSED_DIR / f"{name}.csv", index=False)

def clean_customers(df: pd.DataFrame) -> pd.DataFrame:
    # Convert signup_date to datetime
    df["signup_date"] = pd.to_datetime(df["signup_date"], errors="coerce")
    # Standardize state names (title case)
    df["customer_state"] = df["customer_state"].str.title()
    # Drop rows with missing critical fields
    df = df.dropna(subset=["customer_id", "customer_name", "customer_email", "signup_date"])
    # Remove duplicate customer_id
    df = df.drop_duplicates(subset="customer_id")
    return df

def clean_products(df: pd.DataFrame) -> pd.DataFrame:
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df = df.dropna(subset=["product_id", "product_name", "price"])
    df = df.drop_duplicates(subset="product_id")
    df["category"] = df["category"].str.title()
    return df

def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    date_cols = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    for col in date_cols:
        df[col] = pd.to_datetime(df[col], errors="coerce")
    df = df.dropna(subset=["order_id", "customer_id", "order_purchase_timestamp"])
    df = df.drop_duplicates(subset="order_id")
    df["order_status"] = df["order_status"].str.lower()
    return df

def clean_order_items(df: pd.DataFrame) -> pd.DataFrame:
    df["price"] = pd.to_numeric(df["price"], errors="coerce")
    df["freight_value"] = pd.to_numeric(df["freight_value"], errors="coerce")
    df["shipping_limit_date"] = pd.to_datetime(df["shipping_limit_date"], errors="coerce")
    df = df.dropna(subset=["order_item_id", "order_id", "product_id", "price"])
    df = df.drop_duplicates(subset="order_item_id")
    return df

def clean_payments(df: pd.DataFrame) -> pd.DataFrame:
    df["payment_value"] = pd.to_numeric(df["payment_value"], errors="coerce")
    df = df.dropna(subset=["order_id", "payment_type", "payment_value"])
    return df

def clean_reviews(df: pd.DataFrame) -> pd.DataFrame:
    df["review_creation_date"] = pd.to_datetime(df["review_creation_date"], errors="coerce")
    df["review_answer_timestamp"] = pd.to_datetime(df["review_answer_timestamp"], errors="coerce")
    df = df.dropna(subset=["order_id", "review_id", "review_score"])
    return df

def main():
    customers = clean_customers(load_csv("customers"))
    save_csv(customers, "customers_clean")

    products = clean_products(load_csv("products"))
    save_csv(products, "products_clean")

    orders = clean_orders(load_csv("orders"))
    save_csv(orders, "orders_clean")

    order_items = clean_order_items(load_csv("order_items"))
    save_csv(order_items, "order_items_clean")

    payments = clean_payments(load_csv("payments"))
    save_csv(payments, "payments_clean")

    reviews = clean_reviews(load_csv("order_reviews"))
    save_csv(reviews, "reviews_clean")

if __name__ == "__main__":
    main()
