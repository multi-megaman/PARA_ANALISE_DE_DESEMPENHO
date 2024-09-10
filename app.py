import os
import psutil
import csv
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import sqlite3
import random
import string
from lorem.text import TextLorem
from flask_socketio import SocketIO
import threading
from concurrent.futures import ThreadPoolExecutor


app = Flask(__name__)
socketio = SocketIO(app)
DB_PATH = 'sql/app.db'
TIMEOUT_TIME = 10

# Load environment variables from .env file
load_dotenv()
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD')

# Function to initialize the database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            plate TEXT NOT NULL,
            description TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def gen_lorem(words: int = 256):
    lorem = TextLorem(wsep=' ', srange=(words, words))
    text = lorem.sentence()
    return text

def gen_car_plate():
    letters = ''.join(random.choices(string.ascii_uppercase, k=3))
    digits = ''.join(random.choices(string.digits, k=4))
    return f"{letters}-{digits}"

def get_car_count_from_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM cars")
    count = c.fetchone()[0]
    conn.close()
    return count

def emit_car_count_update():
    count = get_car_count_from_db()
    socketio.emit('car_count_update', {'total_cars': count})

executor = ThreadPoolExecutor(max_workers=5)
csv_file_path = 'performance_analysis/resource_usage.csv'
process = psutil.Process(os.getpid())

def write_resource_usage(cpu_percent, memory_mb):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(csv_file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([timestamp, cpu_percent, memory_mb])

def register_car(car_plate, car_description):
    try:
        # Monitor resources before registration
        cpu_percent = process.cpu_percent(interval=0.1)
        memory_mb = process.memory_info().rss / (1024 * 1024)  # Converter para MB
        
        write_resource_usage(cpu_percent, memory_mb)
        
        # Existing registration logic
        with sqlite3.connect(DB_PATH, timeout=TIMEOUT_TIME) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO cars (plate, description) VALUES (?, ?)", (car_plate, car_description))
            conn.commit()
            new_car = {"id": c.lastrowid, "plate": car_plate, "description": car_description}
            socketio.emit('new_car', new_car)
            emit_car_count_update()
        return {"message": "Registrado com sucesso"}
    except Exception as e:
        error_message = str(e)
        print(f"Erro: {error_message}")
        return {"error": error_message}

@app.route('/')
def home():
    return render_template('index.html')
#--------------------------------------------
@app.route('/register', methods=['POST'])
def register():
    car_description = request.json["description"]
    car_plate = request.json["plate"]
    future = executor.submit(register_car, car_plate, car_description)
    return jsonify({"message": "Registro iniciado"}), 202

#--------------------------------------------
@app.route('/cars', methods=['GET'])
def get_cars():
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 20))
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Debugging: Check if the table exists
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='cars'")
    table_exists = c.fetchone()
    if not table_exists:
        print("Table 'cars' does not exist.")
        conn.close()
        return jsonify([])

    # Debugging: Check the number of records in the table
    c.execute("SELECT COUNT(*) FROM cars")

    c.execute("SELECT plate, description FROM cars LIMIT ? OFFSET ?", (limit, offset))
    cars = c.fetchall()
    conn.close()

    return jsonify([{"plate": car[0], "description": car[1]} for car in cars])

@app.route('/cars/delete', methods=['POST'])
def delete_all_cars():
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({"error": "Password is required"}), 400

    if data['password'] != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        with sqlite3.connect(DB_PATH, timeout=TIMEOUT_TIME) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM cars")
            conn.commit()
            emit_car_count_update()
        return jsonify({"message": "All cars deleted successfully"}), 200

    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        return jsonify({"error": error_message}), 500
#--------------------------------------------
@app.route('/cars/count', methods=['GET'])
def get_car_count():
    count = get_car_count_from_db()
    return jsonify({"total_cars": count})

#--------------------------------------------
@app.route('/reset_resources', methods=['POST'])
def reset_resources():
    data = request.get_json()
    if not data or 'password' not in data:
        return jsonify({"error": "Password is required"}), 400

    if data['password'] != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401
    
    with open(csv_file_path, 'w', newline='') as csvfile:
        # Reset the CSV file
        csvfile.truncate(0)
        writer = csv.writer(csvfile)
        writer.writerow(['Timestamp', 'CPU (%)', 'Memória (MB)'])

    return jsonify({"message": "Resources reset successfully"}), 200

if __name__ == '__main__':
    init_db()
    
    # Create CSV if it doesn't exists
    if not os.path.exists(csv_file_path):
        with open(csv_file_path, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Timestamp', 'CPU (%)', 'Memória (MB)'])
    
    try:
        app.run(host='0.0.0.0', port=5000)
    finally:
        print("Encerrando o executor de threads...")
        executor.shutdown(wait=True)
        print("Executor de threads encerrado.")