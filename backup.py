import random
import string
from flask import Flask, render_template, request, jsonify
import sqlite3
from lorem.text import TextLorem

DB_PATH = 'sql/app.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS cars
                 (id INTEGER PRIMARY KEY, plate TEXT, description TEXT)''')
    conn.commit()
    conn.close()
    print("Database initialized")

app = Flask(__name__)
# app.config['UPLOAD_FOLDER'] = 'static/uploads'

def gen_lorem(words: int = 256):
    lorem = TextLorem(wsep=' ', srange=(words,words))
    text = lorem.sentence()
    print("len(words):", len(text.split()))
    return ' '.join(text)

#generate a random car plate
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
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        car_description = gen_lorem(int(request.json['desc_size']))
        car_plate = gen_car_plate()
        c.execute("INSERT INTO cars (plate, description) VALUES (?, ?)", (car_plate, car_description))
        conn.commit()
        conn.close()
        return jsonify({"message": "Data registered"})
    except Exception as e:
        error_message = str(e)
        print(f"Error: {error_message}")
        return jsonify({"error": error_message}), 500

#--------------------------------------------
@app.route('/cars', methods=['GET'])
def get_cars():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM cars")
    cars = c.fetchall()
    conn.close()
    
    # Convert the list of tuples into a list of dictionaries
    cars_list = [{"id": car[0], "plate":car[1], "description": car[2]} for car in cars]
    
    response = jsonify(cars_list)
    return response


if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
