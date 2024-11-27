from app import app
from werkzeug.test import EnvironBuilder
from werkzeug.wrappers import Request

def run_memory_profile():
    """
    Run all endpoints in the Inventory Service to trigger memory profiling.

    This function simulates a series of API requests to the Inventory Service:
    1. POST request to add a new inventory item.
    2. GET request to retrieve all inventory items.
    3. GET request to retrieve a specific inventory item by ID.
    4. PUT request to update an existing inventory item's details.
    5. POST request to deduct stock from an inventory item.

    Each request is followed by printing the response JSON to the console.
    This function is used to profile memory consumption during the API operations.
    """
    with app.test_client() as client:
        # 1. Add an inventory item
        response = client.post('/inventory', json={
            "name": "Laptop",
            "category": "electronics",
            "price": 1000.0,
            "description": "High-end gaming laptop",
            "stock_count": 50
        })
        print(f"POST /inventory: {response.get_json()}")

        # 2. Get all inventory items
        response = client.get('/inventory')
        print(f"GET /inventory: {response.get_json()}")

        # 3. Get a specific inventory item by ID
        response = client.get('/inventory/1')
        print(f"GET /inventory/1: {response.get_json()}")

        # 4. Update an inventory item
        response = client.put('/inventory/1', json={
            "price": 950.0,
            "description": "Updated gaming laptop"
        })
        print(f"PUT /inventory/1: {response.get_json()}")

        # 5. Deduct stock from an inventory item
        response = client.post('/inventory/1/deduct', json={"quantity": 5})
        print(f"POST /inventory/1/deduct: {response.get_json()}")

if __name__ == "__main__":
    run_memory_profile()
