"""
Generates a sample SQLite database (sample.db) for the demo environment.
This allows users to test the deployed app without needing a real Postgres DB.
"""
import os
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "sample.db"

def create_sample_db():
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create tables (SQLite dialect)
    c.executescript("""
    CREATE TABLE customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        region VARCHAR(50),
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(150) NOT NULL,
        category VARCHAR(80),
        price REAL NOT NULL,
        stock INTEGER DEFAULT 0
    );

    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id INTEGER REFERENCES customers(id),
        order_date DATE NOT NULL,
        total_amount REAL,
        status VARCHAR(30) DEFAULT 'completed'
    );

    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER REFERENCES orders(id),
        product_id INTEGER REFERENCES products(id),
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL
    );

    CREATE TABLE returns (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER REFERENCES orders(id),
        reason VARCHAR(200),
        returned_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );

    -- Views
    CREATE VIEW customer_revenue AS
    SELECT c.id, c.name, c.region,
           COUNT(o.id) AS total_orders,
           SUM(o.total_amount) AS total_revenue,
           MAX(o.order_date) AS last_order_date
    FROM customers c
    LEFT JOIN orders o ON o.customer_id = c.id
    GROUP BY c.id, c.name, c.region;
    """)

    # Insert Data
    customers = [
        ('Amit Sharma',    'amit@example.com',    'North'),
        ('Priya Singh',    'priya@example.com',   'South'),
        ('Rahul Verma',    'rahul@example.com',   'East'),
        ('Neha Gupta',     'neha@example.com',    'West'),
        ('Vikram Joshi',   'vikram@example.com',  'North'),
        ('Sunita Patel',   'sunita@example.com',  'South'),
        ('Arjun Mehta',    'arjun@example.com',   'East'),
        ('Kavya Reddy',    'kavya@example.com',   'West'),
        ('Suresh Kumar',   'suresh@example.com',  'North'),
        ('Ananya Das',     'ananya@example.com',  'South')
    ]
    c.executemany("INSERT INTO customers (name, email, region) VALUES (?, ?, ?)", customers)

    products = [
        ('Wireless Earbuds',    'Electronics',   2499.00, 150),
        ('Yoga Mat',            'Fitness',        899.00,  80),
        ('Python Book',         'Books',          599.00, 200),
        ('Running Shoes',       'Footwear',      3499.00,  60),
        ('Coffee Maker',        'Appliances',    4999.00,  40),
        ('Notebook Set',        'Stationery',    299.00,  300),
        ('Bluetooth Speaker',   'Electronics',  1999.00,  90),
        ('Resistance Bands',    'Fitness',       499.00,  120),
        ('SQL Cookbook',        'Books',         799.00,  100),
        ('Desk Lamp',           'Appliances',   1299.00,   75)
    ]
    c.executemany("INSERT INTO products (name, category, price, stock) VALUES (?, ?, ?, ?)", products)

    orders = [
        (1, '2024-01-05',  3398.00, 'completed'), (2, '2024-01-12',  4999.00, 'completed'),
        (3, '2024-02-03',   898.00, 'completed'), (4, '2024-02-18',  5998.00, 'completed'),
        (5, '2024-03-01',  2499.00, 'completed'), (6, '2024-03-14',  1398.00, 'completed'),
        (7, '2024-04-07',  4298.00, 'completed'), (8, '2024-04-22',   599.00, 'completed'),
        (9, '2024-05-10',  7498.00, 'completed'), (10,'2024-05-28',  2798.00, 'completed'),
        (1, '2024-06-03',  1299.00, 'completed'), (3, '2024-07-14',  3499.00, 'completed'),
        (5, '2024-08-09',   799.00, 'completed'), (2, '2024-09-21',  2498.00, 'completed'),
        (7, '2024-10-15',  4999.00, 'completed'), (4, '2024-11-02',  1798.00, 'completed'),
        (9, '2024-12-18',  5498.00, 'completed'), (6, '2025-01-06',   899.00, 'completed'),
        (10,'2025-01-19',  3998.00, 'completed'), (8, '2025-02-10',  2499.00, 'completed')
    ]
    c.executemany("INSERT INTO orders (customer_id, order_date, total_amount, status) VALUES (?, ?, ?, ?)", orders)

    order_items = [
        (1, 1, 1, 2499.00), (1, 6, 3,  299.00), (2, 5, 1, 4999.00), (3, 2, 1,  899.00),
        (4, 4, 1, 3499.00), (4, 1, 1, 2499.00), (5, 1, 1, 2499.00), (6, 6, 2,  299.00),
        (6, 8, 1,  499.00), (6, 3, 1, 599.00), (7, 4, 1, 3499.00), (7, 2, 1,  899.00),
        (8, 3, 1,  599.00), (9, 5, 1, 4999.00), (9, 7, 1, 1999.00), (9, 10,1,1299.00),
        (10,7, 1, 1999.00), (10,9, 1,  799.00), (11,10,1, 1299.00), (12,4, 1, 3499.00),
        (13,9, 1,  799.00), (14,1, 1, 2499.00), (15,5, 1, 4999.00), (16,6, 3,  299.00),
        (16,8, 2,  499.00), (17,5, 1, 4999.00), (17,2, 1,  899.00), (18,2, 1,  899.00),
        (19,4, 1, 3499.00), (19,3, 1,  599.00), (20,1, 1, 2499.00)
    ]
    c.executemany("INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)", order_items)

    returns = [
        (2,  'Item arrived damaged'), (7,  'Wrong size ordered'),
        (14, 'Changed mind'), (15, 'Product not as described')
    ]
    c.executemany("INSERT INTO returns (order_id, reason) VALUES (?, ?)", returns)

    conn.commit()
    conn.close()
    print(f"✅ Successfully created sample database at {DB_PATH}")

if __name__ == "__main__":
    create_sample_db()
