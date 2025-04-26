# Pico-W-login
# MicroPython Web Server with Basic Authentication and Dashboard

This MicroPython code implements a simple web server that runs on Pico W and provides basic user authentication and a dashboard.

## Functionality

1.  **Wi-Fi Connection:**
    * The `connect_wifi()` function establishes a connection to a specified Wi-Fi network using the provided SSID and password.
    * It prints connection status messages and the assigned IP address to the serial console.

2.  **HTTP Request Parsing:**
    * The `parse_http_request(request)` function takes a raw HTTP request string as input.
    * It parses the request line to extract the HTTP method (GET, POST, etc.), the requested path (URL), and HTTP version.
    * It then parses the header lines and stores them in a dictionary.
    * For POST requests, it extracts the data from the request body and stores it in a dictionary.

3.  **Request Handling:**
    * The `handle_request(client)` function is the core logic for processing incoming HTTP requests from a client.
    * It first parses the received request using `parse_http_request()`.
    * **Authentication:**
        * It checks for a session cookie in the request headers. If a valid session cookie is found, the user is considered logged in.
        * For requests to the root path (`/`) with the POST method, it attempts to authenticate the user by comparing the submitted username and password with the hardcoded `USERS` dictionary.
        * Upon successful login, it generates a simple session ID, stores it in the `sessions` dictionary (in-memory), and sets a session cookie in the HTTP response.
        * If login fails, it displays the login page with an error message.
    * **Dashboard:**
        * If the requested path is `/dashboard` and the user is logged in (either via successful login or a valid session cookie), it serves a basic dashboard page.
        * The dashboard displays placeholder data for temperature, date/time, and power consumption. **Note:** This data is currently hardcoded.
    * **Logout:**
        * If the requested path is `/logout`, it checks for a session cookie. If found, it removes the session from the `sessions` dictionary and clears the session cookie on the client's browser, effectively logging the user out.
    * **Login Page:**
        * For GET requests to the root path (`/`), it serves the login page.
    * **404 Not Found:**
        * For any other unrecognized path, it returns a "404 Not Found" error.
    * Finally, it encodes the HTTP response and sends it back to the client before closing the connection.

4.  **Main Execution:**
    * The `if __name__ == "__main__":` block executes when the script is run directly.
    * It calls `connect_wifi()` to establish a Wi-Fi connection.
    * It initializes an empty dictionary `sessions` to store user session information. **Note:** This is a very basic in-memory session store and will be lost on device reset.
    * It creates a socket, binds it to port 80 (the standard HTTP port) on all available interfaces (`'0.0.0.0'`), and starts listening for incoming connections.
    * The `while True:` loop continuously accepts incoming client connections.
    * For each connection, it calls `handle_request()` in a `try...except...finally` block to handle the request and ensure the client connection is closed even if errors occur.

![Screenshot 2025-04-26 155236](https://github.com/user-attachments/assets/945a680c-e707-4d33-a9d5-a54b2602b497)
## Important Security Considerations


* **Insecure User Credentials:** The `USERS` dictionary stores usernames and passwords in plain text directly in the code. **This is highly insecure and should never be used in a production environment.** For real applications, you should use proper password hashing (e.g., bcrypt, Argon2) and a more secure way to manage user accounts.
* **Basic Session Management:** The session management is very basic, relying on in-memory storage and simple session IDs. It lacks features like session expiration, regeneration, and protection against certain types of session attacks.
* **No HTTPS:** The server serves content over plain HTTP, which means all communication, including login credentials and session cookies, is transmitted unencrypted. For any sensitive information, **HTTPS should be used.**

This code provides a fundamental example of a web server with authentication on a MicroPython platform. It can be expanded upon with more features, better security practices, and integration with actual hardware sensors and actuators.
