from app import app

def run_memory_profile():
    """Run all endpoints in the Sales Service to trigger memory profiling."""
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
