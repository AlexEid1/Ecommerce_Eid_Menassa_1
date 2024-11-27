import cProfile
import pstats
from app import app

def profile_endpoint(client, method, path, json=None):
    """
    Profiles a specific endpoint by sending an HTTP request and printing the response.

    This function sends a request (POST, GET, or DELETE) to a given path on the Flask 
    test client, and then prints out the JSON response. It is used to profile specific 
    endpoints for performance analysis.

    Args:
        client (FlaskClient): The Flask test client used to send HTTP requests.
        method (str): The HTTP method to use for the request (POST, GET, DELETE).
        path (str): The path of the endpoint to test.
        json (dict, optional): The JSON payload to send with the request (default is None).

    Returns:
        response (Flask Response): The response object returned by the Flask test client.
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
    Profiles the endpoints of the Reviews Service and displays the profiling results.

    This script starts a cProfile profiler, sends HTTP requests to the reviews service 
    endpoints using Flask's test client, and then stops the profiler. After the profiling 
    is completed, it prints the top 20 functions with the highest cumulative time, 
    which can be helpful for performance analysis.

    The following endpoints are profiled:
        - POST /reviews
        - GET /reviews/product/1
        - GET /reviews/customer/1
        - POST /reviews/1/moderate

    The profiler results can be used to identify performance bottlenecks in the endpoints.
    """
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
