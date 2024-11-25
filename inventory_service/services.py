from flask import jsonify
import mysql.connector
from mysql.connector import Error
import os

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'rootpassword'),
    'database': os.getenv('DB_NAME', 'ecommerce')
}

def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

def add_inventory_item(data):
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

def get_all_items():
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

def get_item_by_id(item_id):
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

def update_item_details(item_id, data):
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

def deduct_item_stock(item_id, quantity):
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