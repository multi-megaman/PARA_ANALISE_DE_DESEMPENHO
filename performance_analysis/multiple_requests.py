import requests
import json
import random

requests_qnt = 50

# Example data to send in POST requests
cars_options = [
    {"plate": "ABC123", "description": "Blue Sedan"},
    {"plate": "XYZ789", "description": "Red Coupe"},
    {"plate": "JKL456", "description": "Green SUV"}
]

# The URL of the endpoint
url = "http://localhost:5000/register"


cars = []
for i in range(requests_qnt):
    car = random.choice(cars_options)
    cars.append(car)

# Loop through the cars list and make a POST request for each
for car in cars:
    response = requests.post(url, data=json.dumps(car), headers={"Content-Type": "application/json"})
    try:
        response_data = response.json()
        print(f"Status Code: {response.status_code}, Response: {response_data}")
    except json.decoder.JSONDecodeError:
        print(f"Status Code: {response.status_code}, Response could not be decoded as JSON.")

print("Finished making requests to /register endpoint.")