from app import app
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

def run_profile():
    """Run all endpoints in the Customers Service to trigger memory profiling."""
    with app.test_client() as client:
        # 1. Register a customer
        response = client.post('/customers', json={
            "full_name": "John Doe",
            "username": "johndoe",
            "password": "password123",
            "age": 30,
            "address": "123 Main St",
            "gender": "male",
            "marital_status": "single"
        })
        print(f"POST /customers: {response.get_json()}")

        # 2. Get all customers
        response = client.get('/customers')
        print(f"GET /customers: {response.get_json()}")

        # 3. Get a specific customer by username
        response = client.get('/customers/johndoe')
        print(f"GET /customers/johndoe: {response.get_json()}")

        # 4. Charge the customer wallet
        response = client.post('/customers/1/charge', json={"amount": 100})
        print(f"POST /customers/1/charge: {response.get_json()}")

        # 5. Deduct from the customer wallet
        response = client.post('/customers/1/deduct', json={"amount": 50})
        print(f"POST /customers/1/deduct: {response.get_json()}")

        # 6. Delete the customer
        response = client.delete('/customers/1')
        print(f"DELETE /customers/1: {response.get_json()}")

if __name__ == "__main__":
    run_profile()
