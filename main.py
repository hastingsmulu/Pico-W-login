import network
import socket
import time
from machine import Pin
import urandom # For generating slightly better session IDs

# WiFi credentials (replace with your actual credentials)
WIFI_SSID = "wifi"
WIFI_PASSWORD = "your wifi password"

temperature = 25.5 # Replace with actual sensor reading
now = time.localtime()
date_time = "{}-{:02d}-{:02d} {:02d}:{:02d}:{:02d}".format(now[0], now[1], now[2], now[3], now[4], now[5])
watts = 120 # Replace with actual power consumption
# User credentials (VERY INSECURE - DO NOT USE IN PRODUCTION)
USERS = {
    "user1": "password123",
    "admin": "secureadmin"
}

# HTML content for the login page
LOGIN_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body style="font-family: sans-serif;display: flex;justify-content: center; align-items: center; min-height: 100vh; margin: 0;padding: 20px;">
    <div style=" background-color: #fff;padding: 40px;border-radius: 12px;box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);width: 100%;max-width: 400px;text-align: center;box-sizing: border-box;">
    <h1 style=" color: #2c3e50;margin-bottom: 30px;font-weight: 700;">Login</h1><br>
    <form method="post" style=" margin-bottom: 25px;text-align: left;">
        <label for="username" style="display: block;margin-bottom: 8px;color: #34495e;font-weight: 600;font-size: 14px;">Username:</label>
        <input type="text" id="username" name="username"style="width: 100%;padding: 12px 40px 12px 15px;border: 1px solid #e0e0e0;border-radius: 6px;box-sizing: border-box;font-size: 16px;transition: border-color 0.3s ease;outline: none;"><br><br>
        <label for="password" style="display: block;margin-bottom: 8px;color: #34495e;font-weight: 600;font-size: 14px;">Password:</label>
        <input type="password" id="password" name="password" style="width: 100%;padding: 12px 40px 12px 15px;border: 1px solid #e0e0e0;border-radius: 6px;box-sizing: border-box;font-size: 16px;transition: border-color 0.3s ease;outline: none;"><br><br>
        <input type="submit" value="Login" style="background-color: #1f1f1f;color: white;padding: 12px 25px;border: none;border-radius: 6px;cursor: pointer;font-size: 18px;width: 100%;transition: background-color 0.3s ease, transform 0.2s ease;font-weight: 600;">
        <p style="">{error_message}</p>
    </form>
    </div>
