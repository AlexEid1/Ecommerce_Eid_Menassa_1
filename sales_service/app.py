from flask import Flask, request, jsonify
from services import (
    display_available_goods, get_good_details, process_sale
)

app = Flask(__name__)

@app.route('/sales/goods', methods=['GET'])
def list_goods():
    """
    Endpoint to retrieve a list of available goods for sale.

    This endpoint calls the `display_available_goods` function to fetch all the 
    goods that are currently available for sale and returns them as a JSON response.

    Returns:
        Response: A JSON response containing the list of available goods.
    """
    return display_available_goods()

@app.route('/sales/goods/<int:good_id>', methods=['GET'])
def get_good(good_id):
    """
    Endpoint to retrieve the details of a specific good.

    This endpoint takes a good's ID as a URL parameter, calls the `get_good_details`
    function to fetch the details of that good, and returns the details in the 
    response.

    Args:
        good_id (int): The ID of the good whose details are to be fetched.

    Returns:
        Response: A JSON response containing the details of the specific good.
    """
    return get_good_details(good_id)

@app.route('/sales', methods=['POST'])
def make_sale():
    """
    Endpoint to process a sale.

    This endpoint accepts a JSON payload with the sale information, calls the
    `process_sale` function to handle the sale process, and returns a response 
    indicating the success or failure of the transaction.

    Args:
        data (dict): The sale information, including customer and good details, 
                     passed as a JSON payload in the POST request.

    Returns:
        Response: A JSON response indicating whether the sale was processed 
                  successfully or if there was an error.
    """
    data = request.json
    return process_sale(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5003)
