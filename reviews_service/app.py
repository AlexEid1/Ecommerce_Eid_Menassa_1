from flask import Flask, request, jsonify
from services import (
    submit_review, update_review, delete_review,
    get_product_reviews, get_customer_reviews, 
    moderate_review, get_review_details
)

app = Flask(__name__)

@app.route('/reviews', methods=['POST'])
def create_review():
    data = request.json
    return submit_review(data)

@app.route('/reviews/<int:review_id>', methods=['PUT'])
def modify_review(review_id):
    data = request.json
    return update_review(review_id, data)

@app.route('/reviews/<int:review_id>', methods=['DELETE'])
def remove_review(review_id):
    return delete_review(review_id)

@app.route('/reviews/product/<int:product_id>', methods=['GET'])
def list_product_reviews(product_id):
    return get_product_reviews(product_id)

@app.route('/reviews/customer/<int:customer_id>', methods=['GET'])
def list_customer_reviews(customer_id):
    return get_customer_reviews(customer_id)

@app.route('/reviews/<int:review_id>/moderate', methods=['POST'])
def review_moderation(review_id):
    action = request.json.get('action')
    return moderate_review(review_id, action)

@app.route('/reviews/<int:review_id>', methods=['GET'])
def get_review(review_id):
    return get_review_details(review_id)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5004)