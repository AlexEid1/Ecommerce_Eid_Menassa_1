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
    Establishes a connection to the MySQL database using the provided configuration.

    Returns:
        mysql.connector.connection.MySQLConnection: Database connection object.

    Raises:
        RuntimeError: If the database connection fails.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        raise RuntimeError(f"Database connection failed: {str(e)}")

@profile
def register_customer(data):
    """
    Registers a new customer in the database.

    Args:
        data (dict): A dictionary containing customer details, including:
            - full_name (str): Full name of the customer.
            - username (str): Username of the customer.
            - password (str): Password for the customer.
            - age (int): Age of the customer.
            - address (str): Address of the customer.
            - gender (str): Gender of the customer.
            - marital_status (str): Marital status of the customer.

    Returns:
        Response: A JSON response indicating success or failure with a status code.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """INSERT INTO customers (full_name, username, password, age, address, gender, marital_status, wallet_balance)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (
            data['full_name'], data['username'], data['password'], data['age'], 
            data['address'], data['gender'], data['marital_status'], 0.0
        ))
        connection.commit()
        return jsonify({"message": "Customer registered successfully!"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@profile
def delete_customer(customer_id):
    """
    Marks a customer as deleted in the database.

    Args:
        customer_id (int): The ID of the customer to delete.

    Returns:
        Response: A JSON response indicating success or failure with a status code.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE customers SET status = 'deleted' WHERE id = %s", (customer_id,))
        connection.commit()
        return jsonify({"message": "Customer marked as deleted!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@profile
def update_customer_info(customer_id, data):
    """
    Updates the information of an existing customer.

    Args:
        customer_id (int): The ID of the customer to update.
        data (dict): A dictionary containing updated customer details.

    Returns:
        Response: A JSON response indicating success or failure with a status code.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = "UPDATE customers SET "
        query += ", ".join(f"{key} = %s" for key in data.keys())
        query += " WHERE id = %s"
        cursor.execute(query, (*data.values(), customer_id))
        connection.commit()
        return jsonify({"message": "Customer information updated successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@profile
def get_all_customers():
    """
    Retrieves a list of all active customers from the database.

    Returns:
        Response: A JSON response containing a list of active customers or an error message.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM customers WHERE status = 'active'")
        customers = cursor.fetchall()
        return jsonify(customers), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@profile
def get_customer_by_username(username):
    """
    Retrieves customer details based on the provided username.

    Args:
        username (str): The username of the customer to retrieve.

    Returns:
        Response: A JSON response containing customer details or an error message.
    """
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM customers WHERE username = %s", (username,))
        customer = cursor.fetchone()
        if not customer:
            return jsonify({"error": "Customer not found"}), 404
        return jsonify(customer), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@profile
def charge_wallet(customer_id, amount):
    """
    Adds funds to a customer's wallet.

    Args:
        customer_id (int): The ID of the customer.
        amount (float): The amount to add to the wallet.

    Returns:
        Response: A JSON response indicating success or failure with a status code.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("UPDATE customers SET wallet_balance = wallet_balance + %s WHERE id = %s", (amount, customer_id))
        connection.commit()
        return jsonify({"message": "Wallet charged successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

@profile
def deduct_wallet(customer_id, amount):
    """
    Deducts funds from a customer's wallet if sufficient balance exists.

    Args:
        customer_id (int): The ID of the customer.
        amount (float): The amount to deduct from the wallet.

    Returns:
        Response: A JSON response indicating success or failure with a status code.
    """
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT wallet_balance FROM customers WHERE id = %s", (customer_id,))
        wallet_balance = cursor.fetchone()[0]
        if wallet_balance < amount:
            return jsonify({"error": "Insufficient funds"}), 400
        cursor.execute("UPDATE customers SET wallet_balance = wallet_balance - %s WHERE id = %s", (amount, customer_id))
        connection.commit()
        return jsonify({"message": "Wallet deduction successful!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()
