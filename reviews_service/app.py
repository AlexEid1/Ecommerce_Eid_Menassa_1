from flask import Flask, request, jsonify
from auth_permissions import generate_token
from services import get_db_connection
from services import (
    submit_review, update_review, delete_review,
    get_product_reviews, get_customer_reviews, 
    moderate_review, get_review_details
)

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    # Fetch user from database
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM customers WHERE username = %s", (username,))
    user = cursor.fetchone()
    cursor.close()
    connection.close()

    if not user or user["password"] != password:
        return jsonify({"error": "Invalid credentials"}), 401

    token = generate_token(user["id"], user["role"])
    return jsonify({"token": token, "mfa_enabled": user["mfa_enabled"]}), 200

@app.route('/reviews', methods=['POST'])
def create_review():
    """
    Creates a new product review.

    This endpoint allows a customer to submit a review for a product.
    
    Args:
        request.json (dict): The JSON data containing review information.
        
    Returns:
        Response: A JSON response indicating success or failure.
    """
    data = request.json
    return submit_review(data)

@app.route('/reviews/<int:review_id>', methods=['PUT'])
def modify_review(review_id):
    """
    Updates an existing review.

    This endpoint allows the modification of an existing review by its ID.
    
    Args:
        review_id (int): The ID of the review to be updated.
        request.json (dict): The JSON data containing updated review information.
        
    Returns:
        Response: A JSON response indicating success or failure.
    """
    data = request.json
    return update_review(review_id, data)

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def remove_review(review_id):
    """
    Deletes a review by its ID.

    This endpoint allows the removal of a review from the system by its ID.
    
    Args:
        review_id (int): The ID of the review to be deleted.
        
    Returns:
        Response: A JSON response indicating success or failure.
    """
    return delete_review(review_id)

@app.route('/reviews/product/<int:product_id>', methods=['GET'])
def list_product_reviews(product_id):
    """
    Lists all reviews for a specific product.

    This endpoint retrieves all reviews for a given product by its product ID.
    
    Args:
        product_id (int): The ID of the product to retrieve reviews for.
        
    Returns:
        Response: A JSON response containing a list of reviews for the product.
    """
    return get_product_reviews(product_id)

@app.route('/reviews/customer/<int:customer_id>', methods=['GET'])
def list_customer_reviews(customer_id):
    """
    Lists all reviews written by a specific customer.

    This endpoint retrieves all reviews written by a customer by their customer ID.
    
    Args:
        customer_id (int): The ID of the customer to retrieve reviews for.
        
    Returns:
        Response: A JSON response containing a list of reviews written by the customer.
    """
    return get_customer_reviews(customer_id)

@app.route('/reviews/<int:review_id>/moderate', methods=['POST'])
def review_moderation(review_id):
    """
    Moderates a review.

    This endpoint allows moderators to approve or reject a review based on the provided action.
    
    Args:
        review_id (int): The ID of the review to be moderated.
        request.json (dict): The JSON data containing the action to be taken (e.g., 'approve', 'reject').
        
    Returns:
        Response: A JSON response indicating the moderation action was successful.
    """
    action = request.json.get('action')
    return moderate_review(review_id, action)

@app.route('/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    """
    Retrieves the details of a specific review by its ID.

    This endpoint retrieves detailed information about a specific review based on the review ID.
    
    Args:
        review_id (int): The ID of the review to retrieve details for.
        
    Returns:
        Response: A JSON response containing the review details.
    """
    return get_review_details(review_id)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5004)
