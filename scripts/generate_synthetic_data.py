import os
import uuid
import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Helper to generate a random date within the last N years
def random_date(start, end):
    return start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)

NUM_CUSTOMERS = 5000
NUM_PRODUCTS = 1000
NUM_ORDERS = 20000

# Generate customers
customers = pd.DataFrame({
    "customer_id": [str(uuid.uuid4()) for _ in range(NUM_CUSTOMERS)],
    "customer_name": [f"Customer {i}" for i in range(1, NUM_CUSTOMERS + 1)],
    "customer_email": [f"customer{i}@example.com" for i in range(1, NUM_CUSTOMERS + 1)],
    "city": np.random.choice(["Sao Paulo", "Rio de Janeiro", "Belo Horizonte", "Porto Alegre"], NUM_CUSTOMERS),
    "state": np.random.choice(["SP", "RJ", "MG", "RS"], NUM_CUSTOMERS),
    "signup_date": [random_date(datetime(2017, 1, 1), datetime(2022, 12, 31)).date() for _ in range(NUM_CUSTOMERS)],
})

# Generate products
categories = ["Electronics", "Clothing", "Home & Kitchen", "Sports", "Books"]
products = pd.DataFrame({
    "product_id": [str(uuid.uuid4()) for _ in range(NUM_PRODUCTS)],
    "product_name": [f"Product {i}" for i in range(1, NUM_PRODUCTS + 1)],
    "category": np.random.choice(categories, NUM_PRODUCTS),
    "price": np.round(np.random.uniform(5, 500, NUM_PRODUCTS),
})

# Generate orders
order_statuses = ["delivered", "canceled", "shipped", "in_transit"]
orders = []
order_items = []
payments = []
reviews = []

for i in range(1, NUM_ORDERS + 1):
    order_id = str(uuid.uuid4())
    cust = customers.sample(1).iloc[0]
    order_date = random_date(datetime(2018, 1, 1), datetime(2023, 8, 31))
    # delivery date (2-15 days later) unless canceled
    delivery_delay = random.randint(2, 15)
    delivery_date = order_date + timedelta(days=delivery_delay)
    status = np.random.choice(order_statuses, p=[0.7, 0.05, 0.15, 0.1])
    orders.append({
        "order_id": order_id,
        "customer_id": cust["customer_id"],
        "order_date": order_date,
        "delivery_date": delivery_date if status == "delivered" else None,
        "order_status": status,
    })

    # Number of items in the order (1-5)
    n_items = random.randint(1, 5)
    for _ in range(n_items):
        prod = products.sample(1).iloc[0]
        qty = random.randint(1, 3)
        order_items.append({
            "order_id": order_id,
            "product_id": prod["product_id"],
            "quantity": qty,
            "price": prod["price"],
        })

    # Payment record
    payments.append({
        "payment_id": str(uuid.uuid4()),
        "order_id": order_id,
        "payment_type": np.random.choice(["credit_card", "boleto", "debit", "voucher"]),
        "payment_value": sum(item["price"] * item["quantity"] for item in order_items if item["order_id"] == order_id),
        "payment_installments": random.choice([1, 2, 3, 6, 12]),
        "payment_timestamp": order_date + timedelta(hours=random.randint(1, 48)),
    })

    # Optional review (20% chance if delivered)
    if status == "delivered" and random.random() < 0.2:
        reviews.append({
            "review_id": str(uuid.uuid4()),
            "order_id": order_id,
            "review_score": random.randint(1, 5),
            "review_comment": "Auto‑generated review",
            "review_timestamp": delivery_date + timedelta(days=random.randint(0, 30)),
        })

# Convert to DataFrames
orders_df = pd.DataFrame(orders)
order_items_df = pd.DataFrame(order_items)
payments_df = pd.DataFrame(payments)
reviews_df = pd.DataFrame(reviews)

# Output directory
output_dir = os.path.join(os.path.dirname(__file__), "..", "data", "raw")
os.makedirs(output_dir, exist_ok=True)

# Save CSVs
customers.to_csv(os.path.join(output_dir, "customers.csv"), index=False)
products.to_csv(os.path.join(output_dir, "products.csv"), index=False)
orders_df.to_csv(os.path.join(output_dir, "orders.csv"), index=False)
order_items_df.to_csv(os.path.join(output_dir, "order_items.csv"), index=False)
payments_df.to_csv(os.path.join(output_dir, "payments.csv"), index=False)
reviews_df.to_csv(os.path.join(output_dir, "reviews.csv"), index=False)

print("Synthetic data generated in", output_dir)
