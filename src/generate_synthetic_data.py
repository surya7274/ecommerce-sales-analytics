import csv
import os
import random
import uuid
from datetime import datetime, timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
os.makedirs(RAW_DIR, exist_ok=True)

NUM_CUSTOMERS = 20000
NUM_PRODUCTS = 5000
NUM_ORDERS = 50000

# Helper functions
def random_date(start, end):
    return start + timedelta(days=random.randint(0, (end - start).days))

def random_string(length=8):
    return ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=length))

# Customers
customers_path = os.path.join(RAW_DIR, 'customers.csv')
with open(customers_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['customer_id', 'customer_name', 'customer_email', 'customer_state', 'customer_city', 'customer_zipcode', 'signup_date'])
    for i in range(1, NUM_CUSTOMERS + 1):
        name = f"{random_string(5)} {random_string(7)}"
        email = f"{random_string(6).lower()}@example.com"
        state = random.choice(['Delhi', 'Maharashtra', 'Karnataka', 'Tamil Nadu', 'West Bengal'])
        city = random.choice(['CityA', 'CityB', 'CityC'])
        zipcode = f"{random.randint(100000, 999999)}"
        signup = random_date(datetime(2020, 1, 1), datetime(2023, 12, 31)).date()
        writer.writerow([i, name, email, state, city, zipcode, signup])

# Products
def random_price():
    return round(random.uniform(5, 500), 2)

categories = ['Electronics', 'Clothing', 'Home', 'Sports', 'Books', 'Beauty']
products_path = os.path.join(RAW_DIR, 'products.csv')
with open(products_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['product_id', 'product_name', 'category', 'price'])
    for i in range(1, NUM_PRODUCTS + 1):
        product_name = f"{random_string(4)} {random_string(6)}"
        writer.writerow([i, product_name, random.choice(categories), random_price()])

# Orders
order_statuses = ['delivered', 'shipped', 'canceled', 'processing']
orders_path = os.path.join(RAW_DIR, 'orders.csv')
with open(orders_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['order_id', 'customer_id', 'order_status', 'order_purchase_timestamp', 'order_approved_at', 'order_delivered_carrier_date', 'order_delivered_customer_date', 'order_estimated_delivery_date'])
    for i in range(1, NUM_ORDERS + 1):
        cust_id = random.randint(1, NUM_CUSTOMERS)
        purchase = random_date(datetime(2020, 1, 1), datetime(2023, 12, 31))
        approved = purchase + timedelta(days=random.randint(0, 2))
        carrier = purchase + timedelta(days=random.randint(2, 6))
        customer = purchase + timedelta(days=random.randint(3, 10))
        estimated = purchase + timedelta(days=7)
        writer.writerow([i, cust_id, random.choice(order_statuses), purchase, approved, carrier, customer, estimated])

# Order Items
order_items_path = os.path.join(RAW_DIR, 'order_items.csv')
with open(order_items_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['order_item_id', 'order_id', 'product_id', 'seller_id', 'shipping_limit_date', 'price', 'freight_value', 'quantity'])
    order_item_id = 1
    for order_id in range(1, NUM_ORDERS + 1):
        num_items = random.randint(1, 5)
        for _ in range(num_items):
            prod_id = random.randint(1, NUM_PRODUCTS)
            price = random_price()
            freight = round(random.uniform(0, 20), 2)
            quantity = random.randint(1, 3)
            # For shipping limit, use estimated delivery - 1 day (approx)
            shipping_limit = datetime.strptime('2022-01-15', '%Y-%m-%d')  # placeholder date
            writer.writerow([order_item_id, order_id, prod_id, random.randint(1, 5000), shipping_limit, price, freight, quantity])
            order_item_id += 1

# Payments
payment_types = ['credit_card', 'boleto', 'debit_card', 'voucher']
payments_path = os.path.join(RAW_DIR, 'payments.csv')
with open(payments_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['order_id', 'payment_type', 'payment_installments', 'payment_value'])
    for order_id in range(1, NUM_ORDERS + 1):
        writer.writerow([order_id, random.choice(payment_types), random.randint(1, 12), round(random.uniform(20, 2000), 2)])

# Reviews
reviews_path = os.path.join(RAW_DIR, 'order_reviews.csv')
with open(reviews_path, 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['order_id', 'review_id', 'review_score', 'review_comment_title', 'review_comment_message', 'review_creation_date', 'review_answer_timestamp'])
    for order_id in range(1, NUM_ORDERS + 1):
        if random.random() < 0.8:
            review_id = uuid.uuid4().hex[:12]
            score = random.randint(1, 5)
            title = f"Title {random_string(5)}" if score >= 4 else ''
            message = f"Message {random_string(10)}" if random.random() < 0.5 else ''
            # Use order delivered date as creation date placeholder
            creation = datetime(2022, 1, 1) + timedelta(days=random.randint(0, 1000))
            answer = creation + timedelta(days=random.randint(0, 7))
            writer.writerow([order_id, review_id, score, title, message, creation, answer])

print('Synthetic CSV data generated in', RAW_DIR)
