import pytest
import mysql.connector
from app import app

# Database configuration for the test database
TEST_DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,  # Port for test database
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
    yield connection, cursor
    # Cleanup after each test
    cursor.execute("DELETE FROM customers")
    connection.commit()
    cursor.close()
    connection.close()

def test_register_customer(client, db_connection):
    connection, cursor = db_connection
    # Register a new customer
    response = client.post('/customers', json={
        "full_name": "John Doe",
        "username": "johndoe",
        "password": "password123",
        "age": 30,
        "address": "123 Main St",
        "gender": "male",
        "marital_status": "single"
    })
    assert response.status_code == 201
    assert response.json['message'] == "Customer registered successfully!"

    # Verify data in the database
    cursor.execute("SELECT * FROM customers WHERE username = 'johndoe'")
    customer = cursor.fetchone()
    assert customer is not None
    assert customer[1] == "John Doe"  # Full name

def test_get_all_customers(client, db_connection):
    connection, cursor = db_connection
    # Insert test data
    cursor.execute("""INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance, status)
                       VALUES ('John Doe', 'johndoe', 'password123', 30, '123 Main St', 'male', 'single', 0, 'active')""")
    connection.commit()

    # Get all customers
    response = client.get('/customers')
    assert response.status_code == 200
    customers = response.json
    assert len(customers) == 1
    assert customers[0]['username'] == 'johndoe'

def test_get_customer_by_username(client, db_connection):
    connection, cursor = db_connection
    # Insert test data
    cursor.execute("""INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance, status)
                       VALUES ('Jane Doe', 'janedoe', 'password456', 28, '456 Elm St', 'female', 'married', 50, 'active')""")
    connection.commit()

    # Get customer by username
    response = client.get('/customers/janedoe')
    assert response.status_code == 200
    customer = response.json
    assert customer['username'] == 'janedoe'
    assert customer['full_name'] == 'Jane Doe'

def test_charge_customer_wallet(client, db_connection):
    connection, cursor = db_connection
    # Insert test data
    cursor.execute("""INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance, status)
                       VALUES ('John Doe', 'johndoe', 'password123', 30, '123 Main St', 'male', 'single', 0, 'active')""")
    connection.commit()

    customer_id = cursor.lastrowid

    # Charge the customer's wallet
    response = client.post(f'/customers/{customer_id}/charge', json={"amount": 100})
    assert response.status_code == 200
    assert response.json['message'] == "Wallet charged successfully!"

    # Verify the updated wallet balance
    cursor.execute("SELECT wallet_balance FROM customers WHERE id = %s", (customer_id,))
    wallet_balance = cursor.fetchone()[0]
    assert wallet_balance == 100.0

def test_deduct_customer_wallet(client, db_connection):
    connection, cursor = db_connection
    # Insert test data
    cursor.execute("""INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance, status)
                       VALUES ('John Doe', 'johndoe', 'password123', 30, '123 Main St', 'male', 'single', 200, 'active')""")
    connection.commit()

    customer_id = cursor.lastrowid

    # Deduct from the customer's wallet
    response = client.post(f'/customers/{customer_id}/deduct', json={"amount": 50})
    assert response.status_code == 200
    assert response.json['message'] == "Wallet deduction successful!"

    # Verify the updated wallet balance
    cursor.execute("SELECT wallet_balance FROM customers WHERE id = %s", (customer_id,))
    wallet_balance = cursor.fetchone()[0]
    assert wallet_balance == 150.0

def test_delete_customer(client, db_connection):
    connection, cursor = db_connection
    # Insert test data
    cursor.execute("""INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance, status)
                       VALUES ('John Doe', 'johndoe', 'password123', 30, '123 Main St', 'male', 'single', 0, 'active')""")
    connection.commit()

    customer_id = cursor.lastrowid

    # Delete the customer
    response = client.delete(f'/customers/{customer_id}')
    assert response.status_code == 200
    assert response.json['message'] == "Customer marked as deleted!"

    # Verify the status in the database
    cursor.execute("SELECT status FROM customers WHERE id = %s", (customer_id,))
    status = cursor.fetchone()[0]
    assert status == 'deleted'
