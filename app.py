from flask import Flask, render_template, request, jsonify
import sqlite3
import random
import string
from lorem.text import TextLorem
from flask_socketio import SocketIO


app = Flask(__name__)
socketio = SocketIO(app)
DB_PATH = 'sql/app.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cars
                 (id INTEGER PRIMARY KEY, plate TEXT, description TEXT)''')
    conn.commit()
    conn.close()
    print("Database initialized")

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
        with sqlite3.connect(DB_PATH, timeout=10) as conn:
            c = conn.cursor()
            car_description = gen_lorem(int(request.json['desc_size']))
            car_plate = gen_car_plate()
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
    total_records = c.fetchone()[0]
    print(f"Total records in 'cars' table: {total_records}")

    c.execute("SELECT plate, description FROM cars LIMIT ? OFFSET ?", (limit, offset))
    cars = c.fetchall()
    conn.close()
    
    # Debugging: Log the fetched records
    print(f"Fetched records: {cars}")

    return jsonify([{"plate": car[0], "description": car[1]} for car in cars])
#--------------------------------------------
@app.route('/cars/count', methods=['GET'])
def get_car_count():
    count = get_car_count_from_db()
    return jsonify({"total_cars": count})


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)