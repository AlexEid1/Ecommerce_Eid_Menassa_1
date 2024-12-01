from flask import jsonify
import mysql.connector
from mysql.connector import Error
import os
from memory_profiler import profile
from auth_permissions import mfa_required, role_required

# Database configuration from environment variables
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'rootpassword'),
    'database': os.getenv('DB_NAME', 'ecommerce')
}

def get_db_connection():
    """
    Establishes a connection to the database using the configuration 
    specified in the DB_CONFIG dictionary.

    Returns:
        connection: A MySQL connection object if successful.
        response (tuple): A JSON response with an error message and a 500 status code if the connection fails.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

@profile
def display_available_goods():
    """
    Retrieves a list of goods that are currently available for sale, 
    i.e., goods with stock_count greater than zero. This is done by querying 
    the 'inventory' table in the database.

    Returns:
        response (tuple): A JSON response containing a list of available goods and a 200 status code.
        response (tuple): A JSON response with an error message and a 400 status code if the query fails.
    """
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

@profile
def get_good_details(good_id):
    """
    Retrieves the details of a specific good from the 'inventory' table based on the given good ID.

    Args:
        good_id (int): The ID of the good whose details need to be fetched.

    Returns:
        response (tuple): A JSON response containing the details of the good and a 200 status code if found.
        response (tuple): A JSON response with an error message and a 404 status code if the good is not found.
        response (tuple): A JSON response with an error message and a 400 status code if the query fails.
    """
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

@profile
@mfa_required
def process_sale(data):
    """
    Processes a sale by verifying customer wallet balance, checking good availability, 
    updating the inventory, and recording the sale in the 'sales' table.

    Args:
        data (dict): A dictionary containing the sale information, including customer_id, 
                     good_id, and quantity.

    Returns:
        response (tuple): A JSON response with a success message and a 200 status code if the sale is processed successfully.
        response (tuple): A JSON response with an error message and a 400 or 404 status code if the sale fails.
    """
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
