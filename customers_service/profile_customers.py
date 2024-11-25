import cProfile
import pstats
from app import app

def profile_endpoint(client, method, path, json=None):
    """Profiles a specific endpoint."""
    if method == "POST":
        response = client.post(path, json=json)
    elif method == "GET":
        response = client.get(path)
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

        # Profile all endpoints in the Customers Service
        profile_endpoint(client, "POST", "/customers", json={
            "full_name": "John Doe",
            "username": "johndoe",
            "password": "password123",
            "age": 30,
            "address": "123 Main St",
            "gender": "male",
            "marital_status": "single"
        })
        profile_endpoint(client, "GET", "/customers")
        profile_endpoint(client, "GET", "/customers/johndoe")
        profile_endpoint(client, "POST", "/customers/1/charge", json={"amount": 100})
        profile_endpoint(client, "POST", "/customers/1/deduct", json={"amount": 50})
        profile_endpoint(client, "DELETE", "/customers/1")

        # Stop profiling
        profiler.disable()

    # Display the profiling results
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats(20)  # Show top 20 functions by cumulative time