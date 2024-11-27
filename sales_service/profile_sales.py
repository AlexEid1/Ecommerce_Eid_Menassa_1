import cProfile
import pstats
from app import app

def profile_endpoint(client, method, path, json=None):
    """
    Profiles a specific endpoint by sending an HTTP request and printing the response.

    Args:
        client (FlaskClient): The Flask test client used to send the HTTP request.
        method (str): The HTTP method to use for the request ("POST", "GET", "DELETE").
        path (str): The path for the endpoint being requested.
        json (dict, optional): The JSON payload to send with the request (for "POST" method).

    Returns:
        Response: The Flask response object for the HTTP request.
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
    Main function to profile endpoints in the Sales Service.

    Initializes the cProfile profiler, runs a series of HTTP requests to simulate activity 
    on the Sales Service endpoints, and then displays profiling results. 

    The profiling includes:
    - A POST request to process a sale
    - A GET request to list available goods
    - A GET request to retrieve details of a specific good

    Profiling data is then displayed, showing the top 20 functions by cumulative time.
    """
    profiler = cProfile.Profile()

    # Start Flask test client
    with app.test_client() as client:
        # Start profiling
        profiler.enable()

        # Profile all endpoints in the Sales Service
        profile_endpoint(client, "POST", "/sales", json={
            "customer_id": 1,
            "good_id": 7,
            "quantity": 2
        })
        profile_endpoint(client, "GET", "/sales/goods")
        profile_endpoint(client, "GET", "/sales/goods/7")

        # Stop profiling
        profiler.disable()

    # Display the profiling results
    stats = pstats.Stats(profiler)
    stats.strip_dirs()
    stats.sort_stats("cumulative")
    stats.print_stats(20)  # Show top 20 functions by cumulative time
