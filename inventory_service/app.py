from flask import Flask, request, jsonify
from services import (
    add_inventory_item, get_all_items, get_item_by_id,
    update_item_details, deduct_item_stock
)

app = Flask(__name__)

@app.route('/inventory', methods=['POST'])
def create_item():
    data = request.json
    return add_inventory_item(data)

@app.route('/inventory', methods=['GET'])
def list_items():
    return get_all_items()

@app.route('/inventory/<int:item_id>', methods=['GET'])
def get_item(item_id):
    return get_item_by_id(item_id)

@app.route('/inventory/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    data = request.json
    return update_item_details(item_id, data)

@app.route('/inventory/<int:item_id>/deduct', methods=['POST'])
def deduct_stock(item_id):
    quantity = request.json.get('quantity')
    return deduct_item_stock(item_id, quantity)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)