</body>
</html>
"""

# HTML content for the dashboard page
DASHBOARD_PAGE = """<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
</head>
<body>
<div style="display: flex;flex-direction: column;min-height: 100vh;">
        <nav style="background-color: #4CAF50;color: white;padding: 15px 20px;display: flex;justify-content: space-between;align-items: center;box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);">
            <div style=" font-size: 20px;font-weight: 600;">Dashboard</div>
            <div style="display: flex;align-items: center;">
                <a href="#" style="margin-right: 20px;cursor: pointer;font-size: 16px;color: white;text-decoration: none;">Settings</a>
                <div style=" position: relative;display: inline-block;">
                    <a href="/logout" style="color: white;font-size: 16px;cursor: pointer;display: flex;align-items: center;gap: 5px;">Logout</a>
                    </div>
            </div>
        </nav>
        <main style=" flex: 1;padding: 20px;text-align: center;">
    <h1style="font-size: 24px;color: #333;margin-bottom: 20px;">Welcome to the Dashboard!</h1>
    <div style=" background-color: #fff;padding: 30px;border-radius: 12px;box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);text-align: left;line-height: 1.7;">
    <p>You are now logged in.</p>
     <p>This is a sample dashboard layout.  You can customize this page to display
                    your desired content, such as charts, statistics, and other information.
                </p>
                <p>
                    Temperature: {temperature}°C
                </p>
                <p>
                    Date & Time: {date_time}
                </p>
                <p>
                    Total Watts: {watts}W
                </p>
   </main>
     </div>
    <script>
        const dropdownToggle = document.querySelector('.dropdown-toggle');
        const dropdown = document.querySelector('.dropdown');

        dropdownToggle.addEventListener('click', () => {
            dropdown.classList.toggle('active');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (event) => {
            if (!dropdown.contains(event.target) && !dropdown.querySelector('.dropdown-content').contains(event.target)) {
                dropdown.classList.remove('active');
            }
        });
    </script>
</body>
</html>
"""

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.connect(WIFI_SSID, WIFI_PASSWORD)
        while not wlan.isconnected():
            time.sleep(1)
    print('WiFi connected!')
    ip = wlan.ifconfig()[0]
    print(f'IP Address: {ip}')
    return ip

def parse_http_request(request):
    headers = {}
    method = None
    path = None
    body = {}
    lines = request.split('\r\n')
    if lines:
        first_line = lines[0].split()
        if len(first_line) == 3:
            method, path, _ = first_line

    for line in lines[1:]:
        if not line:
            break
        if ": " in line:
            key, value = line.split(": ", 1)
            headers[key.lower()] = value

    if method == "POST":
        if "\r\n\r\n" in request:
            body_str = request.split("\r\n\r\n", 1)[1]
            for param in body_str.split('&'):
                if '=' in param:
                    key, value = param.split('=', 1)
                    body[key] = value

    return method, path, headers, body

def handle_request(client):
    request = client.recv(1024).decode('utf-8')
    method, path, headers, body = parse_http_request(request)
    print(f"Method: {method}, Path: {path}, Headers: {headers}, Body: {body}")

    response = ""
    logged_in = False
    current_user = None
    if 'cookie' in headers:
        cookies = {}
        for cookie_pair in headers['cookie'].split('; '):
            if '=' in cookie_pair:
                key, value = cookie_pair.split('=', 1)
                cookies[key] = value
        if 'session' in cookies and cookies['session'] in sessions:
            logged_in = True
            current_user = sessions[cookies['session']]
            print(f"User {current_user} is logged in via session cookie.")

    if path == '/':
        if method == 'POST':
            username = body.get('username')
            password = body.get('password')
            if username in USERS and USERS[username] == password:
                session_id = str(time.ticks_ms()) + str(urandom.getrandbits(16)) # Slightly better session ID
                sessions[session_id] = username
                response = f"HTTP/1.1 303 See Other\r\nLocation: /dashboard\r\nSet-Cookie: session={session_id}\r\n\r\n"
            else:
                response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{LOGIN_PAGE.format(error_message='Invalid username or password')}"
        else:
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{LOGIN_PAGE.format(error_message='')}"
    elif path == '/dashboard':
        if logged_in:
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\n{DASHBOARD_PAGE}"
        else:
            response = "HTTP/1.1 303 See Other\r\nLocation: /\r\n\r\n"
    elif path == '/logout':
        if 'cookie' in headers:
            cookies = {}
            for cookie_pair in headers['cookie'].split('; '):
                if '=' in cookie_pair:
                    key, value = cookie_pair.split('=', 1)
                    cookies[key] = value
            if 'session' in cookies and cookies['session'] in sessions:
                del sessions[cookies['session']]
                print("User logged out.")
                response = "HTTP/1.1 303 See Other\r\nLocation: /\r\nSet-Cookie: session=; Max-Age=0\r\n\r\n" # Clear the cookie
            else:
                response = "HTTP/1.1 303 See Other\r\nLocation: /\r\n\r\n"
        else:
            response = "HTTP/1.1 303 See Other\r\nLocation: /\r\n\r\n"
    else:
        response = "HTTP/1.1 404 Not Found\r\nContent-Type: text/plain\r\n\r\nNot Found"

    client.sendall(response.encode('utf-8'))
    client.close()

if __name__ == "__main__":
    ip_address = connect_wifi()

    # Initialize session storage (very basic in-memory)
    sessions = {}

    addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

    s = socket.socket()
    s.bind(addr)
    s.listen(1)
    print('Listening on', addr)

    while True:
        cl, addr = s.accept()
        print('Client connected from', addr)
        try:
            handle_request(cl)
        except Exception as e:
            print(f"Error handling request: {e}")
        finally:
            cl.close()
