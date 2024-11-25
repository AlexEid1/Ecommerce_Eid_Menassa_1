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

def submit_review(data):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """INSERT INTO reviews (customer_id, inventory_id, rating, comment) 
                   VALUES (%s, %s, %s, %s)"""
        cursor.execute(query, (
            data['customer_id'], data['inventory_id'], data['rating'], data['comment']
        ))
        connection.commit()
        return jsonify({"message": "Review submitted successfully!"}), 201
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

def update_review(review_id, data):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = "UPDATE reviews SET "
        query += ", ".join(f"{key} = %s" for key in data.keys())
        query += " WHERE id = %s"
        cursor.execute(query, (*data.values(), review_id))
        connection.commit()
        return jsonify({"message": "Review updated successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

def delete_review(review_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM reviews WHERE id = %s", (review_id,))
        connection.commit()
        return jsonify({"message": "Review deleted successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

def get_product_reviews(product_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM reviews WHERE inventory_id = %s", (product_id,))
        reviews = cursor.fetchall()
        return jsonify(reviews), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

def get_customer_reviews(customer_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM reviews WHERE customer_id = %s", (customer_id,))
        reviews = cursor.fetchall()
        return jsonify(reviews), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

def moderate_review(review_id, action):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        if action not in ["approve", "flag"]:
            return jsonify({"error": "Invalid action"}), 400
        status = "approved" if action == "approve" else "flagged"
        cursor.execute("UPDATE reviews SET status = %s WHERE id = %s", (status, review_id))
        connection.commit()
        return jsonify({"message": f"Review {status} successfully!"}), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()

def get_review_details(review_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM reviews WHERE id = %s", (review_id,))
        review = cursor.fetchone()
        if not review:
            return jsonify({"error": "Review not found"}), 404
        return jsonify(review), 200
    except Error as e:
        return jsonify({"error": str(e)}), 400
    finally:
        cursor.close()
        connection.close()