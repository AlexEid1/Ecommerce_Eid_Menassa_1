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
    cursor.execute("DELETE FROM sales")
    cursor.execute("DELETE FROM inventory")
    cursor.execute("DELETE FROM customers")
    connection.commit()
    yield connection, cursor
    cursor.close()
    connection.close()

def test_display_available_goods(client, db_connection):
    connection, cursor = db_connection
    # Insert test data
    cursor.execute("""INSERT INTO inventory (name, category, price, description, stock_count)
                       VALUES ('Laptop', 'electronics', 1000.0, 'High-end gaming laptop', 50)""")
    connection.commit()

    # Get available goods
    response = client.get('/sales/goods')
    assert response.status_code == 200
    goods = response.json
    assert len(goods) == 1
    assert goods[0]['name'] == 'Laptop'
    assert float(goods[0]['price']) == 1000.0  # Price as float
    assert goods[0]['id'] is not None

def test_get_good_details(client, db_connection):
    connection, cursor = db_connection
    # Insert test data
    cursor.execute("""INSERT INTO inventory (name, category, price, description, stock_count)
                       VALUES ('Smartphone', 'electronics', 799.99, 'High-end smartphone', 30)""")
    connection.commit()

    item_id = cursor.lastrowid

    # Get good details
    response = client.get(f'/sales/goods/{item_id}')
    assert response.status_code == 200
    good = response.json
    assert good['name'] == 'Smartphone'
    assert good['category'] == 'electronics'
    assert float(good['price']) == 799.99  # Price as float
    assert good['stock_count'] == 30

def test_process_sale(client, db_connection):
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

    # Process a sale
    response = client.post('/sales', json={
        "customer_id": customer_id,
        "good_id": inventory_id,
        "quantity": 2
    })
    assert response.status_code == 200
    assert response.json['message'] == "Sale processed successfully!"

    # Verify customer wallet balance
    cursor.execute("SELECT wallet_balance FROM customers WHERE id = %s", (customer_id,))
    wallet_balance = cursor.fetchone()[0]
    assert wallet_balance == 0.0  # Initial balance 2000 - (1000 * 2)

    # Verify inventory stock count
    cursor.execute("SELECT stock_count FROM inventory WHERE id = %s", (inventory_id,))
    stock_count = cursor.fetchone()[0]
    assert stock_count == 8  # Initial stock 10 - 2

    # Verify sale record in the database
    cursor.execute("SELECT * FROM sales WHERE customer_id = %s AND inventory_id = %s", (customer_id, inventory_id))
    sale = cursor.fetchone()
    assert sale is not None
    assert sale[4] == 2  # Quantity
    assert sale[5] == 2000.0  # Total price
