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
    cursor.execute("DELETE FROM inventory")
    connection.commit()
    yield connection, cursor
    cursor.close()
    connection.close()

def test_add_inventory_item(client, db_connection):
    connection, cursor = db_connection
    # Add a new inventory item
    response = client.post('/inventory', json={
        "name": "Laptop",
        "category": "electronics",
        "price": 1000.0,
        "description": "High-end gaming laptop",
        "stock_count": 50
    })
    assert response.status_code == 201
    assert response.json['message'] == "Inventory item added successfully!"

    # Verify the item in the database
    cursor.execute("SELECT * FROM inventory WHERE name = 'Laptop'")
    item = cursor.fetchone()
    assert item is not None
    assert item[1] == "Laptop"  # Name
    assert item[2] == "electronics"  # Category
    assert item[3] == 1000.0  # Price
    assert item[4] == "High-end gaming laptop"  # Description
    assert item[5] == 50  # Stock count

def test_get_all_inventory(client, db_connection):
    connection, cursor = db_connection
    # Insert test data
    cursor.execute("""INSERT INTO inventory (name, category, price, description, stock_count)
                       VALUES ('Laptop', 'electronics', 1000.0, 'Gaming Laptop', 50)""")
    connection.commit()

    # Get all inventory items
    response = client.get('/inventory')
    assert response.status_code == 200
    items = response.json
    assert len(items) == 1
    assert items[0]['name'] == 'Laptop'
    assert items[0]['category'] == 'electronics'
    assert float(items[0]['price']) == 1000.0

def test_get_inventory_item_by_id(client, db_connection):
    connection, cursor = db_connection
    # Insert test data
    cursor.execute("""INSERT INTO inventory (name, category, price, description, stock_count)
                       VALUES ('Smartphone', 'electronics', 799.99, 'High-end smartphone', 30)""")
    connection.commit()

    item_id = cursor.lastrowid

    # Get inventory item by ID
    response = client.get(f'/inventory/{item_id}')
    assert response.status_code == 200
    item = response.json
    assert item['name'] == 'Smartphone'
    assert item['category'] == 'electronics'
    assert float(item['price']) == 799.99
    assert item['stock_count'] == 30

def test_update_inventory_item(client, db_connection):
    connection, cursor = db_connection
    # Insert test data
    cursor.execute("""INSERT INTO inventory (name, category, price, description, stock_count)
                       VALUES ('Laptop', 'electronics', 1000.0, 'Gaming Laptop', 50)""")
    connection.commit()

    item_id = cursor.lastrowid

    # Update the inventory item
    response = client.put(f'/inventory/{item_id}', json={
        "price": 950.0,
        "description": "Updated high-end gaming laptop"
    })
    assert response.status_code == 200
    assert response.json['message'] == "Item updated successfully!"

    # Verify the updated data in the database
    cursor.execute("SELECT price, description FROM inventory WHERE id = %s", (item_id,))
    updated_item = cursor.fetchone()
    assert updated_item[0] == 950.0  # Updated price
    assert updated_item[1] == "Updated high-end gaming laptop"  # Updated description

def test_deduct_inventory_stock(client, db_connection):
    connection, cursor = db_connection
    # Insert test data
    cursor.execute("""INSERT INTO inventory (name, category, price, description, stock_count)
                       VALUES ('Laptop', 'electronics', 1000.0, 'Gaming Laptop', 50)""")
    connection.commit()

    item_id = cursor.lastrowid

    # Deduct stock
    response = client.post(f'/inventory/{item_id}/deduct', json={"quantity": 5})
    assert response.status_code == 200
    assert response.json['message'] == "Stock deducted successfully!"

    # Verify the updated stock count in the database
    cursor.execute("SELECT stock_count FROM inventory WHERE id = %s", (item_id,))
    stock_count = cursor.fetchone()[0]
    assert stock_count == 45  # Original stock (50) - Deducted stock (5)
