from app import app

def run_memory_profile():
    """
    Runs a series of HTTP requests to trigger memory profiling for all endpoints 
    in the Sales Service. It simulates the process of making a sale, displaying 
    available goods, and fetching the details of a specific good.

    The function uses the Flask test client to send requests to the application's endpoints:
    - A POST request to process a sale
    - A GET request to list all available goods
    - A GET request to retrieve details of a specific good

    Prints the JSON responses from each endpoint to the console.
    """
    with app.test_client() as client:
        # 1. Process a sale
        response = client.post('/sales', json={
            "customer_id": 1,
            "good_id": 1,
            "quantity": 2
        })
        print(f"POST /sales: {response.get_json()}")

        # 2. Display available goods
        response = client.get('/sales/goods')
        print(f"GET /sales/goods: {response.get_json()}")

        # 3. Get details of a specific good
        response = client.get('/sales/goods/1')
        print(f"GET /sales/goods/1: {response.get_json()}")

if __name__ == "__main__":
    run_memory_profile()
