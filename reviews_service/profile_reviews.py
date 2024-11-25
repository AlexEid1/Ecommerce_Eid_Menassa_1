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

        # Profile all endpoints in the Reviews Service
        profile_endpoint(client, "POST", "/reviews", json={
            "customer_id": 1,
            "inventory_id": 1,
            "rating": 5,
            "comment": "Excellent product!"
        })
        profile_endpoint(client, "GET", "/reviews/product/1")
        profile_endpoint(client, "GET", "/reviews/customer/1")
        profile_endpoint(client, "POST", "/reviews/1/moderate", json={
            "action": "approve"
        })

        # Stop profiling
        profiler.disable()

    # Display the profiling results
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats(20)  # Show top 20 functions by cumulative time
