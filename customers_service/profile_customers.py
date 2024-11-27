import cProfile
import pstats
from app import app

def profile_endpoint(client, method, path, json=None):
    """
    Profile a specific API endpoint.

    This function sends an HTTP request to the specified API endpoint using the
    Flask test client and logs the response.

    Args:
        client (FlaskClient): The Flask test client used to send requests.
        method (str): The HTTP method to use (e.g., "POST", "GET", "DELETE").
        path (str): The endpoint path (e.g., "/customers").
        json (dict, optional): The JSON payload to include in the request body (for POST requests).

    Returns:
        Response: The response object from the Flask test client.

    Raises:
        ValueError: If an unsupported HTTP method is specified.
    """
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
    """
    Main script for profiling API endpoints.

    This script uses Python's `cProfile` to profile the performance of all major
    endpoints in the Customers Service. It sends simulated HTTP requests to
    various endpoints using the Flask test client, collects profiling data, and
    prints the top 20 functions by cumulative time.

    Steps:
    1. Initialize the Flask test client.
    2. Profile the performance of each endpoint by sending HTTP requests.
    3. Generate and display profiling results.

    Example:
        Run this script directly to profile endpoints:
        $ python profile_script.py
    """
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
