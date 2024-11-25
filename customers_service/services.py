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

def register_customer(data):
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

def delete_customer(customer_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM customers WHERE id = %s", (customer_id,))
        connection.commit()
        return jsonify({"message": "Customer deleted successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

def update_customer_info(customer_id, data):
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

def get_all_customers():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM customers")
        customers = cursor.fetchall()
        return jsonify(customers), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

def get_customer_by_username(username):
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

def charge_wallet(customer_id, amount):
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

def deduct_wallet(customer_id, amount):
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
