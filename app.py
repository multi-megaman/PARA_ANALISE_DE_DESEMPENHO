from flask import Flask, render_template, request, jsonify
import sqlite3
import random
import string
from lorem.text import TextLorem

app = Flask(__name__)
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
        return jsonify({"message": "Data registered"})
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
    c.execute("SELECT plate, description FROM cars LIMIT ? OFFSET ?", (limit, offset))
    cars = c.fetchall()
    conn.close()
    return jsonify([{"plate": car[0], "description": car[1]} for car in cars])
#--------------------------------------------
@app.route('/cars/count', methods=['GET'])
def get_car_count():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM cars")
    count = c.fetchone()[0]
    conn.close()
    return jsonify({"total_cars": count})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)