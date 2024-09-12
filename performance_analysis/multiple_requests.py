import threading
import requests
import json
import random
import string
from lorem.text import TextLorem
import time
import csv

# Endpoint URL
url = "http://192.168.1.107:5000/register"

# Function to generate a random license plate
def generate_random_plate():
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    numbers = ''.join(random.choices(string.digits, k=4))
    return f"{letters}-{numbers}"

# Function to make a single request
def make_single_request(description, plate, csv_writer):
    data = {"plate": plate, "description": description}
    start_time = time.time()
    response = requests.post(url, json=data)
    end_time = time.time()
    
    response_time = end_time - start_time
    latency = response.elapsed.total_seconds()
    error = 0 if response.status_code == 200 else 1
    
    csv_writer.writerow([response_time, latency, error])
    
    try:
        response_data = response.json()
        return 1
    except json.decoder.JSONDecodeError:
        return 0

# Main function to make requests in threads
def make_requests(num_words, num_requests, csv_path):
    threads = []
    with open(csv_path, 'a', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        
        for _ in range(num_requests):
            lorem = TextLorem(wsep=' ', srange=(num_words, num_words))
            description = lorem.sentence()
            plate = generate_random_plate()
            thread = threading.Thread(target=make_single_request, args=(description, plate, csv_writer))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

if __name__ == "__main__":
    csv_path = 'performance_analysis/request_results.csv'
    num_words = int(input("Enter the number of words for each description: "))
    num_requests = int(input("Enter the number of requests to be sent: "))
    num_repeat = int(input("Enter the number of times the requests will be repeated: "))

    with open(csv_path, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Tempo de resposta", "Latencia", "Error (0 = OK, 1 = Error)"])
        
    print(f"Starting {num_requests} requests to the /register endpoint.")
    for _ in range(num_repeat):
        make_requests(num_words, num_requests, csv_path)
        time.sleep(10)
    print("Finished sending requests to the /register endpoint.")