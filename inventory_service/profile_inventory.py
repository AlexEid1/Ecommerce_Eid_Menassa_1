import cProfile
import pstats
from app import app

def profile_endpoint(client, method, path, json=None):
    """Profiles a specific endpoint."""
    if method == "POST":
        response = client.post(path, json=json)
    elif method == "GET":
        response = client.get(path)
    elif method == "PUT":
        response = client.put(path, json=json)
    elif method == "DELETE":
        response = client.delete(path)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    print(f"Response for {method} {path}: {response.get_json()}")
    return response

if __name__ == "__main__":
    profiler = cProfile.Profile()

    # Start Flask test client
    with app.test_client() as client:
        # Start profiling
        profiler.enable()

        # Profile all endpoints in the Inventory Service
        profile_endpoint(client, "POST", "/inventory", json={
            "name": "Laptop",
            "category": "electronics",
            "price": 1000.0,
            "description": "High-end gaming laptop",
            "stock_count": 50
        })
        profile_endpoint(client, "GET", "/inventory")
        profile_endpoint(client, "GET", "/inventory/1")
        profile_endpoint(client, "PUT", "/inventory/1", json={
            "price": 950.0,
            "description": "Updated gaming laptop"
        })
        profile_endpoint(client, "POST", "/inventory/1/deduct", json={"quantity": 5})

        # Stop profiling
        profiler.disable()

    # Display the profiling results
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats(20)  # Show top 20 functions by cumulative time
