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

def display_available_goods():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, name, price FROM inventory WHERE stock_count > 0")
        goods = cursor.fetchall()
        return jsonify(goods), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

def get_good_details(good_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM inventory WHERE id = %s", (good_id,))
        good = cursor.fetchone()
        if not good:
            return jsonify({"error": "Good not found"}), 404
        return jsonify(good), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

def process_sale(data):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        # Extract data
        customer_id = data['customer_id']
        good_id = data['good_id']
        quantity = data['quantity']

        # Check customer wallet balance
        cursor.execute("SELECT wallet_balance FROM customers WHERE id = %s", (customer_id,))
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        wallet_balance = customer[0]

        # Check good availability and price
        cursor.execute("SELECT stock_count, price FROM inventory WHERE id = %s", (good_id,))
        good = cursor.fetchone()
        if not good:
            return jsonify({"error": "Good not found"}), 404
        stock_count, price = good

        if stock_count < quantity:
            return jsonify({"error": "Insufficient stock"}), 400

        total_cost = price * quantity
        if wallet_balance < total_cost:
            return jsonify({"error": "Insufficient funds"}), 400

        # Deduct money from customer wallet
        cursor.execute("UPDATE customers SET wallet_balance = wallet_balance - %s WHERE id = %s", (total_cost, customer_id))

        # Deduct stock from inventory
        cursor.execute("UPDATE inventory SET stock_count = stock_count - %s WHERE id = %s", (quantity, good_id))

        # Record the sale
        cursor.execute(
            """INSERT INTO sales (customer_id, inventory_id, quantity, total_price) 
               VALUES (%s, %s, %s, %s)""",
            (customer_id, good_id, quantity, total_cost)
        )
        connection.commit()
        return jsonify({"message": "Sale processed successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()