import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
import sqlite3
import random
import string
from lorem.text import TextLorem
from flask_socketio import SocketIO


app = Flask(__name__)
socketio = SocketIO(app)
DB_PATH = 'sql/app.db'
TIMEOUT_TIME = 60

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


#--------------------------------------------
@app.route('/')
def home():
    return render_template('index.html')
#--------------------------------------------
@app.route('/register', methods=['POST'])
def register():
    try:
        with sqlite3.connect(DB_PATH, timeout=TIMEOUT_TIME) as conn:
            c = conn.cursor()
            car_description = request.json["description"]
            car_plate = request.json["plate"]
            c.execute("INSERT INTO cars (plate, description) VALUES (?, ?)", (car_plate, car_description))
            conn.commit()
            new_car = {"id": c.lastrowid, "plate": car_plate, "description": car_description}
            socketio.emit('new_car', new_car)
            emit_car_count_update()
        return jsonify({"message": "Registered successfully"}), 201

    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        return jsonify({"error": error_message}), 500
    
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


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)