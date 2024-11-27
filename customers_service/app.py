from flask import Flask, request, jsonify
from services import (
    register_customer, delete_customer, update_customer_info, 
    get_all_customers, get_customer_by_username, 
    charge_wallet, deduct_wallet
)
import os

app = Flask(__name__)

# Database configuration from environment variables
app.config['DB_HOST'] = os.getenv('DB_HOST', 'localhost')
app.config['DB_USER'] = os.getenv('DB_USER', 'root')
app.config['DB_PASSWORD'] = os.getenv('DB_PASSWORD', 'rootpassword')
app.config['DB_NAME'] = os.getenv('DB_NAME', 'ecommerce')

@app.route('/customers', methods=['POST'])
def create_customer():
    """
    Create a new customer.

    This endpoint accepts customer details in JSON format and registers a new customer.

    Returns:
        Response: The response from the `register_customer` service containing 
                  the customer creation status.
    """
    data = request.json
    return register_customer(data)

@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def remove_customer(customer_id):
    """
    Delete a customer.

    This endpoint deletes a customer based on the provided customer ID.

    Args:
        customer_id (int): The unique ID of the customer to be deleted.

    Returns:
        Response: The response from the `delete_customer` service containing 
                  the deletion status.
    """
    return delete_customer(customer_id)

@app.route('/customers/<int:customer_id>', methods=['PUT'])
def modify_customer(customer_id):
    """
    Update customer information.

    This endpoint updates the information of a specific customer.

    Args:
        customer_id (int): The unique ID of the customer to be updated.

    Returns:
        Response: The response from the `update_customer_info` service 
                  containing the update status.
    """
    data = request.json
    return update_customer_info(customer_id, data)

@app.route('/customers', methods=['GET'])
def list_customers():
    """
    Get a list of all customers.

    This endpoint retrieves a list of all registered customers.

    Returns:
        Response: A JSON list of all customers from the `get_all_customers` service.
    """
    return get_all_customers()

@app.route('/customers/<string:username>', methods=['GET'])
def get_customer(username):
    """
    Get customer by username.

    This endpoint retrieves customer information based on the provided username.

    Args:
        username (str): The username of the customer to retrieve.

    Returns:
        Response: The customer details from the `get_customer_by_username` service.
    """
    return get_customer_by_username(username)

@app.route('/customers/<int:customer_id>/charge', methods=['POST'])
def add_funds(customer_id):
    """
    Charge a customer's wallet.

    This endpoint adds funds to the customer's wallet.

    Args:
        customer_id (int): The unique ID of the customer to charge.
        amount (float): The amount to be added to the wallet (from JSON payload).

    Returns:
        Response: The response from the `charge_wallet` service containing the 
                  charge status.
    """
    amount = request.json.get('amount')
    return charge_wallet(customer_id, amount)

@app.route('/customers/<int:customer_id>/deduct', methods=['POST'])
def reduce_funds(customer_id):
    """
    Deduct funds from a customer's wallet.

    This endpoint removes funds from the customer's wallet.

    Args:
        customer_id (int): The unique ID of the customer.
        amount (float): The amount to be deducted from the wallet (from JSON payload).

    Returns:
        Response: The response from the `deduct_wallet` service containing 
                  the deduction status.
    """
    amount = request.json.get('amount')
    return deduct_wallet(customer_id, amount)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
