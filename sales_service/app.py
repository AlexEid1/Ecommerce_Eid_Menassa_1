from flask import Flask, request, jsonify
from services import (
    display_available_goods, get_good_details, process_sale
)

app = Flask(__name__)

@app.route('/sales/goods', methods=['GET'])
def list_goods():
    return display_available_goods()

@app.route('/sales/goods/<int:good_id>', methods=['GET'])
def get_good(good_id):
    return get_good_details(good_id)

@app.route('/sales', methods=['POST'])
def make_sale():
    data = request.json
    return process_sale(data)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5003)