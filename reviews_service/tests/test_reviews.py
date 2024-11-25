import pytest
import mysql.connector
from app import app

# Database configuration for the test database
TEST_DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': 'rootpassword',
    'database': 'ecommerce'
}

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def db_connection():
    connection = mysql.connector.connect(**TEST_DB_CONFIG)
    cursor = connection.cursor()
    # Cleanup: Delete all rows before the test starts
    cursor.execute("DELETE FROM reviews")
    cursor.execute("DELETE FROM inventory")
    cursor.execute("DELETE FROM customers")
    connection.commit()
    yield connection, cursor
    cursor.close()
    connection.close()

def test_submit_review(client, db_connection):
    connection, cursor = db_connection
    # Insert test data: Customer
    cursor.execute("""INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance, status)
                       VALUES ('John Doe', 'johndoe', 'password123', 30, '123 Main St', 'male', 'single', 2000, 'active')""")
    customer_id = cursor.lastrowid

    # Insert test data: Inventory
    cursor.execute("""INSERT INTO inventory (name, category, price, description, stock_count)
                       VALUES ('Laptop', 'electronics', 1000.0, 'High-end gaming laptop', 10)""")
    inventory_id = cursor.lastrowid
    connection.commit()

    # Submit a review
    response = client.post('/reviews', json={
        "customer_id": customer_id,
        "inventory_id": inventory_id,
        "rating": 5,
        "comment": "Excellent product!"
    })
    assert response.status_code == 201
    assert response.json['message'] == "Review submitted successfully!"

    # Verify review in the database
    cursor.execute("SELECT * FROM reviews WHERE customer_id = %s AND inventory_id = %s", (customer_id, inventory_id))
    review = cursor.fetchone()
    assert review is not None
    assert review[3] == 5  # Rating
    assert review[4] == "Excellent product!"  # Comment

def test_get_product_reviews(client, db_connection):
    connection, cursor = db_connection
    # Insert test data: Customer
    cursor.execute("""INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance, status)
                       VALUES ('Jane Doe', 'janedoe', 'password456', 28, '456 Elm St', 'female', 'married', 1000, 'active')""")
    customer_id = cursor.lastrowid

    # Insert test data: Inventory
    cursor.execute("""INSERT INTO inventory (name, category, price, description, stock_count)
                       VALUES ('Smartphone', 'electronics', 799.99, 'High-end smartphone', 20)""")
    inventory_id = cursor.lastrowid

    # Insert a review
    cursor.execute("""INSERT INTO reviews (customer_id, inventory_id, rating, comment, status)
                       VALUES (%s, %s, 4, 'Great product!', 'approved')""", (customer_id, inventory_id))
    connection.commit()

    # Get product reviews
    response = client.get(f'/reviews/product/{inventory_id}')
    assert response.status_code == 200
    reviews = response.json
    assert len(reviews) == 1
    assert reviews[0]['rating'] == 4
    assert reviews[0]['comment'] == "Great product!"

def test_get_customer_reviews(client, db_connection):
    connection, cursor = db_connection
    # Insert test data: Customer
    cursor.execute("""INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance, status)
                       VALUES ('John Doe', 'johndoe', 'password123', 30, '123 Main St', 'male', 'single', 2000, 'active')""")
    customer_id = cursor.lastrowid

    # Insert test data: Inventory
    cursor.execute("""INSERT INTO inventory (name, category, price, description, stock_count)
                       VALUES ('Tablet', 'electronics', 499.99, 'High-end tablet', 15)""")
    inventory_id = cursor.lastrowid

    # Insert a review
    cursor.execute("""INSERT INTO reviews (customer_id, inventory_id, rating, comment, status)
                       VALUES (%s, %s, 5, 'Amazing tablet!', 'approved')""", (customer_id, inventory_id))
    connection.commit()

    # Get customer reviews
    response = client.get(f'/reviews/customer/{customer_id}')
    assert response.status_code == 200
    reviews = response.json
    assert len(reviews) == 1
    assert reviews[0]['rating'] == 5
    assert reviews[0]['comment'] == "Amazing tablet!"

def test_moderate_review(client, db_connection):
    connection, cursor = db_connection
    # Insert test data: Customer and Inventory
    cursor.execute("""INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance, status)
                       VALUES ('John Doe', 'johndoe', 'password123', 30, '123 Main St', 'male', 'single', 2000, 'active')""")
    customer_id = cursor.lastrowid
    cursor.execute("""INSERT INTO inventory (name, category, price, description, stock_count)
                       VALUES ('Laptop', 'electronics', 1000.0, 'High-end gaming laptop', 10)""")
    inventory_id = cursor.lastrowid

    # Insert a review
    cursor.execute("""INSERT INTO reviews (customer_id, inventory_id, rating, comment, status)
                       VALUES (%s, %s, 3, 'Good but expensive.', 'flagged')""", (customer_id, inventory_id))
    review_id = cursor.lastrowid
    connection.commit()

    # Moderate the review (approve)
    response = client.post(f'/reviews/{review_id}/moderate', json={"action": "approve"})
    assert response.status_code == 200
    assert response.json['message'] == "Review approved successfully!"

    # Verify moderation in the database
    cursor.execute("SELECT status FROM reviews WHERE id = %s", (review_id,))
    status = cursor.fetchone()[0]
    assert status == "approved"
