from flask import jsonify
import mysql.connector
from mysql.connector import Error
from mysql.connector.errors import IntegrityError
import re
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
    Establishes and returns a connection to the MySQL database.

    This function retrieves the database connection using the configuration stored in
    environment variables. It handles exceptions and returns an error message if the 
    connection fails.
    
    Returns:
        connection (mysql.connector.connection.MySQLConnection): The database connection.
        or
        jsonify (dict): Error message in case of failure.
    """
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        return jsonify({"error": f"Database connection failed: {str(e)}"}), 500

@profile
def validate_review_input(data):
    """Validate and sanitize review inputs."""
    required_fields = ["customer_id", "inventory_id", "rating", "comment"]

    # Ensure all required fields are present
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"

    # Validate customer_id and inventory_id (must be integers)
    if not isinstance(data["customer_id"], int) or data["customer_id"] <= 0:
        return False, "Invalid customer_id. It must be a positive integer."
    if not isinstance(data["inventory_id"], int) or data["inventory_id"] <= 0:
        return False, "Invalid inventory_id. It must be a positive integer."

    # Validate rating (must be an integer between 1 and 5)
    if not isinstance(data["rating"], int) or not (1 <= data["rating"] <= 5):
        return False, "Invalid rating. It must be an integer between 1 and 5."

    # Validate comment (must be a non-empty string, sanitized for harmful content)
    if not isinstance(data["comment"], str) or len(data["comment"].strip()) == 0:
        return False, "Invalid comment. It must be a non-empty string."
    if re.search(r"[<>]", data["comment"]):  # Basic XSS prevention
        return False, "Comment contains invalid characters."

    # All validations passed
    return True, "Valid input."

@profile
def submit_review(data):
    """
    Submits a new review to the database.

    This function takes in review data and inserts it into the 'reviews' table in the database.
    The review includes customer ID, product (inventory) ID, rating, and comment.

    Args:
        data (dict): Review data containing customer_id, inventory_id, rating, and comment.

    Returns:
        jsonify (dict): Success message or error message in case of failure.
    """
    is_valid, message = validate_review_input(data)
    if not is_valid:
        return jsonify({"error": message}), 400

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        query = """INSERT INTO reviews (customer_id, inventory_id, rating, comment, status)
                   VALUES (%s, %s, %s, %s, 'approved')"""
        cursor.execute(query, (
            data["customer_id"],
            data["inventory_id"],
            data["rating"],
            data["comment"]
        ))
        connection.commit()
        return jsonify({"message": "Review submitted successfully!"}), 201
    except IntegrityError as e:
        return jsonify({"error": "Database error: " + str(e)}), 400
    except Exception as e:
        return jsonify({"error": "An unexpected error occurred."}), 500
    finally:
        cursor.close()
        connection.close()


@profile
def update_review(review_id, data):
    """
    Updates an existing review in the database.

    This function updates the review details based on the provided review ID. The fields 
    in the review (like rating, comment) are updated according to the provided data.

    Args:
        review_id (int): The ID of the review to be updated.
        data (dict): The new review data to update.

    Returns:
        jsonify (dict): Success message or error message in case of failure.
    """
    
    is_valid, message = validate_review_input(data)
    if not is_valid:
        return jsonify({"error": message}), 400
    
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

@profile
def delete_review(review_id):
    """
    Deletes a review from the database.

    This function deletes a review from the 'reviews' table based on the provided review ID.

    Args:
        review_id (int): The ID of the review to be deleted.

    Returns:
        jsonify (dict): Success message or error message in case of failure.
    """
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

@profile
def get_product_reviews(product_id):
    """
    Retrieves all reviews for a specific product.

    This function fetches all reviews related to a product from the 'reviews' table based
    on the provided product (inventory) ID.

    Args:
        product_id (int): The ID of the product for which to retrieve reviews.

    Returns:
        jsonify (list): A list of reviews for the specified product or an error message.
    """
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

@profile
def get_customer_reviews(customer_id):
    """
    Retrieves all reviews written by a specific customer.

    This function fetches all reviews written by a customer from the 'reviews' table based
    on the provided customer ID.

    Args:
        customer_id (int): The ID of the customer for which to retrieve reviews.

    Returns:
        jsonify (list): A list of reviews written by the specified customer or an error message.
    """
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

@profile
def moderate_review(review_id, action):
    """
    Moderates a review based on a given action (approve or flag).

    This function updates the status of a review based on the moderation action: either
    approve or flag the review.

    Args:
        review_id (int): The ID of the review to be moderated.
        action (str): The action to take, either "approve" or "flag".

    Returns:
        jsonify (dict): Success message or error message in case of failure.
    """
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

@profile
def get_review_details(review_id):
    """
    Retrieves the details of a specific review.

    This function fetches detailed information about a specific review based on its review ID.

    Args:
        review_id (int): The ID of the review to retrieve.

    Returns:
        jsonify (dict): The review details or an error message if not found.
    """
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
