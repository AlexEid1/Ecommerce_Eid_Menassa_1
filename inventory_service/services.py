from flask import jsonify
import mysql.connector
from mysql.connector import Error
import os
from memory_profiler import profile

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'rootpassword'),
    'database': os.getenv('DB_NAME', 'ecommerce')
}

def get_db_connection():
    """
    Establish a connection to the database using configuration from environment variables.

    Returns:
        connection: A MySQL database connection object if successful.
        jsonify(): JSON response with error message if the connection fails.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

@profile
def add_inventory_item(data):
    """
    Add a new item to the inventory.

    This function inserts a new item into the `inventory` table. It expects the following fields 
    in the request data: `name`, `category`, `price`, `description`, and `stock_count`.

    Args:
        data (dict): A dictionary containing the details of the item to be added.

    Returns:
        jsonify(): JSON response with success or error message.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """INSERT INTO inventory (name, category, price, description, stock_count)
                   VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(query, (
            data['name'], data['category'], data['price'], 
            data['description'], data['stock_count']
        ))
        connection.commit()
        return jsonify({"message": "Inventory item added successfully!"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@profile
def get_all_items():
    """
    Retrieve a list of all inventory items.

    This function queries the `inventory` table and returns all items available.

    Returns:
        jsonify(): JSON response with a list of all inventory items or an error message.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM inventory")
        items = cursor.fetchall()
        return jsonify(items), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@profile
def get_item_by_id(item_id):
    """
    Retrieve details of a specific inventory item by its ID.

    This function queries the `inventory` table for a specific item identified by `item_id`.

    Args:
        item_id (int): The unique identifier of the inventory item.

    Returns:
        jsonify(): JSON response with item details if found, or an error message if not found.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM inventory WHERE id = %s", (item_id,))
        item = cursor.fetchone()
        if not item:
            return jsonify({"error": "Item not found"}), 404
        return jsonify(item), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@profile
def update_item_details(item_id, data):
    """
    Update the details of an inventory item.

    This function updates the fields of an inventory item identified by `item_id` with the provided data.

    Args:
        item_id (int): The unique identifier of the inventory item.
        data (dict): A dictionary of fields to update (e.g., name, category, price, etc.).

    Returns:
        jsonify(): JSON response indicating success or failure of the update operation.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = "UPDATE inventory SET "
        query += ", ".join(f"{key} = %s" for key in data.keys())
        query += " WHERE id = %s"
        cursor.execute(query, (*data.values(), item_id))
        connection.commit()
        return jsonify({"message": "Item updated successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@profile
def deduct_item_stock(item_id, quantity):
    """
    Deduct a specified quantity of stock from an inventory item.

    This function updates the stock count of an inventory item identified by `item_id` by deducting the 
    specified `quantity` from its existing stock.

    Args:
        item_id (int): The unique identifier of the inventory item.
        quantity (int): The amount of stock to deduct from the item.

    Returns:
        jsonify(): JSON response indicating success or failure of the deduction operation.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT stock_count FROM inventory WHERE id = %s", (item_id,))
        stock_count = cursor.fetchone()[0]
        if stock_count < quantity:
            return jsonify({"error": "Insufficient stock"}), 400
        cursor.execute("UPDATE inventory SET stock_count = stock_count - %s WHERE id = %s", (quantity, item_id))
        connection.commit()
        return jsonify({"message": "Stock deducted successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()
