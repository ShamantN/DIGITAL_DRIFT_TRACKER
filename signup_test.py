import requests
import json

url = "http://127.0.0.1:8000/api/auth/signup"
payload = {
    "email": "testuser6@example.com",
    "password": "pass123",
    "confirm_password": "pass123"
}
headers = {
    "Content-Type": "application/json"
}

with open("signup_test_output.txt", "w") as f:
    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        f.write(f"Status Code: {response.status_code}\n")
        f.write(f"Response JSON: {response.json()}\n")
    except requests.exceptions.RequestException as e:
        f.write(f"An error occurred: {e}\n")