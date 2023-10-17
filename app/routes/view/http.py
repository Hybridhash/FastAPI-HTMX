import httpx


# Creating a middleware for the fastapi user to handle the errors in backend 
# Response will be provided to HTML response model in view for rendering the page
async def get_login_http(username: str, password: str) -> httpx.Response:
    # Create an HTTP client
    client = httpx.AsyncClient()
    try:
        # Make the HTTP request with the credentials
        response = await client.post(
            "http://localhost:8080/auth/jwt/login",
            data={"grant_type": "", "username": username, "password": password, "scope": "", "client_id": "", "client_secret": ""},
        )
        # Check the response status code
        if response.status_code == 204:
            print("Login successful!")
            # print(response.headers["set-cookie"])
            # Extract the cookie value from the set-cookie header
            # cookie = http.cookies.SimpleCookie(response.headers["set-cookie"])["fastapiusersauth"].value
            # print(cookie)
        else:
            print("Login failed.")
            print(f"Error: {response.status_code} - {response.text}")

        return response
    finally:
        # Close the HTTP client
        await client.aclose()