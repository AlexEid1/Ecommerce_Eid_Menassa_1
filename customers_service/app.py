from flask import Flask, request, jsonify
from services import (
    register_customer, delete_customer, update_customer_info, 
    get_all_customers, get_customer_by_username, 
    charge_wallet, deduct_wallet
)

app = Flask(__name__)

@app.route('/customers', methods=['POST'])
def create_customer():
    data = request.json
    return register_customer(data)

@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def remove_customer(customer_id):
    return delete_customer(customer_id)

@app.route('/customers/<int:customer_id>', methods=['PUT'])
def modify_customer(customer_id):
    data = request.json
    return update_customer_info(customer_id, data)

@app.route('/customers', methods=['GET'])
def list_customers():
    return get_all_customers()

@app.route('/customers/<string:username>', methods=['GET'])
def get_customer(username):
    return get_customer_by_username(username)

@app.route('/customers/<int:customer_id>/charge', methods=['POST'])
def add_funds(customer_id):
    amount = request.json.get('amount')
    return charge_wallet(customer_id, amount)

@app.route('/customers/<int:customer_id>/deduct', methods=['POST'])
def reduce_funds(customer_id):
    amount = request.json.get('amount')
    return deduct_wallet(customer_id, amount)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5001)
