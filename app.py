import csv
from flask import Flask, render_template, request, jsonify
import time
import hashlib
import datetime
import psutil

app = Flask(__name__)
csv_path = 'performance_analysis/resource_usage_log.csv'

# Simulate a heavy task that takes some time to complete
def process_heavy_task(complexity):
    # Simulate a CPU-intensive task, like calculating a hash multiple times
    # time.sleep(complexity)  
    result = hashlib.sha256(str(complexity).encode()).hexdigest()
    for _ in range(complexity * 100000):
        result = hashlib.sha256(result.encode()).hexdigest()
    return result

def log_resource_usage():
    cpu_usage = psutil.cpu_percent(interval=1)  # Percentual de uso da CPU
    memory_usage = psutil.virtual_memory().percent  # Percentual de uso da memória
    timestamp = datetime.datetime.now()  # Timestamp atual

    # Escrever no arquivo CSV
    with open(csv_path, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([timestamp, cpu_usage, memory_usage])

def initialize_csv():
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "CPU_Usage(%)", "Memory_Usage(%)"])

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_request():
    data = request.get_json()
    
    # get the complexity from the request data
    complexity = data.get('complexity', 1)  # Default to 1 if not provided
    
    # Limit the complexity to a value between 1 and 10
    complexity = max(1, min(complexity, 10))
    
    # Process the heavy task
    result = process_heavy_task(complexity)

    # Log resource usage
    log_resource_usage()
    
    # Return the result as JSON
    return jsonify({
        "complexity": complexity,
        "result": result
    })

if __name__ == '__main__':
    initialize_csv()
    app.run(host='0.0.0.0', port=5000)