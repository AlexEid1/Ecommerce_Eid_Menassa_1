from app import app

def run_memory_profile():
    """
    Run all endpoints in the Reviews Service to trigger memory profiling.
    
    This function simulates HTTP requests to the various endpoints of the Reviews Service 
    (submit a review, fetch reviews for a product or by a customer, and moderate a review) 
    using Flask's test client. The profiling data for each request is generated through 
    the memory profiling decorators applied to the functions in the app.
    
    It prints the JSON response for each HTTP request to validate the functionality.
    """
    with app.test_client() as client:
        # 1. Submit a new review
        response = client.post('/reviews', json={
            "customer_id": 1,
            "inventory_id": 1,
            "rating": 5,
            "comment": "Excellent product!"
        })
        print(f"POST /reviews: {response.get_json()}")

        # 2. Get all reviews for a product
        response = client.get('/reviews/product/1')
        print(f"GET /reviews/product/1: {response.get_json()}")

        # 3. Get all reviews by a customer
        response = client.get('/reviews/customer/1')
        print(f"GET /reviews/customer/1: {response.get_json()}")

        # 4. Moderate a review
        response = client.post('/reviews/1/moderate', json={"action": "approve"})
        print(f"POST /reviews/1/moderate: {response.get_json()}")

if __name__ == "__main__":
    run_memory_profile()
