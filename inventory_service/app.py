from flask import Flask, request, jsonify
from services import (
    add_inventory_item, get_all_items, get_item_by_id,
    update_item_details, deduct_item_stock
)

app = Flask(__name__)

@app.route('/inventory', methods=['POST'])
def create_item():
    """
    Create a new inventory item.

    This endpoint allows the user to add a new item to the inventory.
    The request body must include item details in JSON format.

    Example JSON:
    {
        "name": "Item Name",
        "description": "Item Description",
        "price": 100.0,
        "quantity": 50
    }

    Returns:
        JSON response indicating success or failure.
    """
    data = request.json
    return add_inventory_item(data)

@app.route('/inventory', methods=['GET'])
def list_items():
    """
    Retrieve a list of all inventory items.

    This endpoint returns a list of all items in the inventory.

    Returns:
        JSON response with a list of inventory items.
    """
    return get_all_items()

@app.route('/inventory/<int:item_id>', methods=['GET'])
def get_item(item_id):
    """
    Retrieve details of a specific inventory item.

    This endpoint returns the details of an item identified by its ID.

    Args:
        item_id (int): The unique ID of the inventory item.

    Returns:
        JSON response with item details or an error if the item is not found.
    """
    return get_item_by_id(item_id)

@app.route('/inventory/<int:item_id>', methods=['PUT'])
def update_item(item_id):
    """
    Update details of a specific inventory item.

    This endpoint updates the details of an item identified by its ID.
    The request body must include the updated details in JSON format.

    Example JSON:
    {
        "name": "Updated Name",
        "price": 120.0,
        "quantity": 40
    }

    Args:
        item_id (int): The unique ID of the inventory item.

    Returns:
        JSON response indicating success or failure.
    """
    data = request.json
    return update_item_details(item_id, data)

@app.route('/inventory/<int:item_id>/deduct', methods=['POST'])
def deduct_stock(item_id):
    """
    Deduct stock quantity from an inventory item.

    This endpoint decreases the stock quantity of an item identified by its ID.
    The request body must include the quantity to deduct.

    Example JSON:
    {
        "quantity": 10
    }

    Args:
        item_id (int): The unique ID of the inventory item.

    Returns:
        JSON response indicating success or failure.
    """
    quantity = request.json.get('quantity')
    return deduct_item_stock(item_id, quantity)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5002)